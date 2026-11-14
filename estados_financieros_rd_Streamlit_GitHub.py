"""
==============================================================================
 DASHBOARD FINANCIERO MULTIDIVISA  ·  Streamlit
 Autor original: Ing. Juancito Peña
==============================================================================

PROPÓSITO
---------
Dashboard ejecutivo que lee los estados financieros de una empresa
(Balance General + Estado de Resultados) desde un libro Excel y los convierte
en tiempo real a otras divisas usando tipos de cambio de mercado obtenidos de
una API pública. Todo el libro está expresado en DOP (peso dominicano).

CÓMO EJECUTARLO
---------------
    pip install streamlit pandas requests plotly openpyxl
    streamlit run dashboard_multidivisa_documentado.py

    (openpyxl es necesario para leer el .xlsx y para generar la descarga.)

MODELO DE EJECUCIÓN DE STREAMLIT (LEER ANTES DE MODIFICAR)
----------------------------------------------------------
Streamlit vuelve a ejecutar ESTE ARCHIVO COMPLETO, de arriba hacia abajo,
cada vez que el usuario interactúa con un widget (selectbox, radio, botón...).
Consecuencias prácticas:
  1. El ORDEN del código importa: una variable debe definirse antes de usarse.
     Por ejemplo, `factor` y `codigo_sel` nacen en el sidebar (sección 4) y se
     consumen en las secciones 5 a 9.
  2. `st.set_page_config()` debe ser el primer comando de Streamlit.
  3. Las funciones con `@st.cache_data` guardan su resultado para no repetir
     descargas pesadas en cada interacción (ver sección 3).
  4. Las variables definidas dentro de un `with tabX:` siguen existiendo
     después (no hay ámbito nuevo). La pestaña 2 depende de `df_tabla_er`,
     creado en la pestaña 1 (ver nota en la sección 9).

FLUJO GENERAL DE DATOS
----------------------
    API de divisas ──► obtener_todas_las_tasas() ──► resolver_tasa() ──► factor
                                                                           │
    Excel (GitHub / subido / local) ──► procesar_excel() ──► DataFrames ───┤
                                                                           ▼
                           columnas *_DOP × factor ──► columnas en divisa elegida
                                                                           │
                                  filtros (mes, línea) ──► KPIs, gráficos, tablas

ESTRUCTURA DEL ARCHIVO
----------------------
    1. Configuración de página y estilos CSS
    2. Constantes y catálogo de divisas
    3. Funciones de extracción y procesamiento
    4. Sidebar: panel de control (divisa y fuente del Excel)
    5. Carga de datos y conversión de divisa
    6. Encabezado y filtros
    7. Totales y tarjetas KPI
    8. Gráficos (6 visualizaciones Plotly)
    9. Tablas, descarga a Excel y monitor de divisas

CONTRATO DE DATOS DEL EXCEL (si cambias el Excel, respeta esto)
----------------------------------------------------------------
Hoja "Balance_General" (encabezados en la fila 4, es decir header=3):
    Codigo        -> obligatorio; las filas sin código se descartan (dropna)
    Categoria     -> "Activos" | "Pasivos" | "Capital" (texto exacto)
    Subcategoria, Cuenta
    Monto_DOP     -> monto en pesos dominicanos
    Fecha_Corte   -> OPCIONAL; si existe se muestra como fecha de corte

Hoja "Estado_Resultados" (encabezados en la fila 4, header=3):
    Mes, Linea_Negocio
    Ingresos_DOP, Costos_DOP, Gastos_Operativos_DOP
    (la fila con Mes == "TOTAL" se descarta para no duplicar sumas)
    Las columnas de margen y utilidad se RECALCULAN en Python; no se leen
    del Excel (ver procesar_excel).

CONVENCIÓN DE NOMBRES
---------------------
    *_DOP         -> valor original en pesos dominicanos (nunca se modifica)
    Monto_Mostrar -> Balance convertido a la divisa elegida
    Ingresos, Costos, Margen_Bruto, Gastos_Operativos, Utilidad_Operativa
                  -> Estado de Resultados convertido a la divisa elegida

APIs EXTERNAS
-------------
    - Divisas: fawazahmed0/currency-api (gratuita, sin API key, tasas de
      mercado medio; NO son las tasas de compra/venta del Banco Central).
      Devuelve {"date": "...", "dop": {"usd": 0.0164, "eur": 0.0149, ...}}
      donde cada valor es "unidades de esa moneda por 1 DOP".
    - Excel: archivo en crudo de GitHub (raw.githubusercontent.com).

GUÍA RÁPIDA DE MODIFICACIONES
-----------------------------
    Agregar una divisa    -> añadir una entrada a DICCIONARIO_DIVISAS (sección 2)
                             con el código ISO (la API debe traer ese código).
    Agregar un KPI        -> calcular el total en la sección 7 y llamar
                             render_kpi() (ajustar el número de columnas).
    Agregar un gráfico    -> crear un bloque en la sección 8 siguiendo el patrón
                             de los existentes (agrupar -> figura -> st.plotly_chart).
    Agregar una columna   -> leerla/calcularla en procesar_excel(), convertirla
                             en la sección 5 y mostrarla donde corresponda.
    Cambiar la fuente     -> URL_EXCEL_GITHUB (sección 2).
    Cambiar la API        -> URLS_API_DIVISAS y, si el formato JSON cambia,
                             _consultar_api_tasas() y resolver_tasa().

DIAGNÓSTICO DE PROBLEMAS FRECUENTES
-----------------------------------
    "Error procesando el archivo Excel"
        Cambió el nombre de una hoja o columna (ver contrato de datos).
    La divisa vuelve sola a DOP y sale un error rojo
        La API no respondió o no trae esa moneda (se muestra el motivo).
    Los datos de GitHub no se actualizan
        Caché de 60 s; usar el botón "Refrescar datos desde GitHub".
    ModuleNotFoundError: openpyxl
        pip install openpyxl
    No aparece el archivo local de respaldo
        La ruta "estados_financieros_rd.xlsx" es relativa al directorio desde
        donde se lanza `streamlit run`.
==============================================================================
"""

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import io
import time

# ==============================================================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS PERSONALIZADOS (BENTO CARDS + BORDES)
# ==============================================================================
# Debe ser la PRIMERA llamada a Streamlit del script.
# layout="wide" aprovecha todo el ancho; el sidebar inicia desplegado.
st.set_page_config(
    page_title="Dashboard Financiero Multidivisa | DOP, USD, EUR & Más",
    page_icon="💱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS inyectado una sola vez. Clases disponibles y dónde se usan:
#   .main            -> fondo general de la página
#   .kpi-card        -> tarjeta de KPI (usada por render_kpi); el color del
#                       borde izquierdo se sobrescribe inline por cada KPI
#   .kpi-title/.kpi-value/.kpi-sub -> título, cifra principal y subtítulo
#   .header-banner   -> banner azul superior (sección 6)
#   .currency-pill   -> etiqueta con la divisa activa
#   .status-live     -> insignia verde "EN VIVO"
# `unsafe_allow_html=True` es necesario para que Streamlit acepte <style>/HTML.
st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .kpi-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 6px solid #1e3a8a;
        border-radius: 12px;
        padding: 16px 18px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 12px;
        transition: transform 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    .kpi-title {
        font-size: 0.80rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 5px;
    }
    .kpi-value {
        font-size: 1.45rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 4px;
    }
    .kpi-sub {
        font-size: 0.78rem;
        font-weight: 600;
        color: #475569;
    }
    .header-banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        padding: 22px 28px;
        border-radius: 14px;
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.2);
    }
    .header-banner h1 { margin: 0; font-size: 1.85rem; font-weight: 800; }
    .header-banner p { margin: 6px 0 0 0; font-size: 0.95rem; color: #dbeafe; }
    .currency-pill {
        display: inline-block;
        background-color: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 700;
    }
    .status-live {
        display: inline-block;
        background-color: #dcfce7;
        color: #166534;
        border: 1px solid #86efac;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 700;
        margin-left: 6px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. CONSTANTES Y CATÁLOGO DE DIVISAS
# ==============================================================================
# Excel de origen en GitHub (URL "raw", es decir, el archivo en crudo).
URL_EXCEL_GITHUB = "https://raw.githubusercontent.com/JUANCITOPENA/APIs-Python-Casos-Reales-Excel-Streamlit/main/estados_financieros_rd.xlsx"

# Endpoints de la API de divisas, en orden de prioridad: si el primero falla
# se prueba el segundo (espejo en otro CDN). Ambos devuelven el mismo JSON
# con la moneda base DOP. Se usa "@latest" para recibir siempre la tasa vigente.
URLS_API_DIVISAS = [
    "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/dop.json",
    "https://latest.currency-api.pages.dev/v1/currencies/dop.json",
]

# Catálogo de divisas que aparecen en el selector y en el monitor.
# IMPORTANTE: aquí NO hay tasas de cambio; solo metadatos de presentación.
# Las tasas SIEMPRE vienen de la API (jamás valores fijos o inventados).
# Para agregar una divisa, la clave debe ser su código ISO de 3 letras y debe
# existir en la respuesta de la API (en minúsculas, ej. "usd").
#   nombre  -> texto del selector y de los encabezados
#   simbolo -> prefijo de los montos (ej. "US$ 1,000.00")
#   icono   -> emoji de bandera
DICCIONARIO_DIVISAS = {
    "DOP": {"nombre": "Peso Dominicano (Moneda Base)", "simbolo": "RD$", "icono": "🇩🇴"},
    "USD": {"nombre": "Dólar Estadounidense", "simbolo": "US$", "icono": "🇺🇸"},
    "EUR": {"nombre": "Euro", "simbolo": "€", "icono": "🇪🇺"},
    "GBP": {"nombre": "Libra Esterlina", "simbolo": "£", "icono": "🇬🇧"},
    "CHF": {"nombre": "Franco Suizo", "simbolo": "CHF ", "icono": "🇨🇭"},
    "CAD": {"nombre": "Dólar Canadiense", "simbolo": "CA$", "icono": "🇨🇦"},
    "AUD": {"nombre": "Dólar Australiano", "simbolo": "A$", "icono": "🇦🇺"},
    "SGD": {"nombre": "Dólar de Singapur", "simbolo": "S$", "icono": "🇸🇬"},
    "CNY": {"nombre": "Yuan Chino", "simbolo": "CN¥", "icono": "🇨🇳"},
    "MXN": {"nombre": "Peso Mexicano", "simbolo": "MX$", "icono": "🇲🇽"},
    "JPY": {"nombre": "Yen Japonés", "simbolo": "¥", "icono": "🇯🇵"},
    "BRL": {"nombre": "Real Brasileño", "simbolo": "R$", "icono": "🇧🇷"},
    "COP": {"nombre": "Peso Colombiano", "simbolo": "COL$", "icono": "🇨🇴"},
}

# ==============================================================================
# 3. FUNCIONES DE EXTRACCIÓN Y PROCESAMIENTO
# ==============================================================================
@st.cache_data(ttl=1800, show_spinner=False)
def _consultar_api_tasas():
    """
    Consulta la API de divisas y devuelve (tasas_dop, fecha_api).

    - Prueba cada URL de URLS_API_DIVISAS en orden hasta obtener una respuesta
      válida.
    - Valida el esquema: el JSON debe traer "dop" como diccionario y un "usd"
      numérico mayor que 0 (si no, se considera respuesta corrupta).
    - Si ninguna URL responde bien, lanza ConnectionError.

    Caché: 1800 s (30 min). Truco clave: al fallar se LANZA una excepción en
    lugar de devolver un valor vacío, porque Streamlit no guarda en caché las
    excepciones. Así un fallo puntual se reintenta en la siguiente interacción
    en vez de quedar "pegado" 30 minutos.

    Para forzar refresco manual existe el botón del sidebar, que llama a
    st.cache_data.clear().
    """
    for url in URLS_API_DIVISAS:
        try:
            res = requests.get(url, timeout=8)
            res.raise_for_status()  # convierte HTTP 4xx/5xx en excepción
            datos = res.json()
            tasas_dop = datos.get("dop")
            # Validación de esquema (ver docstring)
            if (
                isinstance(tasas_dop, dict)
                and isinstance(tasas_dop.get("usd"), (int, float))
                and tasas_dop["usd"] > 0
            ):
                return tasas_dop, datos.get("date", "Sin fecha")
        except (requests.exceptions.RequestException, ValueError):
            # RequestException: red/timeout/HTTP. ValueError: JSON inválido.
            continue  # probar la siguiente URL
    raise ConnectionError("La API de divisas no respondió con datos válidos.")

def obtener_todas_las_tasas():
    """
    Envoltorio "seguro" de _consultar_api_tasas() para el resto de la app.

    Devuelve siempre una tupla (tasas_dop, fecha, api_ok):
      - api_ok=True  -> tasas_dop es el diccionario completo de la API.
      - api_ok=False -> tasas_dop={} y la app mostrará avisos (nunca inventa
                        valores).
    No está cacheada a propósito: el caché vive en la función interna.
    """
    try:
        tasas_dop, fecha = _consultar_api_tasas()
        return tasas_dop, fecha, True
    except ConnectionError:
        return {}, "Sin conexión con la API", False

@st.cache_data(ttl=60)
def descargar_excel_github(url):
    """
    Descarga el Excel desde GitHub y devuelve (buffer, etiqueta, exito).

    - buffer: io.BytesIO con el archivo (o None si falló).
    - etiqueta: texto que se muestra como "Fuente" en la interfaz.
    - exito: True/False.

    Caché de 60 s. Para evitar que CDNs intermedios sirvan una versión vieja se
    usan DOS defensas: headers anti-caché y un parámetro ?v=<minuto> en la URL.
    Si la primera petición falla, se reintenta con la URL limpia.
    El filtro `len(content) > 1000` descarta respuestas vacías o páginas de
    error diminutas que devuelven HTTP 200.
    """
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    }
    # time.time() // 60 cambia cada minuto -> URL distinta -> evita caché de CDN
    url_con_ts = f"{url}?v={int(time.time() // 60)}"
    try:
        res = requests.get(url_con_ts, headers=headers, timeout=12)
        if res.status_code == 200 and len(res.content) > 1000:
            return io.BytesIO(res.content), "🌐 Repositorio GitHub (En Vivo)", True
    except requests.exceptions.RequestException:
        pass

    # Segundo intento con la URL tal cual
    try:
        res_clean = requests.get(url, timeout=10)
        if res_clean.status_code == 200 and len(res_clean.content) > 1000:
            return io.BytesIO(res_clean.content), "🌐 Repositorio GitHub (En Vivo)", True
    except requests.exceptions.RequestException:
        pass

    return None, "Error de Conexión GitHub", False

def procesar_excel(ruta_o_buffer):
    """
    Lee las dos hojas del libro y devuelve (df_balance, df_resultados).

    `ruta_o_buffer` puede ser una ruta de archivo, un BytesIO (GitHub) o el
    objeto del file_uploader; pandas acepta los tres.

    header=3 significa que los encabezados están en la fila 4 del Excel (las
    3 primeras filas son título/subtítulo). Si cambia el diseño del Excel,
    ajustar este número.

    Los márgenes y utilidades se RECALCULAN aquí en lugar de leerse del Excel,
    para evitar celdas vacías o fórmulas sin evaluar. Todas las columnas
    resultantes siguen en DOP (sufijo _DOP); la conversión ocurre en la
    sección 5.
    """
    df_bg = pd.read_excel(ruta_o_buffer, sheet_name="Balance_General", header=3).dropna(subset=["Codigo"])
    df_er = pd.read_excel(ruta_o_buffer, sheet_name="Estado_Resultados", header=3)
    # Se excluye la fila "TOTAL" del Excel para no duplicar las sumas
    df_er = df_er[df_er["Mes"] != "TOTAL"].copy()

    # Recálculo completo en memoria (incluyendo Utilidad Operativa)
    #   Margen Bruto       = Ingresos - Costos
    #   Utilidad Operativa = Margen Bruto - Gastos Operativos
    #   % Margen           = Margen / Ingresos * 100
    # Nota: si Ingresos_DOP es 0 el porcentaje resulta inf/NaN.
    df_er["Margen_Bruto_DOP"] = df_er["Ingresos_DOP"] - df_er["Costos_DOP"]
    df_er["Utilidad_Operativa_DOP"] = df_er["Margen_Bruto_DOP"] - df_er["Gastos_Operativos_DOP"]
    df_er["Porcentaje_Margen"] = (df_er["Margen_Bruto_DOP"] / df_er["Ingresos_DOP"]) * 100
    df_er["Porcentaje_Operativo"] = (df_er["Utilidad_Operativa_DOP"] / df_er["Ingresos_DOP"]) * 100
    return df_bg, df_er

def resolver_tasa(cod, tasas):
    """
    Traduce un código de divisa en su tasa usando SOLO datos reales de la API.

    Devuelve (factor, valor_uno_en_rd, disponible):
      - factor          : unidades de la divisa por 1 DOP. Es el número por el
                          que se MULTIPLICA un monto en DOP para convertirlo.
      - valor_uno_en_rd : cuántos RD$ vale 1 unidad de la divisa (= 1/factor).
      - disponible      : True si hay dato real.

    Ejemplo: si la API dice usd=0.0164, 1 USD = RD$ 60.98 y un monto de
    RD$ 1,000 equivale a US$ 16.40.

    Si la API no trae esa moneda devuelve (None, None, False); quien llama debe
    manejarlo (el sidebar vuelve a DOP; el monitor muestra "Sin dato").
    DOP es la moneda base: factor 1, sin consultar la API.
    """
    if cod == "DOP":
        return 1.0, 1.0, True
    valor_api = tasas.get(cod.lower())  # la API usa claves en minúsculas
    if isinstance(valor_api, (int, float)) and valor_api > 0:
        return valor_api, 1 / valor_api, True
    return None, None, False

def fmt_tasa(valor):
    """Formatea una tasa: 2 decimales si es >= 1 (USD) y 4 si es menor (JPY)."""
    return f"{valor:,.2f}" if valor >= 1 else f"{valor:,.4f}"

def generar_excel_descarga(df_er_export, df_bg_export):
    """
    Genera en memoria un .xlsx con dos hojas (Estado_Resultados y
    Balance_General) y devuelve sus bytes, listos para st.download_button.
    Requiere la librería openpyxl. Exporta los datos tal como se ven en las
    tablas de pantalla (ya convertidos a la divisa elegida y con filtros).
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_er_export.to_excel(writer, sheet_name="Estado_Resultados", index=False)
        df_bg_export.to_excel(writer, sheet_name="Balance_General", index=False)
    return output.getvalue()

# ==============================================================================
# 4. SIDEBAR: PANEL DE CONTROL
# ==============================================================================
# Se consultan las tasas UNA vez por ejecución (el caché evita ir a la red
# cada vez). Estas tres variables se reutilizan en el sidebar y en la pestaña 3.
tasas_api, fecha_api, api_ok = obtener_todas_las_tasas()

with st.sidebar:
    st.markdown("## ⚙️ Panel de Control")

    # ---- 4.1 Selector de divisa ------------------------------------------
    st.markdown("### 💱 Divisa de Conversión")
    st.caption("Selecciona cualquier tipo de cambio real para convertir los estados financieros:")

    # Opciones con formato "🇺🇸 USD - Dólar Estadounidense"
    opciones_divisas = [
        f"{info['icono']} {codigo} - {info['nombre']}"
        for codigo, info in DICCIONARIO_DIVISAS.items()
    ]

    seleccion_divisa = st.selectbox(
        "Convertir datos contables a:",
        options=opciones_divisas,
        index=0  # DOP por defecto
    )

    # El código ISO es la 2ª palabra del texto: "🇺🇸 USD - ..." -> "USD".
    # (Depende del formato de opciones_divisas: si lo cambias, ajusta esto.)
    codigo_sel = seleccion_divisa.split(" ")[1]
    factor, valor_uno_en_rd, tasa_en_vivo = resolver_tasa(codigo_sel, tasas_api)

    # Si no hay tasa real para la divisa elegida, se informa y se vuelve a DOP.
    # Nunca se usa un valor estimado.
    if factor is None:
        if not api_ok:
            st.error("🔴 La API de divisas no respondió. Se muestran los datos en DOP.")
        else:
            st.error(f"🔴 La API no trae tasa para {codigo_sel}. Se muestran los datos en DOP.")
        codigo_sel = "DOP"
        factor, valor_uno_en_rd, tasa_en_vivo = 1.0, 1.0, True

    # Variables que usa TODO el resto de la app:
    #   codigo_sel  -> divisa activa      simbolo -> prefijo de montos
    #   factor      -> multiplicador      info_divisa -> metadatos de la divisa
    info_divisa = DICCIONARIO_DIVISAS[codigo_sel]
    simbolo = info_divisa["simbolo"]

    tasa_cotizacion_texto = (
        "Moneda Base RD$ (Sin conversión)"
        if codigo_sel == "DOP"
        else f"1 {codigo_sel} = RD$ {fmt_tasa(valor_uno_en_rd)}"
    )

    st.info(f"**Cotización Activa:**\n\n`{tasa_cotizacion_texto}`\n\n*Fecha API: {fecha_api}*")
    if codigo_sel != "DOP":
        st.success("🟢 Tasa de mercado en vivo desde la API.")

    st.divider()

    # ---- 4.2 Fuente del libro Excel --------------------------------------
    # Tres orígenes posibles. Al final de este bloque `buffer_excel` contiene
    # lo que leerá procesar_excel() y `etiqueta_fuente` el texto informativo.
    st.markdown("### 📥 Fuente del Libro Excel")
    opcion_origen = st.radio(
        "Seleccione el origen del archivo:",
        options=[
            "🌐 GitHub Live (En Tiempo Real)",
            "📂 Subir archivo Excel (.xlsx)",
            "💻 Archivo Local de Respaldo"
        ],
        index=0
    )

    buffer_excel = None
    etiqueta_fuente = ""

    # NOTA: las cadenas de las opciones del radio se comparan literalmente
    # abajo. Si cambias un texto en `options`, cámbialo también en el if/elif.
    if opcion_origen == "🌐 GitHub Live (En Tiempo Real)":
        buffer_excel, etiqueta_fuente, exito = descargar_excel_github(URL_EXCEL_GITHUB)
        if exito:
            st.success("✅ Conectado a GitHub (Sincronizado).")
            if st.button("🔄 Refrescar datos desde GitHub"):
                st.cache_data.clear()  # borra TODOS los cachés (Excel y tasas)
                st.rerun()
        else:
            # Sin red: se cae al archivo local para que la app no se rompa
            st.warning("⚠️ Sin conexión con GitHub. Usando archivo local de respaldo.")
            buffer_excel = "estados_financieros_rd.xlsx"
            etiqueta_fuente = "💻 Archivo Local (Fallback de Emergencia)"

    elif opcion_origen == "📂 Subir archivo Excel (.xlsx)":
        archivo_subido = st.file_uploader("Arrastra tu archivo Excel contable:", type=["xlsx"])
        if archivo_subido is not None:
            buffer_excel = archivo_subido
            etiqueta_fuente = f"📂 Subido por usuario: {archivo_subido.name}"
            st.success("✅ Archivo cargado correctamente.")
        else:
            # Mientras el usuario no suba nada se muestra el archivo local
            buffer_excel = "estados_financieros_rd.xlsx"
            etiqueta_fuente = "💻 Archivo Local (En espera de archivo)"
            st.info("ℹ️ Mostrando datos locales de respaldo.")
    else:
        buffer_excel = "estados_financieros_rd.xlsx"
        etiqueta_fuente = "💻 Archivo Local del Servidor"

    # Refresco manual de tasas (también limpia el caché del Excel)
    if st.button("🔄 Actualizar Tasas de Divisas (API)"):
        st.cache_data.clear()
        st.rerun()

# ==============================================================================
# 5. CARGA DE DATOS Y CONVERSIÓN DINÁMICA
# ==============================================================================
# Si el Excel no se puede leer (hoja/columna ausente, archivo corrupto) se
# muestra el error y se detiene la ejecución con st.stop() para no seguir
# con datos inexistentes.
try:
    df_balance, df_resultados = procesar_excel(buffer_excel)
except Exception as e:
    st.error(f"Error procesando el archivo Excel: {e}")
    st.stop()

# CONVERSIÓN: monto_en_divisa = monto_DOP * factor, redondeado a 2 decimales.
# Las columnas *_DOP originales se conservan intactas. Para añadir una métrica
# convertida nueva, replica este patrón.
df_balance["Monto_Mostrar"] = (df_balance["Monto_DOP"] * factor).round(2)
df_resultados["Ingresos"] = (df_resultados["Ingresos_DOP"] * factor).round(2)
df_resultados["Costos"] = (df_resultados["Costos_DOP"] * factor).round(2)
df_resultados["Margen_Bruto"] = (df_resultados["Margen_Bruto_DOP"] * factor).round(2)
df_resultados["Gastos_Operativos"] = (df_resultados["Gastos_Operativos_DOP"] * factor).round(2)
df_resultados["Utilidad_Operativa"] = (df_resultados["Utilidad_Operativa_DOP"] * factor).round(2)

# Fecha de corte leída dinámicamente del Excel: se toma el primer valor de la
# columna opcional "Fecha_Corte" (primeros 10 caracteres = AAAA-MM-DD). Si la
# columna no existe o está vacía se muestra un texto genérico.
fecha_corte_excel = (
    str(df_balance["Fecha_Corte"].iloc[0])[:10]
    if "Fecha_Corte" in df_balance.columns and not df_balance["Fecha_Corte"].dropna().empty
    else "Fecha Oficial Registrada"
)

# ==============================================================================
# 6. HEADER Y FILTROS INTERACTIVOS
# ==============================================================================
# Banner superior (HTML estático con la clase .header-banner)
st.markdown("""
<div class="header-banner">
    <h1>🏛️ Dashboard Financiero Multidivisa</h1>
    <p>Consumo de API pública de divisas de mercado + Integración Continua con Excel desde GitHub</p>
</div>
""", unsafe_allow_html=True)

# Tres columnas: [info de divisa (doble ancho) | filtro de mes | filtro de línea]
c_info1, c_info2, c_info3 = st.columns([2, 1, 1])

with c_info1:
    # La insignia "EN VIVO" solo aparece si hay conversión (no en DOP)
    badge_estado = "" if codigo_sel == "DOP" else "<span class='status-live'>🟢 EN VIVO</span>"
    st.markdown(
        f"**Divisa de Visualización:** <span class='currency-pill'>{info_divisa['icono']} {codigo_sel} ({simbolo})</span>{badge_estado}",
        unsafe_allow_html=True
    )
    st.caption(f"Tasa de Conversión: **{tasa_cotizacion_texto}** | Fuente: `{etiqueta_fuente}`")

with c_info2:
    # sorted() ordena alfabéticamente los meses (ver sección de mejoras)
    lista_meses = ["Todos"] + sorted(list(df_resultados["Mes"].unique()))
    mes_sel = st.selectbox("📅 Filtrar por Mes:", lista_meses, index=0)

with c_info3:
    lista_lineas = ["Todas"] + sorted(list(df_resultados["Linea_Negocio"].unique()))
    linea_sel = st.selectbox("🏢 Línea de Negocio:", lista_lineas, index=0)

# Los filtros afectan SOLO al Estado de Resultados (df_er_filt).
# El Balance General es una "foto" a una fecha de corte y NO se filtra.
df_er_filt = df_resultados.copy()
if mes_sel != "Todos":
    df_er_filt = df_er_filt[df_er_filt["Mes"] == mes_sel]
if linea_sel != "Todas":
    df_er_filt = df_er_filt[df_er_filt["Linea_Negocio"] == linea_sel]

# ==============================================================================
# 7. CÁLCULO DE TOTALES Y TARJETAS BENTO KPI
# ==============================================================================
# --- Balance General (sin filtros): totales por categoría ---
tot_activos = df_balance[df_balance["Categoria"] == "Activos"]["Monto_Mostrar"].sum()
tot_pasivos = df_balance[df_balance["Categoria"] == "Pasivos"]["Monto_Mostrar"].sum()
tot_capital = df_balance[df_balance["Categoria"] == "Capital"]["Monto_Mostrar"].sum()
# Control contable: Activos = Pasivos + Capital. Esta diferencia alimenta el
# aviso de "ecuación cuadrada" más abajo (tolerancia: menos de 1 unidad de la
# divisa activa).
diferencia_cuadre = abs(tot_activos - (tot_pasivos + tot_capital))

# --- Estado de Resultados (con filtros de mes y línea aplicados) ---
tot_ingresos = df_er_filt["Ingresos"].sum()
tot_costos = df_er_filt["Costos"].sum()
tot_margen = df_er_filt["Margen_Bruto"].sum()
tot_gastos = df_er_filt["Gastos_Operativos"].sum()
tot_utilidad_op = df_er_filt["Utilidad_Operativa"].sum()

# Porcentajes protegidos contra división por cero (si el denominador es 0 -> 0)
pct_margen_global = (tot_margen / tot_ingresos * 100) if tot_ingresos > 0 else 0
pct_operativo_global = (tot_utilidad_op / tot_ingresos * 100) if tot_ingresos > 0 else 0
pct_pasivos = (tot_pasivos / tot_activos * 100) if tot_activos > 0 else 0
pct_capital = (tot_capital / tot_activos * 100) if tot_activos > 0 else 0

def render_kpi(col, titulo, valor, subtitulo, icono="📌", color_borde="#1e3a8a"):
    """
    Dibuja una tarjeta KPI dentro de la columna `col`.

    Parámetros:
      col          : columna de st.columns() donde se pinta la tarjeta
      titulo       : etiqueta pequeña en mayúsculas
      valor        : cifra principal ya formateada (texto)
      subtitulo    : línea secundaria (ej. porcentaje o nota)
      icono        : emoji junto al título
      color_borde  : color hex del acento lateral izquierdo
    Para agregar un KPI nuevo basta llamar a esta función en otra columna.
    """
    col.markdown(f"""
    <div class="kpi-card" style="border-left-color: {color_borde};">
        <div class="kpi-title">{icono} {titulo}</div>
        <div class="kpi-value">{valor}</div>
        <div class="kpi-sub">{subtitulo}</div>
    </div>
    """, unsafe_allow_html=True)

# Encabezado de la sección Balance, con verificación de la ecuación contable
st.markdown(f"""
### 🏛️ Posición Financiera (Balance General en {codigo_sel})
<div style='background-color: #f1f5f9; border-left: 4px solid #2563eb; padding: 8px 14px; border-radius: 6px; color: #1e293b; font-size: 0.98rem; font-weight: 600; margin-top: -4px; margin-bottom: 14px;'>
    📌 <em>Foto patrimonial acumulada a fecha de corte ({fecha_corte_excel}) · Ecuación contable: {"✅ Cuadrada (A = P + C)" if diferencia_cuadre < 1 else f"⚠️ Diferencia de {simbolo} {diferencia_cuadre:,.2f}"}</em>
</div>
""", unsafe_allow_html=True)

# Fila de KPIs del Balance (3 columnas)
k1, k2, k3 = st.columns(3)
render_kpi(k1, "Total Activos", f"{simbolo} {tot_activos:,.2f}", f"Recursos totales ({codigo_sel})", "🏛️", "#2563eb")
render_kpi(k2, "Total Pasivos", f"{simbolo} {tot_pasivos:,.2f}", f"Endeudamiento: {pct_pasivos:.1f}% de activos", "💳", "#dc2626")
render_kpi(k3, "Total Capital", f"{simbolo} {tot_capital:,.2f}", f"Patrimonio neto: {pct_capital:.1f}% de activos", "🛡️", "#059669")

# Encabezado de la sección Rentabilidad; muestra los filtros activos
st.markdown(f"""
### 📈 Indicadores de Rentabilidad y Operación (Estado de Resultados en {codigo_sel})
<div style='background-color: #f1f5f9; border-left: 4px solid #059669; padding: 8px 14px; border-radius: 6px; color: #1e293b; font-size: 0.98rem; font-weight: 600; margin-top: -4px; margin-bottom: 14px;'>
    📊 <em>Flujo operativo dinámico · Mes: <strong>{mes_sel}</strong> | Línea de Negocio: <strong>{linea_sel}</strong>.</em>
</div>
""", unsafe_allow_html=True)

# Fila de KPIs de rentabilidad (5 columnas). Si agregas o quitas KPIs,
# ajusta el número en st.columns().
r1, r2, r3, r4, r5 = st.columns(5)
render_kpi(r1, "Ingresos Totales", f"{simbolo} {tot_ingresos:,.2f}", f"Ventas ({codigo_sel})", "💰", "#0284c7")
render_kpi(r2, "Costos Directos", f"{simbolo} {tot_costos:,.2f}", f"Costo de ventas ({codigo_sel})", "📉", "#ea580c")
render_kpi(r3, "Margen Bruto", f"{simbolo} {tot_margen:,.2f}", f"Rentabilidad bruta: {pct_margen_global:.1f}%", "💵", "#16a34a")
render_kpi(r4, "Gastos Operativos", f"{simbolo} {tot_gastos:,.2f}", f"OPEX del período ({codigo_sel})", "🏢", "#d97706")
render_kpi(r5, "Utilidad Operativa", f"{simbolo} {tot_utilidad_op:,.2f}", f"Margen operativo: {pct_operativo_global:.2f}%", "🏆", "#7c3aed")

st.divider()

# ==============================================================================
# 8. PANEL DE VISUALIZACIÓN EJECUTIVA (6 GRÁFICOS INTERACTIVOS)
# ==============================================================================
# Patrón de todos los gráficos: agrupar el DataFrame -> crear figura Plotly ->
# ajustar layout -> st.plotly_chart. Distribución: 3 filas x 2 columnas.

# ---- FILA 1: Evolución mensual (barras) + Cascada (waterfall) ---------------
g1, g2 = st.columns(2)

with g1:
    st.subheader(f"📊 Evolución Mensual: Ingresos, Costos y Utilidad ({codigo_sel})")
    # Suma por mes (respeta los filtros activos)
    df_mes = df_er_filt.groupby("Mes", as_index=False)[["Ingresos", "Costos", "Margen_Bruto", "Utilidad_Operativa"]].sum()
    fig_bar = px.bar(
        df_mes,
        x="Mes",
        y=["Ingresos", "Costos", "Margen_Bruto", "Utilidad_Operativa"],
        barmode="group",
        color_discrete_map={
            "Ingresos": "#2563eb",
            "Costos": "#f97316",
            "Margen_Bruto": "#10b981",
            "Utilidad_Operativa": "#7c3aed"
        },
        labels={"value": f"Monto ({simbolo})", "variable": "Rubro"}
    )
    fig_bar.update_layout(height=370, margin=dict(l=10, r=10, t=20, b=10), legend=dict(orientation="h", y=1.15))
    st.plotly_chart(fig_bar, use_container_width=True)

with g2:
    st.subheader(f"🌊 Cascada de Resultados (Waterfall en {codigo_sel})")
    # Cascada: Ingresos (+) -> Costos (-) -> [Margen Bruto = subtotal] ->
    # Gastos Op. (-) -> [Utilidad Operativa = total].
    # measure="total" hace que Plotly dibuje el acumulado hasta ese punto,
    # por eso su valor en `y` es 0 (no se suma nada, solo se muestra el total).
    # `text` define las etiquetas visibles sobre cada barra.
    fig_waterfall = go.Figure(go.Waterfall(
        orientation="v",
        measure=["relative", "relative", "total", "relative", "total"],
        x=["Ingresos", "Costos Directos", "Margen Bruto", "Gastos Operativos", "Utilidad Operativa"],
        textposition="outside",
        text=[
            f"{simbolo}{tot_ingresos:,.0f}",
            f"-{simbolo}{tot_costos:,.0f}",
            f"{simbolo}{tot_margen:,.0f}",
            f"-{simbolo}{tot_gastos:,.0f}",
            f"{simbolo}{tot_utilidad_op:,.0f}",
        ],
        y=[tot_ingresos, -tot_costos, 0, -tot_gastos, 0],
        connector={"line": {"color": "#94a3b8"}},
        increasing={"marker": {"color": "#2563eb"}},
        decreasing={"marker": {"color": "#ef4444"}},
        totals={"marker": {"color": "#10b981"}}
    ))
    fig_waterfall.update_layout(
        height=370,
        margin=dict(l=10, r=10, t=25, b=10),
        yaxis_title=f"Monto ({simbolo})",
        showlegend=False
    )
    st.plotly_chart(fig_waterfall, use_container_width=True)

# ---- FILA 2: Rendimiento por línea de negocio + Tendencia de márgenes % -----
g3, g4 = st.columns(2)

with g3:
    st.subheader(f"🏢 Ingresos y Utilidad por Línea de Negocio ({codigo_sel})")
    df_linea = df_er_filt.groupby("Linea_Negocio", as_index=False)[["Ingresos", "Margen_Bruto", "Utilidad_Operativa"]].sum()
    # Orden ascendente: en barras horizontales la línea con más ingresos
    # queda arriba.
    df_linea = df_linea.sort_values(by="Ingresos", ascending=True)
    fig_linea = px.bar(
        df_linea,
        y="Linea_Negocio",
        x=["Ingresos", "Margen_Bruto", "Utilidad_Operativa"],
        orientation="h",
        barmode="group",
        color_discrete_map={
            "Ingresos": "#0284c7",
            "Margen_Bruto": "#16a34a",
            "Utilidad_Operativa": "#7c3aed"
        },
        labels={"value": f"Monto ({simbolo})", "Linea_Negocio": "Línea", "variable": "Indicador"}
    )
    fig_linea.update_layout(height=360, margin=dict(l=10, r=10, t=20, b=10), legend=dict(orientation="h", y=1.15))
    st.plotly_chart(fig_linea, use_container_width=True)

with g4:
    st.subheader("📈 Evolución de Eficiencia: % Margen Bruto vs. % Operativo")
    # Los porcentajes mensuales se recalculan sobre las SUMAS del mes (no se
    # promedian porcentajes de filas), lo cual es estadísticamente correcto.
    df_pct_mes = df_er_filt.groupby("Mes", as_index=False)[["Ingresos", "Margen_Bruto", "Utilidad_Operativa"]].sum()
    df_pct_mes["% Margen Bruto"] = (df_pct_mes["Margen_Bruto"] / df_pct_mes["Ingresos"] * 100).round(2)
    df_pct_mes["% Margen Operativo"] = (df_pct_mes["Utilidad_Operativa"] / df_pct_mes["Ingresos"] * 100).round(2)

    fig_line = px.line(
        df_pct_mes,
        x="Mes",
        y=["% Margen Bruto", "% Margen Operativo"],
        markers=True,
        color_discrete_map={"% Margen Bruto": "#10b981", "% Margen Operativo": "#7c3aed"},
        labels={"value": "Porcentaje (%)", "variable": "Métrica"}
    )
    # Línea de referencia: meta de margen bruto del 50 % (cambiar y=50 si la
    # meta de la empresa es otra; el mismo umbral se usa en color_margen()).
    fig_line.add_hline(y=50, line_dash="dash", line_color="#64748b", annotation_text="Meta Bruta 50%")
    fig_line.update_layout(height=360, margin=dict(l=10, r=10, t=20, b=10), legend=dict(orientation="h", y=1.15))
    st.plotly_chart(fig_line, use_container_width=True)

# ---- FILA 3: Composición del Balance (dona) + Treemap de cuentas ------------
g5, g6 = st.columns(2)

with g5:
    st.subheader(f"🍩 Estructura del Balance General ({codigo_sel})")
    df_cat = df_balance.groupby("Categoria", as_index=False)["Monto_Mostrar"].sum()
    fig_pie = px.pie(
        df_cat,
        names="Categoria",
        values="Monto_Mostrar",
        hole=0.48,  # el hueco convierte el pie en dona
        color="Categoria",
        color_discrete_map={"Activos": "#2563eb", "Pasivos": "#ef4444", "Capital": "#10b981"}
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    fig_pie.update_layout(height=370, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_pie, use_container_width=True)

with g6:
    st.subheader(f"🌳 Mapa Jerárquico de Cuentas Contables ({codigo_sel})")

    # 1. Agrupar por jerarquía contable y filtrar montos positivos (Treemap no acepta negativos como Depreciación)
    # OJO: al excluir cuentas negativas (p. ej. depreciación acumulada) la suma
    # del treemap puede no coincidir con el total de Activos del KPI.
    df_tree = (
        df_balance.groupby(["Categoria", "Subcategoria", "Cuenta"], as_index=False)["Monto_Mostrar"]
        .sum()
    )
    df_tree = df_tree[df_tree["Monto_Mostrar"] > 0].copy()

    # path define los niveles: Raíz -> Categoría -> Subcategoría -> Cuenta.
    # px.Constant crea el nodo raíz "Balance General". La clave "(?)" del mapa
    # de colores es el color del nodo raíz (Plotly lo etiqueta así).
    fig_tree = px.treemap(
        df_tree,
        path=[px.Constant("Balance General"), "Categoria", "Subcategoria", "Cuenta"],
        values="Monto_Mostrar",
        color="Categoria",
        color_discrete_map={
            "(?)": "#e2e8f0",
            "Activos": "#2563eb",
            "Pasivos": "#ef4444",
            "Capital": "#10b981"
        }
    )
    # hovertemplate: tooltip personalizado con la divisa activa y el % que
    # representa cada nodo respecto a su padre.
    fig_tree.update_traces(
        textinfo="label+value+percent parent",
        hovertemplate="<b>%{label}</b><br>Monto: " + simbolo + " %{value:,.2f}<br>Participación: %{percentParent:.1%}<extra></extra>"
    )
    fig_tree.update_layout(height=370, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_tree, use_container_width=True)

# ==============================================================================
# 9. TABLAS FINANCIERAS + DESCARGA MULTIDIVISA + MONITOR DE API
# ==============================================================================
# Tres pestañas. Los títulos se construyen con la divisa activa.
tab1, tab2, tab3 = st.tabs([
    f"📋 Estado de Resultados ({codigo_sel})",
    f"🏛️ Balance General ({codigo_sel})",
    "💱 Monitor Global de Divisas (API)"
])

# ---- Pestaña 1: Estado de Resultados (con semáforo de margen) ---------------
with tab1:
    st.subheader(f"Detalle Operativo en {info_divisa['nombre']}")

    # Columnas a mostrar y su orden. `df_tabla_er` también alimenta la
    # descarga a Excel de la pestaña 2 (dependencia entre pestañas).
    df_tabla_er = df_er_filt[[
        "Mes", "Linea_Negocio", "Ingresos", "Costos", "Margen_Bruto",
        "Porcentaje_Margen", "Gastos_Operativos", "Utilidad_Operativa", "Porcentaje_Operativo"
    ]].copy()

    def color_margen(val):
        """
        Semáforo para el % de margen bruto (devuelve estilo CSS de celda):
          verde    >= 50 %   (meta saludable)
          rojo     <  40 %   (alerta)
          amarillo 40-50 %   (zona intermedia)
        Ajustar los umbrales aquí según la política de la empresa.
        """
        if val >= 50:
            return "background-color: #dcfce7; color: #166534; font-weight: bold;"
        elif val < 40:
            return "background-color: #fee2e2; color: #991b1b; font-weight: bold;"
        return "background-color: #fef9c3; color: #854d0e; font-weight: bold;"

    # `.format` pone símbolo y decimales; `{{:,.2f}}` con doble llave es
    # intencional: el f-string deja una llave simple y Styler rellena el valor.
    # `.map` aplica el semáforo solo a la columna Porcentaje_Margen.
    styler_er = (
        df_tabla_er.style
        .format({
            "Ingresos": f"{simbolo} {{:,.2f}}",
            "Costos": f"{simbolo} {{:,.2f}}",
            "Margen_Bruto": f"{simbolo} {{:,.2f}}",
            "Gastos_Operativos": f"{simbolo} {{:,.2f}}",
            "Utilidad_Operativa": f"{simbolo} {{:,.2f}}",
            "Porcentaje_Margen": "{:.2f}%",
            "Porcentaje_Operativo": "{:.2f}%"
        })
        .map(color_margen, subset=["Porcentaje_Margen"])
    )
    st.dataframe(styler_er, use_container_width=True, hide_index=True, height=400)

# ---- Pestaña 2: Balance General + descarga a Excel --------------------------
with tab2:
    st.subheader(f"Cuentas del Balance General en {info_divisa['nombre']}")

    # Se muestran el monto original (DOP) y el convertido, lado a lado.
    # La columna convertida se renombra con el símbolo de la divisa activa.
    df_tabla_bg = df_balance[["Codigo", "Categoria", "Subcategoria", "Cuenta", "Monto_DOP", "Monto_Mostrar"]].copy()
    df_tabla_bg.rename(columns={"Monto_Mostrar": f"Monto ({simbolo})"}, inplace=True)

    def color_categoria(val):
        """Color de fondo por categoría contable; sin coincidencia -> sin estilo."""
        colores = {
            "Activos": "background-color: #dbeafe; color: #1e40af; font-weight: bold;",
            "Pasivos": "background-color: #fee2e2; color: #991b1b; font-weight: bold;",
            "Capital": "background-color: #dcfce7; color: #166534; font-weight: bold;"
        }
        return colores.get(val, "")

    styler_bg = (
        df_tabla_bg.style
        .format({
            "Monto_DOP": "RD$ {:,.2f}",
            f"Monto ({simbolo})": f"{simbolo} {{:,.2f}}"
        })
        .map(color_categoria, subset=["Categoria"])
    )
    st.dataframe(styler_bg, use_container_width=True, hide_index=True, height=450)

    # Botón de exportación a Excel en la divisa actual.
    # Usa `df_tabla_er` (definido en la pestaña 1) y `df_tabla_bg` (arriba).
    # Si algún día separas las pestañas en funciones, pasa ambos como parámetros.
    excel_bytes = generar_excel_descarga(df_tabla_er, df_tabla_bg)
    st.download_button(
        label=f"📥 Descargar Reporte Financiero Completo en {codigo_sel} (.xlsx)",
        data=excel_bytes,
        file_name=f"reporte_financiero_{codigo_sel.lower()}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ---- Pestaña 3: Monitor de tipos de cambio (auditoría de la API) ------------
# Muestra TODAS las divisas del catálogo con su tasa real y un estado, para
# que cualquier persona pueda verificar de dónde sale cada número.
with tab3:
    st.subheader("🌐 Tabla Maestra de Tipos de Cambio de Mercado (Contra Peso Dominicano)")

    filas_divisas = []
    for cod, info in DICCIONARIO_DIVISAS.items():
        # Aquí el orden del retorno es (factor, valor_en_RD$, disponible)
        factor_val, t_rd, disponible = resolver_tasa(cod, tasas_api)
        filas_divisas.append({
            "Bandera": info["icono"],
            "Código": cod,
            "Nombre de la Moneda": info["nombre"],
            "Símbolo": info["simbolo"],
            "Valor de 1 Unidad en RD$": t_rd,
            "Factor (1 RD$ equivale a)": factor_val,
            "Estado": "🟢 En vivo" if disponible else "🔴 Sin dato"
        })

    # Orden de mayor a menor valor en RD$; las divisas sin dato (None/NaN) van
    # al final gracias a na_position="last".
    df_todas_divisas = pd.DataFrame(filas_divisas).sort_values(
        by="Valor de 1 Unidad en RD$", ascending=False, na_position="last"
    )
    n_sin_dato = int((df_todas_divisas["Estado"] == "🔴 Sin dato").sum())

    # Mensaje de estado honesto según lo que realmente respondió la API
    if not api_ok:
        st.error("🔴 La API no respondió: no hay tasas reales disponibles en este momento.")
    elif n_sin_dato > 0:
        st.caption(f"Tasas de la API pública de mercado | Fecha de la API: **{fecha_api}** | ⚠️ {n_sin_dato} divisa(s) sin dato en la API.")
    else:
        st.caption(f"Tasas de la API pública de mercado (todas en vivo) | Fecha de la API: **{fecha_api}**")

    # na_rep="—" muestra una raya en las celdas sin dato en lugar de "nan"
    styler_div = (
        df_todas_divisas.style
        .format({
            "Valor de 1 Unidad en RD$": "RD$ {:,.4f}",
            "Factor (1 RD$ equivale a)": "{:,.6f}"
        }, na_rep="—")
    )
    st.dataframe(styler_div, use_container_width=True, hide_index=True, height=460)

    st.caption(
        "ℹ️ Tasas de mercado medio de agregador público (fawazahmed0/currency-api), "
        "referenciales respecto a tasas de ventanilla del Banco Central de la República Dominicana."
    )