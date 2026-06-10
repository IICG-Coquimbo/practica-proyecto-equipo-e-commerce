import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Configuración de la página web
st.set_page_config(page_title="Dashboard Notebooks Ejecutivo", layout="wide")

st.title("Analítica de computadores")
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
    st.header(" Concentración de computadores por Marca")
    st.caption("Frecuencia: Mensual | Objetivo: Evaluar monopolios de fabricantes")
    
    # Procesamiento rápido en Pandas
    total = len(df)
    df_est = df['marca'].value_counts().reset_index()
    df_est.columns = ['marca', 'Cantidad de notebooks']
    df_est['Participacion'] = (df_est['Cantidad de notebooks'] / total) * 100
    
    # Diseño en columnas de Streamlit (Métricas clave arriba)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(label="Total computadores en venta por las tiendas analizadas", value=total)
        st.metric(label="Fabricante más frecuente", value=df_est['marca'].iloc[0], delta=f"{df_est['Participacion'].iloc[0]:.4f}% de la góndola")
        st.dataframe(df_est, hide_index=True)
        
    with col2:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        sns.barplot(x="Participacion", y="marca", data=df_est, hue="marca", palette="magma", legend=False, ax=ax)
        sns.despine(left=True, bottom=False)
        ax.set_xlabel("Participación (%)")
        st.pyplot(fig)

# ==========================================
# PESTAÑA 2: NIVEL TÁCTICO
# ==========================================
with tab_tac:
    st.header(" Volatilidad de Precios")
    st.caption("Frecuencia: Semanal | Objetivo: Diseñar estrategias de precios")
    
    # Filtro interactivo en tiempo real (¡El poder de Streamlit!)
    marcas_seleccionadas = st.multiselect("Filtrar Marcas de fabricantes:", options=df['marca'].unique(), default=df['marca'].unique())
    
    df_filtrado = df[df['marca'].isin(marcas_seleccionadas)]
    
    df_tac = df_filtrado.groupby('marca')['precio_numerico'].agg(['min', 'mean', 'max']).reset_index().sort_values(by='mean')
    
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.vlines(x=df_tac['marca'], ymin=df_tac['min'], ymax=df_tac['max'], colors='#B0BEC5', alpha=0.7, linewidth=3)
    ax.scatter(df_tac['marca'], df_tac['mean'], color='#1A237E', s=120, zorder=3, label="Promedio")
    ax.scatter(df_tac['marca'], df_tac['min'], color='#2E7D32', marker='^', s=80, zorder=3, label="Mínimo")
    ax.scatter(df_tac['marca'], df_tac['max'], color='#C62828', marker='v', s=80, zorder=3, label="Máximo")
    ax.set_ylabel("Precio ($)")
    plt.xticks(rotation=25, ha='right')
    ax.legend()
    sns.despine(left=True)
    st.pyplot(fig)

# ==========================================
# PESTAÑA 3: NIVEL OPERACIONAL
# ==========================================
with tab_op:
    st.header(" Matriz de Alertas de Precios Bajo Umbral")
    st.caption("Frecuencia: Diario / Tiempo Real | Objetivo: Detectar oportunidades de mercado para ofertas relámpago")
    
    # 1. Slider para ajustar el umbral de precio en tiempo real
    umbral_precio = st.slider("Ajustar Umbral de Precio ($):", min_value=50000, max_value=500000, value=150000, step=10000)
    
    df_op = df.copy()
    # Aseguramos que precio_numerico sea numérico para el filtro
    df_op['precio_numerico'] = pd.to_numeric(df_op['precio_numerico'], errors='coerce')
    alertas = df_op[df_op['precio_numerico'] < umbral_precio]
    
    st.warning(f"Se han detectado {len(alertas)} productos con precios por debajo de ${umbral_precio:,}")
    
    if len(alertas) > 0:
        # Calculamos la altura dinámica: al menos 400px, y sumamos 20px por cada producto
        altura_dinamica = max(400, len(alertas) * 30)
        
        fig, ax = plt.subplots(figsize=(10, altura_dinamica / 80)) # Ajuste de proporción
        
        sns.barplot(x="precio_numerico", y="identificador", data=alertas.sort_values("precio_numerico"), 
                    palette="Reds_r", hue="identificador", legend=False, ax=ax)
        
        ax.set_xlabel("Precio ($)")
        ax.set_ylabel("Producto")
        sns.despine(left=True)
        
        # Guardamos en un contenedor de Streamlit para que no se desborde
        st.pyplot(fig)
        
        # Tabla interactiva
        st.subheader("Detalle de Productos en Alerta:")
        st.dataframe(alertas[['identificador', 'tienda', 'precio_numerico']], hide_index=True)
    else:
        st.success("No hay productos bajo ese umbral")
