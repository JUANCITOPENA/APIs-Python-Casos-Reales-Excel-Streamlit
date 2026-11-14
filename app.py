import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import io
import time

# ==============================================================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS PERSONALIZADOS (BENTO CARDS + BORDES)
# ==============================================================================
st.set_page_config(
    page_title="Dashboard Financiero DOP & USD | Sincronizado con GitHub",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Fondo general */
    .main {
        background-color: #f8fafc;
    }
    /* Estilo de Tarjetas Bento KPI con bordes y acento lateral */
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
    /* Banner superior */
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
    /* Badge de Fuente Activa */
    .source-badge {
        display: inline-block;
        background-color: #dcfce7;
        color: #166534;
        border: 1px solid #86efac;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.80rem;
        font-weight: 700;
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)

# URL oficial del archivo Excel en crudo alojado en GitHub
URL_EXCEL_GITHUB = "https://raw.githubusercontent.com/JUANCITOPENA/APIs-Python-Casos-Reales-Excel-Streamlit/main/estados_financieros_rd.xlsx"

# ==============================================================================
# 2. FUNCIONES DE EXTRACCIÓN (API DIVISAS + EXCEL DESDE GITHUB / LOCAL) CON CACHÉ
# ==============================================================================
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
    # Respaldo de emergencia si no hay internet
    return (1 / 60.83), 60.83, "Tasa Referencial (Offline)"

@st.cache_data(ttl=60)
def descargar_excel_github(url):
    """
    Descarga el archivo Excel en vivo desde GitHub con headers anticaché.
    TTL de 60 segundos: cada 60s consulta si hay nueva versión en el repo.
    """
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    }
    # Parametro de versión con timestamp para evitar el caché intermedio de CDNs
    url_con_ts = f"{url}?v={int(time.time() // 60)}"
    try:
        res = requests.get(url_con_ts, headers=headers, timeout=12)
        if res.status_code == 200 and len(res.content) > 1000:
            return io.BytesIO(res.content), "🌐 Repositorio GitHub (En Vivo)", True
    except requests.exceptions.RequestException:
        pass
    
    # Intento con URL limpia de respaldo
    try:
        res_clean = requests.get(url, timeout=10)
        if res_clean.status_code == 200 and len(res_clean.content) > 1000:
            return io.BytesIO(res_clean.content), "🌐 Repositorio GitHub (En Vivo)", True
    except requests.exceptions.RequestException:
        pass

    return None, "Error de Conexión GitHub", False

def procesar_excel(ruta_o_buffer):
    """Lee las hojas del Excel y recalcula márgenes en Pandas para evitar celdas vacías."""
    df_bg = pd.read_excel(ruta_o_buffer, sheet_name="Balance_General", header=3).dropna(subset=["Codigo"])
    df_er = pd.read_excel(ruta_o_buffer, sheet_name="Estado_Resultados", header=3)
    df_er = df_er[df_er["Mes"] != "TOTAL"].copy()

    # Recálculo limpio en memoria
    df_er["Margen_Bruto_DOP"] = df_er["Ingresos_DOP"] - df_er["Costos_DOP"]
    df_er["Porcentaje_Margen"] = (df_er["Margen_Bruto_DOP"] / df_er["Ingresos_DOP"]) * 100
    return df_bg, df_er

# ==============================================================================
# 3. SIDEBAR: CONTROLES, ORIGEN DE DATOS (GITHUB / LOCAL / UPLOAD) Y FILTROS
# ==============================================================================
with st.sidebar:
    st.markdown("## ⚙️ Panel de Control")
    
    # Selector de Moneda Principal
    moneda_vista = st.radio(
        "💱 Moneda de Visualización:",
        options=["Pesos Dominicanos (RD$)", "Dólares Estadounidenses (US$)"],
        index=0
    )
    es_usd = "US$" in moneda_vista
    simbolo = "US$" if es_usd else "RD$"

    st.divider()

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
    es_github = False

    if opcion_origen == "🌐 GitHub Live (En Tiempo Real)":
        buffer_excel, etiqueta_fuente, exito = descargar_excel_github(URL_EXCEL_GITHUB)
        if exito:
            st.success("✅ Conectado al repo oficial en GitHub.")
            st.caption(f"Cada vez que subas cambios a GitHub, Streamlit los reflejará automáticamente.")
            if st.button("🔄 Refrescar datos desde GitHub"):
                st.cache_data.clear()
                st.rerun()
            es_github = True
        else:
            st.warning("⚠️ No se pudo descargar desde GitHub. Usando archivo local de respaldo.")
            buffer_excel = "estados_financieros_rd.xlsx"
            etiqueta_fuente = "💻 Archivo Local (Fallback de Emergencia)"

    elif opcion_origen == "📂 Subir archivo Excel (.xlsx)":
        archivo_subido = st.file_uploader("Arrastra tu archivo Excel contable:", type=["xlsx"])
        if archivo_subido is not None:
            buffer_excel = archivo_subido
            etiqueta_fuente = f"📂 Subido por usuario: {archivo_subido.name}"
            st.success("✅ Archivo cargado correctamente.")
        else:
            buffer_excel = "estados_financieros_rd.xlsx"
            etiqueta_fuente = "💻 Archivo Local (En espera de archivo)"
            st.info("ℹ️ Mostrando datos de respaldo locales hasta que subas un archivo.")

    else:
        buffer_excel = "estados_financieros_rd.xlsx"
        etiqueta_fuente = "💻 Archivo Local del Servidor"

    # Botón para refrescar tasa de API
    if st.button("🔄 Actualizar Tasa de Divisas"):
        st.cache_data.clear()
        st.rerun()

# ==============================================================================
# 4. CARGA DE DATOS Y CONVERSIÓN DE MONEDA
# ==============================================================================
tasa_dop_a_usd, tasa_usd_a_rd, fecha_tasa = obtener_tasa_cambio()

try:
    df_balance, df_resultados = procesar_excel(buffer_excel)
except Exception as e:
    st.error(f"Error procesando el archivo Excel: {e}")
    st.stop()

# Aplicar factor de conversión según moneda elegida
factor = tasa_dop_a_usd if es_usd else 1.0

df_balance["Monto_Mostrar"] = (df_balance["Monto_DOP"] * factor).round(2)
df_resultados["Ingresos"] = (df_resultados["Ingresos_DOP"] * factor).round(2)
df_resultados["Costos"] = (df_resultados["Costos_DOP"] * factor).round(2)
df_resultados["Margen_Bruto"] = (df_resultados["Margen_Bruto_DOP"] * factor).round(2)
df_resultados["Gastos_Operativos"] = (df_resultados["Gastos_Operativos_DOP"] * factor).round(2)

# ==============================================================================
# 5. HEADER Y FILTROS INTERACTIVOS
# ==============================================================================
st.markdown(f"""
<div class="header-banner">
    <h1>🏛️ Dashboard Financiero Ejecutivo</h1>
    <p>Consumo de APIs REST en Vivo + Integración Continua con Excel desde GitHub + Analítica Multimoneda</p>
</div>
""", unsafe_allow_html=True)

# Barra de estado y filtros de página
col_info1, col_info2, col_info3 = st.columns([2, 1, 1])

with col_info1:
    st.markdown(f"**Fuente de Datos Activa:** `{etiqueta_fuente}`")
    st.caption(f"Tasa de Cambio Oficial: **US$ 1.00 = RD$ {tasa_usd_a_rd:,.2f}** | Fecha API: **{fecha_tasa}**")

with col_info2:
    lista_meses = ["Todos"] + sorted(list(df_resultados["Mes"].unique()))
    mes_sel = st.selectbox("📅 Filtrar por Mes:", lista_meses, index=0)

with col_info3:
    lista_lineas = ["Todas"] + sorted(list(df_resultados["Linea_Negocio"].unique()))
    linea_sel = st.selectbox("🏢 Línea de Negocio:", lista_lineas, index=0)

# Aplicar filtros al Estado de Resultados
df_er_filt = df_resultados.copy()
if mes_sel != "Todos":
    df_er_filt = df_er_filt[df_er_filt["Mes"] == mes_sel]
if linea_sel != "Todas":
    df_er_filt = df_er_filt[df_er_filt["Linea_Negocio"] == linea_sel]

# ==============================================================================
# 6. CÁLCULO DE TOTALES Y TARJETAS BENTO KPI
# ==============================================================================
# Balance General
tot_activos = df_balance[df_balance["Categoria"] == "Activos"]["Monto_Mostrar"].sum()
tot_pasivos = df_balance[df_balance["Categoria"] == "Pasivos"]["Monto_Mostrar"].sum()
tot_capital = df_balance[df_balance["Categoria"] == "Capital"]["Monto_Mostrar"].sum()

# Estado de Resultados
tot_ingresos = df_er_filt["Ingresos"].sum()
tot_costos = df_er_filt["Costos"].sum()
tot_margen = df_er_filt["Margen_Bruto"].sum()
pct_margen_global = (tot_margen / tot_ingresos * 100) if tot_ingresos > 0 else 0

def render_kpi(col, titulo, valor, subtitulo, icono="📌", color_borde="#1e3a8a"):
    col.markdown(f"""
    <div class="kpi-card" style="border-left-color: {color_borde};">
        <div class="kpi-title">{icono} {titulo}</div>
        <div class="kpi-value">{valor}</div>
        <div class="kpi-sub">{subtitulo}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("### 🏛️ Posición Financiera (Balance General)")
k1, k2, k3 = st.columns(3)
render_kpi(k1, "Total Activos", f"{simbolo} {tot_activos:,.2f}", "Recursos y bienes totales", "🏛️", "#2563eb")
render_kpi(k2, "Total Pasivos", f"{simbolo} {tot_pasivos:,.2f}", f"Endeudamiento: {(tot_pasivos/tot_activos*100):.1f}% de activos", "💳", "#dc2626")
render_kpi(k3, "Total Capital", f"{simbolo} {tot_capital:,.2f}", f"Patrimonio neto: {(tot_capital/tot_activos*100):.1f}% de activos", "🛡️", "#059669")

st.markdown("### 📈 Indicadores de Rentabilidad (Estado de Resultados)")
r1, r2, r3, r4 = st.columns(4)
render_kpi(r1, "Ingresos Totales", f"{simbolo} {tot_ingresos:,.2f}", "Ventas brutas del período", "💰", "#0284c7")
render_kpi(r2, "Costos Directos", f"{simbolo} {tot_costos:,.2f}", "Costo de ventas / servicios", "📉", "#ea580c")
render_kpi(r3, "Margen Bruto", f"{simbolo} {tot_margen:,.2f}", "Utilidad antes de gastos op.", "💵", "#16a34a")
render_kpi(r4, "% Margen Bruto", f"{pct_margen_global:.2f}%", "Meta saludable: ≥ 50.00%", "🎯", "#7c3aed")

st.divider()

# ==============================================================================
# 7. GRÁFICOS INTERACTIVOS (PLOTLY)
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
# 8. TABLAS FINANCIERAS CON ESTILO CONDICIONAL Y FORMATO PROFESIONAL
# ==============================================================================
tab1, tab2 = st.tabs(["📋 Tabla: Estado de Resultados", "🏛️ Tabla: Balance General"])

with tab1:
    st.subheader(f"Detalle de Ingresos, Costos y Márgenes ({moneda_vista})")
    
    df_tabla_er = df_er_filt[[
        "Mes", "Linea_Negocio", "Ingresos", "Costos", "Margen_Bruto", "Porcentaje_Margen", "Gastos_Operativos"
    ]].copy()

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
