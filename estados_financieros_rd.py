import pandas as pd
import requests

# 1. Obtener la tasa de DOP a USD desde la API
urls = [
    "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/dop.json",
    "https://latest.currency-api.pages.dev/v1/currencies/dop.json",
]

tasa_dop_a_usd = None
for url in urls:
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            tasa_dop_a_usd = res.json()["dop"]["usd"]
            break
    except requests.exceptions.RequestException:
        continue

if tasa_dop_a_usd:
    tasa_cambio_rd = 1 / tasa_dop_a_usd
    print(f"Tasa actual: US$ 1 = RD$ {tasa_cambio_rd:,.2f}\n")

    archivo = "estados_financieros_rd.xlsx"

    # 2. Leer Balance General
    df_balance = pd.read_excel(archivo, sheet_name="Balance_General", header=3).dropna(subset=["Codigo"])
    df_balance["Monto_USD"] = (df_balance["Monto_DOP"] * tasa_dop_a_usd).round(2)

    # 3. Leer Estado de Resultados y recalcular márgenes en Pandas (evita los NaN de fórmulas sin caché)
    df_resultados = pd.read_excel(archivo, sheet_name="Estado_Resultados", header=3)
    df_resultados = df_resultados[df_resultados["Mes"] != "TOTAL"].copy()

    df_resultados["Margen_Bruto_DOP"] = df_resultados["Ingresos_DOP"] - df_resultados["Costos_DOP"]
    df_resultados["Porcentaje_Margen"] = (df_resultados["Margen_Bruto_DOP"] / df_resultados["Ingresos_DOP"]) * 100

    # 4. Convertir columnas financieras a USD
    df_resultados["Ingresos_USD"] = (df_resultados["Ingresos_DOP"] * tasa_dop_a_usd).round(2)
    df_resultados["Costos_USD"] = (df_resultados["Costos_DOP"] * tasa_dop_a_usd).round(2)
    df_resultados["Margen_Bruto_USD"] = (df_resultados["Margen_Bruto_DOP"] * tasa_dop_a_usd).round(2)
    df_resultados["Gastos_Operativos_USD"] = (df_resultados["Gastos_Operativos_DOP"] * tasa_dop_a_usd).round(2)
    df_resultados["Porcentaje_Margen"] = df_resultados["Porcentaje_Margen"].round(2)

    print("=== BALANCE GENERAL (EN USD) ===")
    print(df_balance[["Categoria", "Cuenta", "Monto_DOP", "Monto_USD"]].to_string(index=False))

    print("\n=== ESTADO DE RESULTADOS (PRIMERAS 10 FILAS EN USD) ===")
    cols_mostrar = ["Mes", "Linea_Negocio", "Ingresos_USD", "Costos_USD", "Margen_Bruto_USD", "Porcentaje_Margen"]
    print(df_resultados[cols_mostrar].head(10).to_string(index=False))
else:
    print("No se pudo obtener la tasa de cambio de la API.")