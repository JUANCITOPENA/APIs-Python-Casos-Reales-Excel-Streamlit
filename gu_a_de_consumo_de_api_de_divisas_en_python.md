# Guía Paso a Paso: Consumo de API de Divisas con Python

Esta guía documenta cómo obtener tasas de cambio en tiempo real utilizando Python y una API gratuita, preparando el entorno de desarrollo desde cero hasta la visualización de los datos en consola.

---

## 1. Introducción: ¿Qué significa consumir una API?

Una **API** (*Application Programming Interface* o Interfaz de Programación de Aplicaciones) es un puente de comunicación que permite que dos programas diferentes intercambien información de manera estructurada.

**Consumir una API** significa que nuestro programa en Python actúa como un "cliente" que le pide datos a un servidor externo a través de internet. En lugar de descargar una página web diseñada para humanos (con colores y botones), nuestro código recibe los datos en crudo (generalmente en formato **JSON**, muy similar a los diccionarios de Python) para procesarlos, calcularlos o mostrarlos en un dashboard.

### ¿Qué API utilizamos en este proyecto?
Utilizamos **Currency API** (`@fawazahmed0/currency-api`), un servicio gratuito, de código abierto y sin límites de peticiones (*rate limits*) ni necesidad de claves secretas (*API Keys*). 
* Está alojada en redes de distribución global (**CDN** como *jsDelivr* y *Cloudflare*), lo que garantiza alta velocidad y disponibilidad.
* Toma como moneda base el **Peso Dominicano (`dop`)** y devuelve su equivalencia frente a más de 150 divisas mundiales y criptomonedas.

### ¿Qué verbo HTTP usamos aquí?
Para comunicarnos con la API utilizamos el protocolo HTTP y el verbo **`GET`**.
* **`GET`**: Se utiliza exclusivamente para **consultar y obtener información** desde un servidor, sin modificar ni enviar datos sensibles. En nuestro código, esto se ejecuta mediante la función `requests.get(url)`.

---

## 2. Preparación del Entorno de Trabajo

Es una buena práctica aislar las librerías de cada proyecto utilizando un entorno virtual para evitar conflictos de versiones en tu computadora.

### Paso 1: Crear el entorno virtual
Abre la terminal (PowerShell o CMD en Windows, o Terminal en Mac/Linux) dentro de la carpeta de tu proyecto y ejecuta:

```bash
python -m venv venv
```
*(Esto creará una carpeta llamada `venv` que contendrá una instalación limpia de Python).*

### Paso 2: Activar el entorno virtual
Debes activar el entorno antes de instalar librerías o ejecutar el script:

* **En Windows (PowerShell):**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
  *(Nota: Si PowerShell bloquea la ejecución por políticas de seguridad, ejecuta primero `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` y vuelve a intentar).*

* **En Windows (CMD):**
  ```cmd
  venv\Scripts\activate.bat
  ```

* **En Mac / Linux:**
  ```bash
  source venv/bin/activate
  ```

Sabrás que está activo porque verás `(venv)` al inicio de la línea de comandos.

### Paso 3: Instalar dependencias
Para este script solo necesitamos la librería **`requests`**, que es el estándar en Python para realizar peticiones HTTP a APIs. Instálala ejecutando:

```bash
pip install requests
```

---

## 3. Código Paso a Paso (Bien Comentado)

Crea un archivo llamado `divisas.py` en tu carpeta de proyecto y pega el siguiente código:

```python
# 1. IMPORTACIÓN DE LIBRERÍAS
# 'requests' permite hacer peticiones HTTP (como GET) a servidores en internet.
import requests

# 2. DEFINICIÓN DE ENDPOINTS (URLs DE LA API)
# Usamos una lista con dos URLs: la principal en jsDelivr y un respaldo en Cloudflare.
# Ambas devuelven un archivo JSON con el Peso Dominicano ('dop') como moneda base.
urls = [
    "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/dop.json",
    "https://latest.currency-api.pages.dev/v1/currencies/dop.json",
]

# 3. PETICIÓN HTTP (VERBO GET) Y MANEJO DE ERRORES
datos = None  # Variable para guardar la respuesta exitosa

for url in urls:
    try:
        # Enviamos una petición GET esperando máximo 10 segundos por respuesta
        respuesta = requests.get(url, timeout=10)

        # El código de estado 200 indica que la petición fue exitosa (OK)
        if respuesta.status_code == 200:
            # Convertimos el texto JSON recibido en un diccionario de Python
            datos = respuesta.json()
            break  # Salimos del bucle porque ya obtuvimos los datos

    except requests.exceptions.RequestException:
        # Si falla la conexión o se agota el tiempo, pasamos a la siguiente URL
        print(f"No se pudo conectar a {url}, intentando servidor de respaldo...")

# 4. PROCESAMIENTO Y CÁLCULO DE DATOS
if datos:
    # Extraemos el diccionario interno correspondiente a las tasas del 'dop'
    tasas = datos["dop"]

    # Definimos una lista de tuplas con las 10 divisas a consultar:
    # Estructura: (código_api, Nombre_Legible, Símbolo)
    monedas = [
        ("gbp", "Libra Esterlina", "£"),
        ("chf", "Franco Suizo", "CHF "),
        ("eur", "Euro", "€"),
        ("usd", "Dólar Estadounidense", "US$"),
        ("sgd", "Dólar de Singapur", "S$"),
        ("cad", "Dólar Canadiense", "CA$"),
        ("aud", "Dólar Australiano", "A$"),
        ("cny", "Yuan Chino", "¥"),
        ("mxn", "Peso Mexicano", "MX$"),
        ("jpy", "Yen Japonés", "¥"),
    ]

    tabla = []  # Lista donde almacenaremos los resultados calculados

    for codigo, nombre, simbolo in monedas:
        # Verificamos que la moneda exista en la API y su tasa sea mayor a 0
        if codigo in tasas and tasas[codigo] > 0:
            # La API dice cuánto vale 1 DOP en moneda extranjera (ej. 1 DOP = 0.016 USD).
            # Para saber cuánto vale 1 unidad extranjera en DOP, dividimos 1 entre la tasa.
            cambio_rd = 1 / tasas[codigo]

            # Guardamos el resultado formateado en nuestra lista
            tabla.append((nombre, f"{simbolo}1", cambio_rd))

    # 5. ORDENAMIENTO DE RESULTADOS
    # Ordenamos la lista de mayor a menor (reverse=True) usando el índice [2] (cambio_rd)
    tabla.sort(key=lambda x: x[2], reverse=True)

    # 6. PRESENTACIÓN EN CONSOLA
    # Imprimimos los encabezados alineados con espacios fijos (<22 y <10)
    print(f"{'Moneda':<22} | {'Valor Base':<10} | {'Cambio a Peso Dominicano'}")
    print("-" * 62)

    # Recorremos la tabla ordenada e imprimimos cada fila con formato de moneda (, y 2 decimales)
    for nombre, unidad, cambio_rd in tabla:
        print(f"{nombre:<22} | {unidad:<10} | RD$ {cambio_rd:,.2f}")

else:
    # Mensaje de respaldo si ningún servidor respondió
    print("Error: No se pudo conectar con ninguno de los servidores de divisas.")
```

---

## 4. Ejecución y Resultado Esperado

Para ejecutar el script, asegúrate de tener el entorno `(venv)` activo y escribe en la terminal:

```bash
python divisas.py
```

### Resultado en consola:
*(Nota: Los valores exactos variarán según la cotización del día en que ejecutes el código).*

```text
Moneda                 | Valor Base | Cambio a Peso Dominicano
--------------------------------------------------------------
Libra Esterlina        | £1         | RD$ 78.45
Franco Suizo           | CHF 1      | RD$ 70.12
Euro                   | €1         | RD$ 65.80
Dólar Estadounidense   | US$1       | RD$ 60.50
Dólar de Singapur      | S$1        | RD$ 45.10
Dólar Canadiense       | CA$1       | RD$ 43.25
Dólar Australiano      | A$1        | RD$ 39.80
Yuan Chino             | ¥1         | RD$ 8.35
Peso Mexicano          | MX$1       | RD$ 3.02
Yen Japonés            | ¥1         | RD$ 0.39
```