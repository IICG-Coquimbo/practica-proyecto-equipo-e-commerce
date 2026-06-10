import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Configuración de la página web
st.set_page_config(page_title="Dashboard E-commerce Ejecutivo", layout="wide")

st.title(" Cuadro de Mando Integral - Analítica E-commerce")
st.markdown("---")

# 2. Carga de datos optimizada
@st.cache_data
def cargar_datos():
    # Cambia la ruta a donde guardaste el CSV en el Paso 1
    return pd.read_csv("datos_notebooks_dashboard.csv")

df = cargar_datos()

# 3. Creación de las Pestañas (Tabs) por Nivel Organizacional
tab_est, tab_tac, tab_op = st.tabs([
    " Nivel Estratégico (CEO)", 
    " Nivel Táctico (Gerente)", 
    " Nivel Operacional (Supervisor)"
])

# ==========================================
# PESTAÑA 1: NIVEL ESTRATÉGICO
# ==========================================
with tab_est:
    st.header(" Concentración del Portafolio por Marca")
    st.caption("Frecuencia: Mensual | Objetivo: Evaluar monopolios de proveedores")
    
    # Procesamiento rápido en Pandas
    total_sku = len(df)
    df_est = df['marca'].value_counts().reset_index()
    df_est.columns = ['marca', 'Cantidad_notebooks_marca']
    df_est['Participacion'] = (df_est['Cantidad_notebooks_marca'] / total_sku) * 100
    
    # Diseño en columnas de Streamlit (Métricas clave arriba)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(label="Total Marcas en Catálogo", value=total_sku)
        st.metric(label="Marca Líder", value=df_est['marca'].iloc[0], delta=f"{df_est['Participacion'].iloc[0]:.1f}% de la góndola")
        st.dataframe(df_est, hide_index=True)
        
    with col2:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        sns.barplot(x="Participacion", y="marca", data=df_est, hue="marca", palette="Blues_r", legend=False, ax=ax)
        sns.despine(left=True, bottom=False)
        ax.set_xlabel("Participación (%)")
        st.pyplot(fig)


# ==========================================
# PESTAÑA 2: NIVEL TÁCTICO
# ==========================================
with tab_tac:
    st.header("Combinaciones de Hardware más Comunes")
    st.caption("Frecuencia: Semanal | Objetivo: Medir la concentración de la oferta en torno a configuraciones específicas de hardware para mitigar riesgos de obsolescencia")

    
    # Filtramos por las RAMs disponibles para que el usuario interactúe
    ram_disponibles = sorted(df['ram_numero'].unique())
    ram_seleccionadas = st.multiselect(
        "Filtrar por cantidad de memoria RAM:", 
        options=ram_disponibles, 
        default=ram_disponibles
    )

    # 2. Filtrar el DataFrame según la selección del usuario
    df_filtrado = df[df['ram_numero'].isin(ram_seleccionadas)]

    # 3. Crear la matriz de frecuencias para el Heatmap (Cruzar RAM vs Almacenamiento)
    # Esto cuenta de forma automática cuántos notebooks hay por cada combinación
    matriz_tactica = pd.crosstab(
        df_filtrado['ram_numero'], 
        df_filtrado['almacenamiento_numero']
    )

    # 4. Configurar el diseño del gráfico de Matplotlib/Seaborn
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.set_theme(style="white")

    # 5. Dibujar el Heatmap
    sns.heatmap(
        matriz_tactica, 
        annot=True,           # Muestra la cantidad exacta de productos dentro de cada cuadro
        fmt="d",              # Formato de número entero (de ahí la 'd')
        cmap="Purples",       # Paleta de morados (puedes cambiarla por "YlGnBu" o "viridis")
        linewidths=.5,        # Línea divisoria delgada entre los cuadros
        cbar_kws={'label': 'Cantidad de Productos'}, # Etiqueta de la barra lateral de color
        ax=ax
    )

    # 6. Estilizar etiquetas y títulos
    ax.set_title("Matriz de Concentración: RAM vs Almacenamiento", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Capacidad de Almacenamiento", fontsize=12)
    ax.set_ylabel("Memoria RAM", fontsize=12)
    
    # Rotar las etiquetas del eje X si son muy largas
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # 7. Renderizar el gráfico directamente en tu pestaña de Streamlit
    st.pyplot(fig)


# ==========================================
# PESTAÑA 3: NIVEL OPERACIONAL
# ==========================================
with tab_op:
    st.header("Índice de Concentración de Canales Competitivos")
    st.caption("Frecuencia: Tiempo Real | Objetivo: Monitorear la cuota de góndola digital y distribución de la oferta entre canales competidores.")
    
    # 1. Agrupar y calcular la participación por tienda en Pandas (basado en tus datos)
    # Contamos cuántos notebooks tiene cada tienda y calculamos su porcentaje
    df_tiendas = df['tienda'].value_counts().reset_index()
    df_tiendas.columns = ['tienda', 'Cantidad_notebooks_tienda']
    
    total_notebooks = df_tiendas['Cantidad_notebooks_tienda'].sum()
    df_tiendas['Participacion_Gondola_Pct'] = (df_tiendas['Cantidad_notebooks_tienda'] / total_notebooks) * 100
    
    # Ordenar de mayor a menor para el Top
    df_tiendas = df_tiendas.sort_values(by='Participacion_Gondola_Pct', ascending=False)

    # 2. Control interactivo para el Supervisor (Elegir cuántas tiendas ver en el Top)
    max_tiendas = len(df_tiendas)
    top_n = st.slider("Ajustar visualización del Top de Competidores:", min_value=3, max_value=max_tiendas, value=10, step=1)
    
    # Filtrar el DataFrame según el slider
    df_top_grafico = df_tiendas.head(top_n)
    
    # 3. Mensaje Operativo Dinámico (Saber cuántas tiendas dominan el mercado)
    # Sumamos la cuota del Top seleccionado para medir la concentración
    concentracion_top = df_top_grafico['Participacion_Gondola_Pct'].sum()
    st.info(f"📊 Concentración de Mercado: El Top {top_n} de los canales competidores concentra el **{concentracion_top:.2f}%** de la oferta digital total.")

    # 4. Diseño del Gráfico de Barras Horizontales con Degradado de Morados
    fig, ax = plt.subplots(figsize=(12, max(5, top_n * 0.4))) # Altura dinámica según la cantidad de tiendas
    sns.set_theme(style="whitegrid")

    # Creamos las barras horizontales
    ax = sns.barplot(
        data=df_top_grafico,
        x="Participacion_Gondola_Pct",
        y="tienda",
        hue="tienda",             # Mapeo explícito
        palette="Purples_r",      # Paleta de morados degradados como tu imagen
        legend=False,
        ax=ax
    )

    # 5. Añadir las etiquetas de porcentaje al final de cada barra
    for p in ax.patches:
        width = p.get_width()
        if width > 0: # Evitar errores con barras en 0
            ax.annotate(
                f'{width:.2f}%',
                (width + 0.3, p.get_y() + p.get_height() / 2),
                va='center', 
                ha='left', 
                fontsize=10, 
                fontweight='bold'
            )

    # 6. Estilizar el gráfico para que quede idéntico al tuyo
    ax.set_title("VISTA OPERATIVA: Distribución y Participación de Canales (% del Total de la Oferta Digital)", fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel("Cuota de Góndola Digital (%)", fontsize=11)
    ax.set_ylabel("Portal Competidor / Retailer", fontsize=11)
    
    # Dar margen extra a la derecha para que las etiquetas de porcentaje no se corten
    ax.set_xlim(0, df_top_grafico["Participacion_Gondola_Pct"].max() + 5)
    
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    
    # 7. Mostrar el gráfico en Streamlit
    st.pyplot(fig)
    