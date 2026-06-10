import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de la página
st.set_page_config(page_title="Dashboard Notebooks Chile", layout="wide")
st.title("Analítica de Mercado de Notebooks")
st.markdown("---")

# Carga de datos (cacheado)
@st.cache_data
def cargar_datos():
    return pd.read_csv("datos_notebooks_dashboard.csv")

df = cargar_datos()

# Crear pestañas
tab_est, tab_tac, tab_op = st.tabs([
    "📊 Nivel Estratégico (CEO)",
    "📈 Nivel Táctico (Gerente)",
    "🔔 Nivel Operacional (Supervisor)"
])

# ===========================================
# PESTAÑA 1: ESTRATÉGICO
# ===========================================
with tab_est:
    st.header("Concentración del Mercado y Precios por Fabricante")
    st.caption("Frecuencia: Mensual | Objetivo: Evaluar monopolios y posicionamiento de precios")

    # 1. Participación por marca
    total = len(df)
    df_est = df['marca'].value_counts().reset_index()
    df_est.columns = ['marca', 'Cantidad']
    df_est['Participacion'] = (df_est['Cantidad'] / total) * 100

    # Métricas principales
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total productos en catálogo", total)
        st.metric("Fabricante líder", df_est.iloc[0]['marca'],
                  delta=f"{df_est.iloc[0]['Participacion']:.1f}% del mercado")
        st.dataframe(df_est, hide_index=True)

    with col2:
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(data=df_est, x="Participacion", y="marca", hue="marca",
                    palette="Blues_r", legend=False, ax=ax)
        ax.set_xlabel("Participación (%)")
        ax.set_title("Participación por fabricante")
        st.pyplot(fig)

    # 2. Precio promedio por marca
    df_precio = df.groupby('marca')['precio_numerico'].mean().sort_values(ascending=False).reset_index()
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    sns.barplot(data=df_precio, x="precio_numerico", y="marca", hue="marca",
                palette="Reds_r", legend=False, ax=ax2)
    ax2.set_xlabel("Precio promedio (CLP)")
    ax2.set_title("Precio promedio por fabricante")
    st.pyplot(fig2)

    # 3. Rango de precios por tienda
    df_rango = df.groupby('tienda')['precio_numerico'].agg(['min', 'max']).reset_index()
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    for _, row in df_rango.iterrows():
        ax3.plot([row['min'], row['max']], [row['tienda'], row['tienda']], 'o-', color='gray')
    ax3.scatter(df_rango['min'], df_rango['tienda'], color='green', label='Mínimo', zorder=3)
    ax3.scatter(df_rango['max'], df_rango['tienda'], color='red', label='Máximo', zorder=3)
    ax3.set_xlabel("Precio (CLP)")
    ax3.set_title("Rango de precios por tienda")
    ax3.legend()
    st.pyplot(fig3)

# ===========================================
# PESTAÑA 2: TÁCTICO
# ===========================================
with tab_tac:
    st.header("Volatilidad de Precios y Segmentación de Gamas")
    st.caption("Frecuencia: Semanal | Objetivo: Diseñar estrategias de precios")

    # Filtro interactivo por marca (para el gráfico de bandas)
    marcas_seleccionadas = st.multiselect(
        "Filtrar marcas para el análisis de bandas:",
        options=df['marca'].unique(),
        default=df['marca'].unique()
    )
    df_filtrado = df[df['marca'].isin(marcas_seleccionadas)]

    # Cálculo de min, mean, max por marca
    df_bandas = df_filtrado.groupby('marca')['precio_numerico'].agg(['min', 'mean', 'max']).reset_index()
    df_bandas = df_bandas.sort_values('mean')

    # Gráfico de bandas (líneas verticales con puntos)
    fig_bandas, ax_bandas = plt.subplots(figsize=(12, 6))
    ax_bandas.vlines(x=df_bandas['marca'], ymin=df_bandas['min'], ymax=df_bandas['max'],
                     colors='lightgray', linewidth=3)
    ax_bandas.scatter(df_bandas['marca'], df_bandas['mean'], color='navy', s=100, label='Promedio', zorder=3)
    ax_bandas.scatter(df_bandas['marca'], df_bandas['min'], color='green', marker='^', s=80, label='Mínimo', zorder=3)
    ax_bandas.scatter(df_bandas['marca'], df_bandas['max'], color='red', marker='v', s=80, label='Máximo', zorder=3)
    ax_bandas.set_ylabel("Precio (CLP)")
    plt.xticks(rotation=45, ha='right')
    ax_bandas.legend()
    sns.despine()
    st.pyplot(fig_bandas)

    # Segmentación de clusters (K‑Means)
    if 'prediction' in df.columns:
        st.subheader("Segmentación de gamas (K‑Means)")
        fig_clust, ax_clust = plt.subplots(figsize=(10, 6))
        sns.scatterplot(data=df, x="ram_numero", y="precio_numerico",
                        hue="prediction", palette="Set2", alpha=0.6, ax=ax_clust)
        ax_clust.set_xlabel("RAM (GB)")
        ax_clust.set_ylabel("Precio (CLP)")
        ax_clust.set_title("RAM vs Precio por cluster")
        st.pyplot(fig_clust)
    else:
        st.warning("No se encontró la columna 'prediction' (clusters K‑Means) en los datos.")

# ===========================================
# PESTAÑA 3: OPERACIONAL
# ===========================================
with tab_op:
    st.header("Alertas de Precios y Concentración de Canales")
    st.caption("Frecuencia: Diario / Tiempo Real | Objetivo: Detectar oportunidades y riesgos")

    # 1. Concentración de canales (tiendas)
    df_canales = df['tienda'].value_counts().reset_index()
    df_canales.columns = ['tienda', 'Cantidad']
    df_canales['Participacion'] = (df_canales['Cantidad'] / total) * 100

    fig_canales, ax_canales = plt.subplots(figsize=(10, 5))
    sns.barplot(data=df_canales, x="Participacion", y="tienda", hue="tienda",
                palette="Greens_r", legend=False, ax=ax_canales)
    ax_canales.set_xlabel("Participación en el catálogo (%)")
    ax_canales.set_title("Concentración de canales")
    st.pyplot(fig_canales)

    # 2. Outliers de precio por marca (IQR)
    # Calcular Q1, Q3, IQR por marca
    def detect_outliers_iqr(group):
        Q1 = group.quantile(0.25)
        Q3 = group.quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        return group[(group < lower) | (group > upper)]
    outliers = df.groupby('marca')['precio_numerico'].apply(detect_outliers_iqr).reset_index(level=0, drop=True)
    df_outliers = df[df['precio_numerico'].isin(outliers)]

    st.warning(f"Se detectaron {len(df_outliers)} precios atípicos (outliers) por marca.")
    if not df_outliers.empty:
        fig_out, ax_out = plt.subplots(figsize=(10, 6))
        # Todos los puntos (gris)
        ax_out.scatter(df['ram_numero'], df['precio_numerico'], alpha=0.4, color='gray', label='Productos normales')
        # Outliers (rojo)
        ax_out.scatter(df_outliers['ram_numero'], df_outliers['precio_numerico'],
                       color='crimson', s=80, edgecolor='black', label='Outliers de precio')
        ax_out.set_xlabel("RAM (GB)")
        ax_out.set_ylabel("Precio (CLP)")
        ax_out.set_title("Detección de outliers de precio (método IQR)")
        ax_out.legend()
        st.pyplot(fig_out)
    else:
        st.success("No se encontraron outliers de precio.")