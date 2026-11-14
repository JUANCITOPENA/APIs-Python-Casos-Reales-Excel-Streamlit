# Guía Paso a Paso: Lectura de Excel Financiero y Conversión a Dólares (USD) con Python

Esta guía documenta la segunda fase del proyecto: leer un archivo de Excel estructurado con estados financieros en Pesos Dominicanos (**DOP**), consultar una API en tiempo real para obtener la tasa de cambio del día y transformar todos los indicadores (Activos, Pasivos, Capital, Ingresos, Costos y Márgenes) a Dólares Estadounidenses (**USD**) utilizando **Pandas**.

---

## 1. Introducción: ¿Cómo integramos Excel con una API?

En el flujo de análisis de datos profesional, es común tener fuentes de datos estáticas o locales (como reportes contables en **Excel**) que necesitan enriquecerse con información externa dinámica (como tasas de cambio, inflación o precios de mercado desde una **API**).

En este script realizamos un proceso **ETL** (*Extract, Transform, Load*):
1. **Extracción (*Extract*):** Leemos las hojas `Balance_General` y `Estado_Resultados` del archivo `estados_financieros_rd.xlsx` y consultamos el endpoint JSON de la API de divisas mediante el verbo HTTP **`GET`**.
2. **Transformación (*Transform*):** Limpiamos filas de totales, recalculamos márgenes financieros directamente en memoria y aplicamos la tasa de conversión de `DOP` a `USD`.
3. **Carga / Visualización (*Load*):** Presentamos los resultados limpios y formateados en consola, dejando los *DataFrames* listos para ser exportados o mostrados en un dashboard con Streamlit.

### Nota técnica importante sobre fórmulas de Excel y `NaN`
Cuando un archivo `.xlsx` es generado automáticamente por código (sin haber sido abierto y guardado manualmente en Microsoft Excel), las celdas que contienen fórmulas (como `=C5-D5`) **no tienen guardado un valor en caché**. Si `pandas` intenta leer esas celdas directamente, devolverá `NaN` (*Not a Number*). Por ello, la mejor práctica en ingeniería de datos es **recalcular las columnas derivadas directamente en Pandas** a partir de los datos numéricos base.

---

## 2. Preparación del Entorno e Instalación de Librerías

Asegúrate de estar dentro de la carpeta de tu proyecto y con tu entorno virtual `(venv)` activo.

### Paso 1: Activar el entorno virtual (si aún no lo está)
* **Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
* **Windows (CMD):**
  ```cmd
  venv\Scripts\activate.bat
  ```
* **Mac / Linux:**
  ```bash
  source venv/bin/activate
  ```

### Paso 2: Instalar las librerías necesarias
Además de `requests` (para la API), necesitamos **`pandas`** (para manipular tablas de datos) y **`openpyxl`** (el motor que permite a Pandas leer archivos modernos `.xlsx`).

Ejecuta en tu terminal:
```bash
pip install pandas openpyxl requests
```

*(Nota: Asegúrate de que el archivo `estados_financieros_rd.xlsx` esté guardado dentro de la misma carpeta donde crearás tu script).*

---

## 3. Código Paso a Paso (Bien Comentado)

Crea un archivo llamado `estados_financieros_rd.py` en la carpeta de tu proyecto y pega el siguiente código:

```python
# ==============================================================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# ==============================================================================
import pandas as pd    # Librería principal para análisis y manipulación de tablas (DataFrames)
import requests        # Librería para realizar peticiones HTTP (GET) a la API de divisas

# ==============================================================================
# 2. CONSULTA A LA API DE DIVISAS (OBTENER TASA DOP -> USD)
# ==============================================================================
# Definimos dos URLs (principal en jsDelivr y respaldo en Cloudflare) para garantizar disponibilidad
urls = [
    "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/dop.json",
    "https://latest.currency-api.pages.dev/v1/currencies/dop.json",
]

tasa_dop_a_usd = None  # Variable donde guardaremos el factor de conversión

for url in urls:
    try:
        # Enviamos petición GET con un tiempo límite (timeout) de 10 segundos
        respuesta = requests.get(url, timeout=10)
        
        # Si el servidor responde con código 200 (OK), extraemos el JSON
        if respuesta.status_code == 200:
            datos_api = respuesta.json()
            # Extraemos cuántos dólares equivale 1 Peso Dominicano (ej. 0.01644)
            tasa_dop_a_usd = datos_api["dop"]["usd"]
            break  # Salimos del ciclo al obtener el dato con éxito
            
    except requests.exceptions.RequestException:
        print(f"Advertencia: No se pudo conectar a {url}. Probando respaldo...")

# ==============================================================================
# 3. LECTURA DEL EXCEL Y TRANSFORMACIÓN DE DATOS CON PANDAS
# ==============================================================================
if tasa_dop_a_usd:
    # Calculamos la tasa inversa solo para mostrarla de forma legible (ej. US$ 1 = RD$ 60.83)
    tasa_cambio_rd = 1 / tasa_dop_a_usd
    print(f"Conexión exitosa. Tasa del día: US$ 1 = RD$ {tasa_cambio_rd:,.2f}\n")

    archivo_excel = "estados_financieros_rd.xlsx"

    # --------------------------------------------------------------------------
    # A. PROCESAMIENTO DEL BALANCE GENERAL
    # --------------------------------------------------------------------------
    # header=3 indica a Pandas que los encabezados están en la fila 4 de Excel (índice 3)
    df_balance = pd.read_excel(archivo_excel, sheet_name="Balance_General", header=3)
    
    # Eliminamos filas vacías o filas de totales inferiores donde 'Codigo' sea nulo (NaN)
    df_balance = df_balance.dropna(subset=["Codigo"]).copy()

    # Creamos la nueva columna 'Monto_USD' multiplicando los pesos por la tasa y redondeando a 2 decimales
    df_balance["Monto_USD"] = (df_balance["Monto_DOP"] * tasa_dop_a_usd).round(2)

    # --------------------------------------------------------------------------
    # B. PROCESAMIENTO DEL ESTADO DE RESULTADOS
    # --------------------------------------------------------------------------
    df_resultados = pd.read_excel(archivo_excel, sheet_name="Estado_Resultados", header=3)
    
    # Filtramos para excluir la fila resumen de 'TOTAL' y quedarnos solo con los registros mensuales
    df_resultados = df_resultados[df_resultados["Mes"] != "TOTAL"].copy()

    # Recalculamos el Margen Bruto y el % de Margen directamente en Pandas
    # (Esto evita errores de valores NaN si Excel no tiene guardada la caché de sus fórmulas)
    df_resultados["Margen_Bruto_DOP"] = df_resultados["Ingresos_DOP"] - df_resultados["Costos_DOP"]
    df_resultados["Porcentaje_Margen"] = (
        (df_resultados["Margen_Bruto_DOP"] / df_resultados["Ingresos_DOP"]) * 100
    ).round(2)

    # Convertimos todas las métricas monetarias de DOP a USD
    df_resultados["Ingresos_USD"] = (df_resultados["Ingresos_DOP"] * tasa_dop_a_usd).round(2)
    df_resultados["Costos_USD"] = (df_resultados["Costos_DOP"] * tasa_dop_a_usd).round(2)
    df_resultados["Margen_Bruto_USD"] = (df_resultados["Margen_Bruto_DOP"] * tasa_dop_a_usd).round(2)
    df_resultados["Gastos_Operativos_USD"] = (df_resultados["Gastos_Operativos_DOP"] * tasa_dop_a_usd).round(2)

    # ==========================================================================
    # 4. PRESENTACIÓN DE RESULTADOS EN CONSOLA
    # ==========================================================================
    print("=" * 75)
    print("BALANCE GENERAL CONVERTIDO A DÓLARES (USD)")
    print("=" * 75)
    # Seleccionamos las columnas clave y ocultamos el índice numérico (index=False)
    cols_balance = ["Categoria", "Cuenta", "Monto_DOP", "Monto_USD"]
    print(df_balance[cols_balance].to_string(index=False))

    print("\n" + "=" * 75)
    print("ESTADO DE RESULTADOS - PRIMERAS 10 FILAS EN DÓLARES (USD)")
    print("=" * 75)
    cols_resultados = [
        "Mes", 
        "Linea_Negocio", 
        "Ingresos_USD", 
        "Costos_USD", 
        "Margen_Bruto_USD", 
        "Porcentaje_Margen"
    ]
    print(df_resultados[cols_resultados].head(10).to_string(index=False))

else:
    print("Error crítico: No se pudo obtener la tasa de cambio desde la API.")
```

---

## 4. Ejecución y Resultado Esperado

Con el entorno `(venv)` activo en tu terminal, ejecuta el script mediante:

```bash
python estados_financieros_rd.py
```

### Resultado en consola:
*(Nota: Los valores en USD variarán ligeramente dependiendo de la tasa de cambio vigente el día que ejecutes el programa).*

```text
Conexión exitosa. Tasa del día: US$ 1 = RD$ 60.83

===========================================================================
BALANCE GENERAL CONVERTIDO A DÓLARES (USD)
===========================================================================
Categoria                      Cuenta  Monto_DOP  Monto_USD
  Activos   Efectivo en Caja y Bancos    1850000   30414.56
  Activos Inversiones a Corto Plazo     950000   15618.29
  Activos Cuentas por Cobrar Clientes    2400000   39456.72
  Activos    Inventario de Mercancías    2100000   34524.63
  Activos  Propiedad, Planta y Equipo    4200000   69049.27
  Activos         Activos Intangibles    1000000   16440.31
  Pasivos   Cuentas por Pagar Prov.      1350000   22194.42
  Pasivos  Impuestos y Retenciones       450000    7398.14
  Pasivos Préstamos Bancarios C.P.       900000   14796.28
  Pasivos  Deuda Financiera L.P.        2500000   41100.78
  Capital     Capital Social Pagado     4500000   73981.41
  Capital         Reserva Legal          650000   10686.20
  Capital     Utilidades Acumuladas     1250000   20550.39
  Capital    Utilidad del Ejercicio      900000   14796.28

===========================================================================
ESTADO DE RESULTADOS - PRIMERAS 10 FILAS EN DÓLARES (USD)
===========================================================================
    Mes          Linea_Negocio  Ingresos_USD  Costos_USD  Margen_Bruto_USD  Porcentaje_Margen
2026-01  Software y Desarrollo      15179.55     4618.71          10560.84              69.57
2026-01 Consultoría BI y Datos       9969.10     3921.11           6047.99              60.67
2026-01      Licencias y Cloud       9090.57     4394.54           4696.03              51.66
2026-02  Software y Desarrollo      12964.58     4865.42           8099.16              62.47
2026-02 Consultoría BI y Datos       9447.87     3434.97           6012.90              63.64
2026-02      Licencias y Cloud      10397.97     4631.94           5766.03              55.45
2026-03  Software y Desarrollo      15623.91     5072.81          10551.10              67.53
2026-03 Consultoría BI y Datos      11926.18     4076.96           7849.22              65.82
2026-03      Licencias y Cloud      10964.61     4843.25           6121.36              55.83
2026-04  Software y Desarrollo      15129.07     5009.45          10119.62              66.89
```