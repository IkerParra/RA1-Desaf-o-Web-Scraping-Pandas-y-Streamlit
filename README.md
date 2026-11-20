# Práctica Web Scraping + Streamlit

Scraping de https://books.toscrape.com (web de prácticas que permite scraping) con BeautifulSoup,
limpieza con Pandas y dashboard interactivo con Streamlit.

## Instalación
    python -m venv .venv
    .venv\Scripts\activate        (Windows)
    pip install -r requirements.txt

## Uso
1. `python scraper.py`      -> genera data/libros.csv y data/categorias.csv
2. `streamlit run app.py`   -> abre el dashboard en el navegador

## Buenas prácticas aplicadas
- Se comprueba robots.txt
- User-Agent propio
- Pausa de 1 s entre peticiones (time.sleep)
- Limpieza de datos en Python (precio -> float, rating -> int, fecha -> datetime)
