"""
PARTE 2: Dashboard con Streamlit.
Ejecutar:  streamlit run app.py
"""
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Libros - Dashboard", page_icon="📚", layout="wide")


@st.cache_data  # evita recargar el CSV cada vez que tocas un filtro
def cargar_datos():
    return pd.read_csv("data/libros.csv", parse_dates=["fecha_scraping"])


df = cargar_datos()

st.title("📚 Dashboard de libros (Books to Scrape)")
st.write("Datos obtenidos con BeautifulSoup. Usa los filtros de la izquierda.")

# ---------- FILTROS (barra lateral) ----------
st.sidebar.header("Filtros")

categorias = sorted(df["categoria"].unique())
cat_elegidas = st.sidebar.multiselect("Categoría", categorias, default=categorias[:5])

precio_min, precio_max = float(df["precio"].min()), float(df["precio"].max())
rango_precio = st.sidebar.slider("Rango de precio (£)", precio_min, precio_max,
                                 (precio_min, precio_max))

rating_min = st.sidebar.slider("Rating mínimo (estrellas)", 1, 5, 1)
busqueda = st.sidebar.text_input("Buscar en el título")

# Aplicamos los filtros al DataFrame
filtrado = df[
    (df["categoria"].isin(cat_elegidas))
    & (df["precio"].between(*rango_precio))
    & (df["rating"] >= rating_min)
    & (df["titulo"].str.contains(busqueda, case=False, na=False))
]

if filtrado.empty:
    st.warning("No hay libros con esos filtros. Prueba a cambiarlos.")
    st.stop()

# ---------- MÉTRICAS ----------
c1, c2, c3 = st.columns(3)
c1.metric("Libros", len(filtrado))
c2.metric("Precio medio", f"£{filtrado['precio'].mean():.2f}")
c3.metric("Rating medio", f"{filtrado['rating'].mean():.2f} ⭐")

# ---------- TABLA ----------
st.subheader("Tabla de resultados")
st.dataframe(filtrado[["titulo", "categoria", "precio", "rating", "enlace"]],
             use_container_width=True)

# ---------- GRÁFICOS ----------
izq, der = st.columns(2)

with izq:
    st.subheader("Nº de libros por categoría")
    st.bar_chart(filtrado["categoria"].value_counts())

with der:
    st.subheader("Precio medio según el rating")
    st.bar_chart(filtrado.groupby("rating")["precio"].mean())

# ---------- ANÁLISIS CRÍTICO ----------
st.subheader("¿Influye el precio en la valoración?")
st.scatter_chart(filtrado, x="precio", y="rating")

if len(filtrado) > 1 and filtrado["rating"].nunique() > 1:
    corr = filtrado["precio"].corr(filtrado["rating"])
    st.write(f"**Correlación precio-rating: {corr:.2f}**")
    if abs(corr) < 0.2:
        st.info("La correlación es muy baja: el precio NO parece influir en la valoración.")
    elif corr > 0:
        st.info("Correlación positiva: los libros más caros tienden a tener mejor rating.")
    else:
        st.info("Correlación negativa: los libros más caros tienden a tener peor rating.")
