import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ------------------------------------------------------------
# Configuración de la página
# ------------------------------------------------------------
st.set_page_config(page_title="Dashboard E-commerce", layout="wide")
st.title(" Dashboard Ejecutivo – Monitoreo de Notebooks")
st.markdown("---")

# ------------------------------------------------------------
# Carga de datos (ajusta la ruta si es necesario)
# ------------------------------------------------------------
@st.cache_data
def cargar_datos():
    
    return pd.read_csv("datos_pc.csv")

df = cargar_datos()

# Aseguramos que precio_numerico sea numérico (por si acaso)
df['precio_numerico'] = pd.to_numeric(df['precio_numerico'], errors='coerce')

# ------------------------------------------------------------
# Pestañas de los tres niveles
# ------------------------------------------------------------
tab_est, tab_tac, tab_op = st.tabs([" Estratégico", " Táctico", "⚙ Operacional"])

# ==========================================
#  ESTRATÉGICO: Distribución de precios por marca
# ==========================================
with tab_est:
    st.header("Distribución de precios por fabricante")
    st.markdown("""
    **¿Qué decisión apoya?**  
    - Identificar marcas con precios compactos (líderes de segmento) vs. marcas con gran dispersión (cubren varias gamas).  
    - Detectar posibles errores de scraping (outliers extremos).
    """)

    # Ordenamos marcas por mediana de precio
    order = df.groupby('marca')['precio_numerico'].median().sort_values(ascending=False).index

    fig, ax = plt.subplots(figsize=(12, 7))
    sns.boxplot(data=df, x='precio_numerico', y='marca', order=order,
                palette='viridis', width=0.6, ax=ax)
    ax.set_title('Rango de precios por fabricante', fontweight='bold')
    ax.set_xlabel('Precio (CLP)')
    ax.set_ylabel('Marca')
    ax.grid(axis='x', alpha=0.4)
    st.pyplot(fig)

    # Métricas de contexto
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total de productos", len(df))
    with col2:
        st.metric("Precio promedio general", f"${df['precio_numerico'].mean():,.0f}")

# ==========================================
#  TÁCTICO: Índice de estandarización del hardware
# ==========================================
with tab_tac:
    st.header("Índice de estandarización del hardware")
    st.markdown("""
    **¿Qué decisión apoya?**  
    - Cuanto más alto el índice, más conviene estandarizar compras y logística.  
    - Si el índice es bajo, se necesita segmentar por configuración para no mezclar gamas.
    """)

    # Crear combinación hardware
    df['combo_hw'] = df['ram'].astype(str) + ' + ' + df['almacenamiento'].astype(str)
    combo_counts = df['combo_hw'].value_counts().head(10)
    combo_share = (combo_counts / len(df) * 100).round(2)

    df_combo = pd.DataFrame({
        'Combinación': combo_counts.index,
        'Cantidad': combo_counts.values,
        'Participación (%)': combo_share.values
    })

    # Índice: cobertura de los 5 combos más comunes
    top5_share = df_combo['Participación (%)'].head(5).sum()
    st.metric("Cobertura Top 5 combos", f"{top5_share:.1f}%",
              delta="Alta" if top5_share > 60 else "Media/Baja")

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(df_combo['Combinación'], df_combo['Participación (%)'], color='steelblue')
    ax.set_xlabel('Participación (%)')
    ax.set_title('Top 10 configuraciones de hardware más comunes', fontweight='bold')
    ax.invert_yaxis()
    for bar, pct in zip(bars, df_combo['Participación (%)']):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2, f'{pct}%', va='center')
    st.pyplot(fig)

# ==========================================
#  OPERACIONAL: Mapa de calor de precios tienda/marca
# ==========================================
with tab_op:
    st.header("Mapa de calor: Precio promedio por tienda y marca")
    st.markdown("""
    **¿Qué decisión apoya?**  
    - Identificar de inmediato en qué tienda cada marca es más cara o barata.  
    - Permite negociar con proveedores o elegir el canal de compra más conveniente.
    """)

    pivot = df.pivot_table(values='precio_numerico', index='marca', columns='tienda', aggfunc='mean')
    pivot['promedio_general'] = pivot.mean(axis=1)
    pivot = pivot.sort_values('promedio_general', ascending=False).drop('promedio_general', axis=1)

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(pivot, annot=True, fmt='.0f', cmap='YlOrRd', linewidths=.5,
                cbar_kws={'label': 'Precio promedio (CLP)'}, ax=ax)
    ax.set_title('Precio promedio por tienda y marca', fontweight='bold')
    ax.set_ylabel('Marca')
    ax.set_xlabel('Tienda')
    plt.xticks(rotation=45)
    st.pyplot(fig)