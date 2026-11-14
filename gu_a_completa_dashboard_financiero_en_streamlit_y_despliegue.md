# Guía Completa: Dashboard Financiero en Streamlit (Excel + API Divisas + Despliegue en la Nube)

Esta guía documenta la fase final del proyecto: construir una aplicación web interactiva con **Streamlit** que consume datos financieros desde un libro de **Excel**, consulta en tiempo real la cotización del **Dólar (`USD`)** frente al **Peso Dominicano (`DOP`)** mediante una **API**, y presenta tarjetas KPI personalizadas, gráficos interactivos y tablas con formato condicional. Además, incluye los pasos exactos para subir el proyecto a **GitHub** y publicarlo gratis en **Streamlit Community Cloud**.

---

## 1. Arquitectura del Proyecto y Librerías Necesarias

Para que tu proyecto funcione tanto en tu computadora como en la nube al publicarlo, tu carpeta debe tener exactamente esta estructura:

```text
proyecto-dashboard-financiero/
├── app.py                        # Código principal del dashboard en Streamlit
├── estados_financieros_rd.xlsx   # Base de datos contable (Balance y Resultados)
├── requirements.txt              # Lista de librerías que instalará el servidor en la nube
└── README.md                     # Documentación del repositorio (opcional)
```

### ¿Qué librerías se necesitan para ejecutarlo y publicarlo?

El archivo `requirements.txt` le indica a **Streamlit Community Cloud** qué paquetes debe instalar automáticamente en su servidor Linux antes de arrancar tu aplicación:

1. **`streamlit`**: El framework principal que convierte scripts de Python en aplicaciones web interactivas sin necesidad de escribir HTML/JS desde cero.
2. **`pandas`**: Motor de análisis de datos encargado de leer el Excel, limpiar filas de totales, recalcular márgenes y aplicar conversiones monetarias.
3. **`openpyxl`**: Dependencia obligatoria de Pandas para poder abrir y leer archivos de Excel modernos (`.xlsx`).
4. **`requests`**: Cliente HTTP utilizado para hacer la petición `GET` a la API de tasas de cambio.
5. **`plotly`**: Librería de visualización interactiva utilizada para crear los gráficos de barras agrupadas y de dona.

### Instalación local en tu entorno virtual `(venv)`

Con tu entorno virtual activo en la terminal, instala todas las dependencias leyendo directamente el archivo `requirements.txt`:

```powershell
pip install -r requirements.txt
```

---

## 2. Código Completo del Dashboard (`app.py`) Bien Comentado

Asegúrate de que tu archivo `app.py` contenga el siguiente código estructurado y comentado paso a paso:

```python
# ==============================================================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# ==============================================================================
import streamlit as st          # Framework para construir la interfaz web
import pandas as pd             # Manipulación y limpieza de tablas (DataFrames)
import requests                 # Peticiones HTTP (GET) hacia la API de divisas
import plotly.express as px     # Creación de gráficos interactivos

# ==============================================================================
# 2. CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS (TARJETAS KPI + BORDES + SOMBRAS)
# ==============================================================================
# set_page_config siempre debe ser la primera instrucción de Streamlit en el script
st.set_page_config(
    page_title="Dashboard Financiero | DOP & USD",
    page_icon="📊",
    layout="wide",                     # Aprovecha todo el ancho de la pantalla
    initial_sidebar_state="expanded"   # Mantiene el menú lateral abierto al iniciar
)

# Inyectamos código CSS personalizado para diseñar las tarjetas KPI con bordes redondeados,
# franja lateral de color, sombra suave y efecto hover al pasar el mouse.
st.markdown("""
<style>
    .main {
        background-color: #f8fafc;
    }
    .kpi-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-left: 6px solid #1e3a8a;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 12px;
        transition: transform 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    .kpi-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 1.55rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 4px;
    }
    .kpi-sub {
        font-size: 0.80rem;
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
    .header-banner h1 {
        margin: 0;
        font-size: 1.85rem;
        font-weight: 800;
    }
    .header-banner p {
        margin: 6px 0 0 0;
        font-size: 0.95rem;
        color: #dbeafe;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. FUNCIONES DE EXTRACCIÓN DE DATOS CON CACHÉ (@st.cache_data)
# ==============================================================================
# El decorador @st.cache_data(ttl=3600) guarda el resultado en memoria durante 1 hora
# para no saturar la API cada vez que el usuario hace clic en un filtro.
@st.cache_data(ttl=3600)
def obtener_tasa_cambio():
    """Consulta la API de divisas con respaldo automático y retorna tasa DOP->USD."""
    urls = [
        "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/dop.json",
        "https://latest.currency-api.pages.dev/v1/currencies/dop.json",
    ]
    for url in urls:
        try:
            res = requests.get(url, timeout=8)
            if res.status_code == 200:
                datos = res.json()
                tasa_dop_usd = datos["dop"]["usd"]
                fecha_api = datos.get("date", "Actualizada")
                return tasa_dop_usd, (1 / tasa_dop_usd), fecha_api
        except requests.exceptions.RequestException:
            continue
    # Si ambos servidores fallan, retorna una tasa de respaldo para no romper la app
    return (1 / 60.80), 60.80, "Tasa Referencial (Offline)"

@st.cache_data
def cargar_excel(ruta_o_buffer):
    """Lee el Excel y recalcula márgenes en Pandas para evitar celdas NaN."""
    # header=3 indica que los nombres de columnas están en la fila 4 de Excel
    df_bg = pd.read_excel(ruta_o_buffer, sheet_name="Balance_General", header=3).dropna(subset=["Codigo"])
    df_er = pd.read_excel(ruta_o_buffer, sheet_name="Estado_Resultados", header=3)
    
    # Excluimos la fila 'TOTAL' para evitar duplicar sumas
    df_er = df_er[df_er["Mes"] != "TOTAL"].copy()

    # Recalculamos márgenes directamente en Python (evita fórmulas sin caché en Excel)
    df_er["Margen_Bruto_DOP"] = df_er["Ingresos_DOP"] - df_er["Costos_DOP"]
    df_er["Porcentaje_Margen"] = (df_er["Margen_Bruto_DOP"] / df_er["Ingresos_DOP"]) * 100
    return df_bg, df_er

# ==============================================================================
# 4. BARRA LATERAL (SIDEBAR): CONTROLES DE MONEDA Y CARGA DE ARCHIVOS
# ==============================================================================
with st.sidebar:
    st.markdown("## ⚙️ Panel de Control")
    
    # Selector interactivo para alternar todo el dashboard entre Pesos y Dólares
    moneda_vista = st.radio(
        "💱 Moneda de Visualización:",
        options=["Pesos Dominicanos (RD$)", "Dólares Estadounidenses (US$)"],
        index=0
    )
    es_usd = "US$" in moneda_vista
    simbolo = "US$" if es_usd else "RD$"

    st.divider()

    # Permite al usuario subir un nuevo Excel desde la web o usar el del repositorio
    archivo_subido = st.file_uploader("📂 Cargar Excel actualizado (.xlsx)", type=["xlsx"])
    fuente_excel = archivo_subido if archivo_subido is not None else "estados_financieros_rd.xlsx"

    # Botón para limpiar la caché y forzar una nueva consulta a la API
    if st.button("🔄 Actualizar Tasa API", use_container_width=True):
        st.cache_data.clear()

# ==============================================================================
# 5. PROCESAMIENTO Y APLICACIÓN DE FILTROS
# ==============================================================================
tasa_dop_a_usd, tasa_usd_a_dop, fecha_tasa = obtener_tasa_cambio()
factor = tasa_dop_a_usd if es_usd else 1.0  # Si es USD multiplica por tasa; si es DOP por 1

try:
    df_balance, df_resultados = cargar_excel(fuente_excel)
except Exception as e:
    st.error(f"❌ Error al leer el archivo Excel: {e}")
    st.stop()

# Filtros dinámicos de Meses y Líneas de Negocio en la barra lateral
with st.sidebar:
    st.divider()
    st.markdown("### 🔍 Filtros de Resultados")
    meses_disp = sorted(df_resultados["Mes"].unique())
    meses_sel = st.multiselect("📅 Meses:", options=meses_disp, default=meses_disp)

    lineas_disp = sorted(df_resultados["Linea_Negocio"].unique())
    lineas_sel = st.multiselect("🏢 Línea de Negocio:", options=lineas_disp, default=lineas_disp)

# Filtramos el DataFrame según la selección del usuario
df_er_filt = df_resultados[
    (df_resultados["Mes"].isin(meses_sel)) &
    (df_resultados["Linea_Negocio"].isin(lineas_sel))
].copy()

# Convertimos las columnas financieras según la moneda elegida
df_balance["Monto_Mostrar"] = (df_balance["Monto_DOP"] * factor).round(2)
df_er_filt["Ingresos"] = (df_er_filt["Ingresos_DOP"] * factor).round(2)
df_er_filt["Costos"] = (df_er_filt["Costos_DOP"] * factor).round(2)
df_er_filt["Margen_Bruto"] = (df_er_filt["Margen_Bruto_DOP"] * factor).round(2)
df_er_filt["Gastos_Operativos"] = (df_er_filt["Gastos_Operativos_DOP"] * factor).round(2)

# ==============================================================================
# 6. BANNER SUPERIOR Y TARJETAS KPI PERSONALIZADAS
# ==============================================================================
st.markdown(f"""
<div class="header-banner">
    <h1>📊 Dashboard Financiero Ejecutivo (DOP ⇄ USD)</h1>
    <p>Consolidación de Balance General y Estado de Resultados conectada en tiempo real a API de Divisas • Tasa actual: <b>US$ 1 = RD$ {tasa_usd_a_dop:,.2f}</b> ({fecha_tasa})</p>
</div>
""", unsafe_allow_html=True)

def render_kpi(col, titulo, valor_str, subtitulo, icono, color_borde):
    """Función auxiliar que dibuja una tarjeta KPI HTML dentro de una columna."""
    col.markdown(f"""
    <div class="kpi-card" style="border-left-color: {color_borde};">
        <div class="kpi-title">{icono} {titulo}</div>
        <div class="kpi-value">{valor_str}</div>
        <div class="kpi-sub">{subtitulo}</div>
    </div>
    """, unsafe_allow_html=True)

# Cálculos agregados para las tarjetas
tot_activos = df_balance.loc[df_balance["Categoria"] == "Activos", "Monto_Mostrar"].sum()
tot_pasivos = df_balance.loc[df_balance["Categoria"] == "Pasivos", "Monto_Mostrar"].sum()
tot_capital = df_balance.loc[df_balance["Categoria"] == "Capital", "Monto_Mostrar"].sum()

tot_ingresos = df_er_filt["Ingresos"].sum()
tot_costos = df_er_filt["Costos"].sum()
tot_margen = df_er_filt["Margen_Bruto"].sum()
pct_margen_global = (tot_margen / tot_ingresos * 100) if tot_ingresos > 0 else 0.0

# Fila 1 de KPIs: Balance General (3 columnas)
st.markdown("### 🏦 Indicadores de Situación Financiera (Balance General)")
k1, k2, k3 = st.columns(3)
render_kpi(k1, "Total Activos", f"{simbolo} {tot_activos:,.2f}", "Recursos y bienes totales", "🏛️", "#2563eb")
render_kpi(k2, "Total Pasivos", f"{simbolo} {tot_pasivos:,.2f}", f"Endeudamiento: {(tot_pasivos/tot_activos*100):.1f}% de activos", "💳", "#dc2626")
render_kpi(k3, "Total Capital", f"{simbolo} {tot_capital:,.2f}", f"Patrimonio neto: {(tot_capital/tot_activos*100):.1f}% de activos", "🛡️", "#059669")

# Fila 2 de KPIs: Estado de Resultados (4 columnas)
st.markdown("### 📈 Indicadores de Rentabilidad (Estado de Resultados)")
r1, r2, r3, r4 = st.columns(4)
render_kpi(r1, "Ingresos Totales", f"{simbolo} {tot_ingresos:,.2f}", "Ventas brutas del período", "💰", "#0284c7")
render_kpi(r2, "Costos Directos", f"{simbolo} {tot_costos:,.2f}", "Costo de ventas / servicios", "📉", "#ea580c")
render_kpi(r3, "Margen Bruto", f"{simbolo} {tot_margen:,.2f}", "Utilidad antes de gastos op.", "💵", "#16a34a")
render_kpi(r4, "% Margen Bruto", f"{pct_margen_global:.2f}%", "Meta saludable: ≥ 50.00%", "🎯", "#7c3aed")

st.divider()

# ==============================================================================
# 7. GRÁFICOS INTERACTIVOS CON PLOTLY
# ==============================================================================
g1, g2 = st.columns(2)

with g1:
    st.subheader("📊 Evolución Mensual: Ingresos vs. Margen")
    df_mes = df_er_filt.groupby("Mes", as_index=False)[["Ingresos", "Costos", "Margen_Bruto"]].sum()
    fig_bar = px.bar(
        df_mes,
        x="Mes",
        y=["Ingresos", "Costos", "Margen_Bruto"],
        barmode="group",
        color_discrete_map={"Ingresos": "#2563eb", "Costos": "#f97316", "Margen_Bruto": "#10b981"},
        labels={"value": f"Monto ({simbolo})", "variable": "Rubro"}
    )
    fig_bar.update_layout(height=360, margin=dict(l=10, r=10, t=20, b=10), legend=dict(orientation="h", y=1.12))
    st.plotly_chart(fig_bar, use_container_width=True)

with g2:
    st.subheader("🍩 Composición del Balance General")
    df_cat = df_balance.groupby("Categoria", as_index=False)["Monto_Mostrar"].sum()
    fig_pie = px.pie(
        df_cat,
        names="Categoria",
        values="Monto_Mostrar",
        hole=0.48,
        color="Categoria",
        color_discrete_map={"Activos": "#2563eb", "Pasivos": "#ef4444", "Capital": "#10b981"}
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    fig_pie.update_layout(height=360, margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# ==============================================================================
# 8. TABLAS DETALLADAS CON FORMATO CONDICIONAL (PANDAS STYLER)
# ==============================================================================
tab1, tab2 = st.tabs(["📋 Tabla: Estado de Resultados", "🏛️ Tabla: Balance General"])

with tab1:
    st.subheader(f"Detalle de Ingresos, Costos y Márgenes ({moneda_vista})")
    df_tabla_er = df_er_filt[[
        "Mes", "Linea_Negocio", "Ingresos", "Costos", "Margen_Bruto", "Porcentaje_Margen", "Gastos_Operativos"
    ]].copy()

    # Aplica colores tipo semáforo según el porcentaje de rentabilidad
    def color_margen(val):
        if val >= 50:
            return "background-color: #dcfce7; color: #166534; font-weight: bold;"
        elif val < 40:
            return "background-color: #fee2e2; color: #991b1b; font-weight: bold;"
        return "background-color: #fef9c3; color: #854d0e; font-weight: bold;"

    styler_er = (
        df_tabla_er.style
        .format({
            "Ingresos": f"{simbolo} {{:,.2f}}",
            "Costos": f"{simbolo} {{:,.2f}}",
            "Margen_Bruto": f"{simbolo} {{:,.2f}}",
            "Gastos_Operativos": f"{simbolo} {{:,.2f}}",
            "Porcentaje_Margen": "{:.2f}%"
        })
        .map(color_margen, subset=["Porcentaje_Margen"])
    )
    st.dataframe(styler_er, use_container_width=True, hide_index=True, height=400)

with tab2:
    st.subheader(f"Cuentas del Balance General ({moneda_vista})")
    df_tabla_bg = df_balance[["Codigo", "Categoria", "Subcategoria", "Cuenta", "Monto_DOP", "Monto_Mostrar"]].copy()
    df_tabla_bg.rename(columns={"Monto_Mostrar": f"Monto ({simbolo})"}, inplace=True)

    # Colorea cada categoría contable para facilitar su lectura
    def color_categoria(val):
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
```

---

## 3. Ejecución Local

Para probar la aplicación en tu computadora antes de subirla a internet, abre la terminal con `(venv)` activo y ejecuta:

```powershell
streamlit run app.py
```

Esto abrirá automáticamente tu navegador en `http://localhost:8501`.

---

## 4. Cómo Publicar el Proyecto en GitHub y Streamlit Cloud (Gratis)

Una vez que verifiques que tu dashboard funciona bien en local, sigue estos pasos para tenerlo en línea con una URL pública compartible:

### Paso 1: Subir los archivos a GitHub
1. Crea un nuevo repositorio público en [github.com](https://github.com) (por ejemplo: `dashboard-financiero-api-excel`).
2. **Importante:** No subas la carpeta `venv/` a GitHub (solo sube `app.py`, `estados_financieros_rd.xlsx` y `requirements.txt`).
3. Ejecuta estos comandos en tu terminal dentro de la carpeta del proyecto:
   ```bash
   git init
   git add app.py estados_financieros_rd.xlsx requirements.txt
   git commit -m "Subiendo dashboard financiero en Streamlit con API de divisas"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/dashboard-financiero-api-excel.git
   git push -u origin main
   ```

### Paso 2: Desplegar en Streamlit Community Cloud
1. Entra a [share.streamlit.io](https://share.streamlit.io) e inicia sesión con tu cuenta de **GitHub**.
2. Haz clic en el botón azul **"Create app"** (o **"New app"**).
3. Selecciona:
   * **Repository:** `TU_USUARIO/dashboard-financiero-api-excel`
   * **Branch:** `main`
   * **Main file path:** `app.py`
4. Haz clic en **"Deploy!"**.
5. En unos 2 minutos, Streamlit leerá tu `requirements.txt`, instalará las librerías en la nube y te entregará tu enlace público listo para compartir en tu portafolio o LinkedIn.