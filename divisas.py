import requests

# URL correcta de la API gratuita de divisas (con respaldo en Cloudflare)
urls = [
    "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/dop.json",
    "https://latest.currency-api.pages.dev/v1/currencies/dop.json",
]

datos = None
for url in urls:
    try:
        respuesta = requests.get(url, timeout=10)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            break
    except requests.exceptions.RequestException as e:
        print(f"No se pudo conectar a {url}, intentando respaldo...")

if datos:
    tasas = datos["dop"]

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

    # Calcular cuánto vale 1 unidad de cada moneda en Pesos Dominicanos
    tabla = []
    for codigo, nombre, simbolo in monedas:
        if codigo in tasas and tasas[codigo] > 0:
            cambio_rd = 1 / tasas[codigo]
            tabla.append((nombre, f"{simbolo}1", cambio_rd))

    # Ordenar de mayor a menor según el valor en RD$ (índice 2 de la tupla)
    tabla.sort(key=lambda x: x[2], reverse=True)

    # Imprimir la tabla
    print(f"{'Moneda':<22} | {'Valor Base':<10} | {'Cambio a Peso Dominicano'}")
    print("-" * 62)
    for nombre, unidad, cambio_rd in tabla:
        print(f"{nombre:<22} | {unidad:<10} | RD$ {cambio_rd:,.2f}")
else:
    print("Error: No se pudo conectar con ninguno de los servidores de divisas.")