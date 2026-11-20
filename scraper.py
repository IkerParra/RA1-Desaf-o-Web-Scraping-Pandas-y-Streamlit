"""
PARTE 1: Web scraping de https://books.toscrape.com con BeautifulSoup.
Guarda los resultados en data/libros.csv y data/categorias.csv

Ejecutar:  python scraper.py
"""
import re
import time
from datetime import date
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
HEADERS = {"User-Agent": "Practica-DAM-Scraping/1.0 (alumno 2DAM, uso educativo)"}
PAUSA = 1  # segundos entre peticiones para no saturar el servidor

# En la web el rating viene como palabra ("Three"); lo pasamos a número
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def comprobar_robots():
    """Mira el robots.txt para ver si podemos scrapear la web."""
    rp = RobotFileParser()
    rp.set_url(urljoin(BASE_URL, "robots.txt"))
    try:
        rp.read()
        permitido = rp.can_fetch(HEADERS["User-Agent"], BASE_URL)
    except Exception:
        permitido = True  # si no hay robots.txt, no hay restricciones
    print(f"robots.txt -> scraping permitido: {permitido}")
    return permitido


def obtener_soup(url):
    """Descarga una URL (con pausa) y devuelve el HTML ya 'parseado'."""
    time.sleep(PAUSA)
    respuesta = requests.get(url, headers=HEADERS, timeout=10)
    respuesta.raise_for_status()      # lanza error si la web responde 404, 500...
    respuesta.encoding = "utf-8"      # así el símbolo £ se lee bien
    return BeautifulSoup(respuesta.text, "html.parser")


def obtener_categorias():
    """Devuelve una lista de (nombre, url) con todas las categorías."""
    soup = obtener_soup(BASE_URL)
    enlaces = soup.select("div.side_categories ul li ul li a")
    return [(a.get_text(strip=True), urljoin(BASE_URL, a["href"])) for a in enlaces]


def limpiar_precio(texto):
    """'£51.77' -> 51.77 (quitamos todo lo que no sea número o punto)."""
    return float(re.sub(r"[^\d.]", "", texto))


def scrapear_categoria(nombre, url):
    """Recorre todas las páginas de una categoría y devuelve una lista de libros."""
    libros = []
    while url:  # mientras haya página siguiente
        soup = obtener_soup(url)
        for libro in soup.select("article.product_pod"):
            clase_rating = libro.select_one("p.star-rating")["class"][1]  # ['star-rating','Three']
            libros.append({
                "titulo": libro.h3.a["title"],
                "precio": limpiar_precio(libro.select_one("p.price_color").text),
                "rating": RATINGS[clase_rating],
                "disponibilidad": libro.select_one("p.availability").get_text(strip=True),
                "categoria": nombre,
                "enlace": urljoin(url, libro.h3.a["href"]),
                "imagen": urljoin(url, libro.img["src"]),
                "fecha_scraping": date.today().isoformat(),
            })
        siguiente = soup.select_one("li.next a")
        url = urljoin(url, siguiente["href"]) if siguiente else None
    return libros


def main():
    if not comprobar_robots():
        print("El robots.txt no permite el scraping. Paro.")
        return

    categorias = obtener_categorias()
    print(f"{len(categorias)} categorías encontradas")

    todos = []
    for i, (nombre, url) in enumerate(categorias, start=1):
        print(f"[{i}/{len(categorias)}] {nombre}")
        todos.extend(scrapear_categoria(nombre, url))

    # --- Limpieza y guardado con Pandas ---
    df = pd.DataFrame(todos)
    df["fecha_scraping"] = pd.to_datetime(df["fecha_scraping"])
    df = df.drop_duplicates(subset="enlace")

    # Segundo CSV: resumen por categoría
    resumen = (df.groupby("categoria")
                 .agg(num_libros=("titulo", "count"),
                      precio_medio=("precio", "mean"),
                      rating_medio=("rating", "mean"))
                 .round(2)
                 .reset_index())

    df.to_csv("data/libros.csv", index=False, encoding="utf-8")
    resumen.to_csv("data/categorias.csv", index=False, encoding="utf-8")
    print(f"Listo: {len(df)} libros guardados en data/libros.csv")


if __name__ == "__main__":
    main()
