import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA WEB
# ==========================================
st.set_page_config(page_title="Dashboard Ejecutivo de Hardware", layout="wide")

st.title("📊 Cuadro de Mando Integral - Analítica de E-Commerce & Hardware")
st.markdown("---")

# ==========================================
# 2. CARGA DE DATOS OPTIMIZADA
# ==========================================
@st.cache_data
def cargar_datos():
    # Carga el CSV con tus datos reales de tecnología
    return pd.read_csv("/home/jovyan/work/semanas/Semana 15/datos_hardware_dashboard.csv")

df = cargar_datos()

# ==========================================
# 3. CREACIÓN DE LAS PESTAÑAS (TABS)
# ==========================================
tab_est, tab_tac, tab_op = st.tabs([
    "📈 Nivel Estratégico (CEO)",
    "⚙️ Nivel Táctico (Gerente)",
    "🛠️ Nivel Operacional (Supervisor)"
])

# ==========================================
# PESTAÑA 1: NIVEL ESTRATÉGICO
# ==========================================
with tab_est:
    st.header("Concentración del Mercado por Marca")
    st.caption("Frecuencia: Mensual | Objetivo: Evaluar el posicionamiento de fabricantes en el retail")
    
    # Procesamiento rápido de porcentajes en Pandas
    total_equipos = len(df)
    df_est = df['marca'].value_counts().reset_index()
    df_est.columns = ['marca', 'Cantidad']
    df_est['Porcentaje'] = (df_est['Cantidad'] / total_equipos) * 100
    
    # Diseño en columnas de Streamlit
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric(label="Total Equipos Analizados", value=total_equipos)
        st.metric(
            label="Marca Líder", 
            value=df_est['marca'].iloc[0], 
            delta=f"{df_est['Porcentaje'].iloc[0]:.1f}% del catálogo"
        )
        st.dataframe(df_est, hide_index=True)
        
    with col2:
        fig, ax = plt.subplots(figsize=(8, 5))
        # Gráfico de barras horizontales limpio y sin amontonarse
        sns.barplot(
            x="Porcentaje", 
            y="marca", 
            data=df_est, 
            hue="marca", 
            palette="Blues_r", 
            legend=False, 
            ax=ax
        )
        
        # Agregar los porcentajes al lado de cada barra
        for barra in ax.patches:
            ancho = barra.get_width()
            if ancho > 0:
                ax.text(
                    ancho + 0.5, 
                    barra.get_y() + barra.get_height()/2, 
                    f'{ancho:.1f}%', 
                    va='center', 
                    ha='left', 
                    fontsize=9, 
                    weight='bold'
                )
                
        ax.set_xlabel("Participación (%)")
        ax.set_ylabel("Marca")
        sns.despine()
        st.pyplot(fig)


# ==========================================
# PESTAÑA 2: NIVEL TÁCTICO
# ==========================================
with tab_tac:
    st.header("Bandas de Competitividad: Precios Mínimos y Máximos por Tienda")
    st.caption("Frecuencia: Semanal | Objetivo: Diseñar estrategias de precios competitivos frente al retail")
    
    # Filtro interactivo multiselect en tiempo real
    tiendas_seleccionadas = st.multiselect(
        "Selecciona las Tiendas a Comparar:", 
        options=df['tienda'].unique(), 
        default=df['tienda'].unique()
    )
    
    df_filtrado_tiendas = df[df['tienda'].isin(tiendas_seleccionadas)]
    
    # Agrupación y cálculo de precios límites
    df_tac = df_filtrado_tiendas.groupby('tienda')['precio_numerico'].agg(['min', 'mean', 'max']).reset_index().sort_values(by='mean')
    
    if not df_tac.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Dibujar líneas de rango de precios
        ax.vlines(x=df_tac['tienda'], ymin=df_tac['min'], ymax=df_tac['max'], colors='#B0BEC5', alpha=0.7, linewidth=3)
        
        # Dibujar los puntos clave de precios
        ax.scatter(df_tac['tienda'], df_tac['mean'], color='#1A237E', s=120, zorder=3, label="Promedio")
        ax.scatter(df_tac['tienda'], df_tac['min'], color='#2E7D32', marker='^', s=80, zorder=3, label="Mínimo")
        ax.scatter(df_tac['tienda'], df_tac['max'], color='#C62828', marker='v', s=80, zorder=3, label="Máximo")
        
        # TRUCO: Formatear el eje Y como dinero con puntos reales ($1.500.000)
        formatter = ticker.FuncFormatter(lambda x, pos: f"${int(x):,}".replace(",", "."))
        ax.yaxis.set_major_formatter(formatter)
        
        ax.set_ylabel("Precio ($)")
        plt.xticks(rotation=35, ha='right')
        ax.legend()
        sns.despine()
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info("Por favor, selecciona al menos una tienda para visualizar las bandas de precios.")


# ==========================================
# PESTAÑA 3: NIVEL OPERACIONAL
# ==========================================
with tab_op:
    st.header("Distribución del Hardware según su Nivel de Gama")
    st.caption("Frecuencia: Diario / Tiempo Real | Objetivo: Monitorear el inventario según las predicciones de clústeres")
    
    df_op_base = df.copy()
    
    # CORRECCIÓN DE COLUMNA: Tu base de datos usa 'prediction_idx'
    if 'prediction_idx' in df_op_base.columns:
        # Pasamos a entero por seguridad y mapeamos al nombre real de la gama
        df_op_base['prediction_idx'] = df_op_base['prediction_idx'].astype(int)
        gama_map = {0: "Gama Baja-Inicial", 1: "Gama Baja", 2: "Gama Media", 3: "Gama Alta", 4: "Gama Premium"}
        df_op_base['gama_nombre'] = df_op_base['prediction_idx'].map(gama_map)
    else:
        # Resguardo en caso de cualquier cambio imprevisto en la columna
        df_op_base['gama_nombre'] = "Clasificación General"

    # Control interactivo: Slider dinámico operativo para filtrar por precio máximo en vivo
    precio_max_filtro = st.slider(
        "Ajustar Filtro Operativo de Precio Máximo ($):", 
        min_value=int(df['precio_numerico'].min()), 
        max_value=int(df['precio_numerico'].max()), 
        value=int(df['precio_numerico'].max() * 0.8),
        step=50000
    )
    
    # Filtrar según el movimiento del slider
    df_zona_alerta = df_op_base[df_op_base['precio_numerico'] > precio_max_filtro]
    
    st.warning(f"⚠️ Se han detectado {len(df_zona_alerta)} equipos en inventario que superan el límite operacional de precio.")
    
    # Agrupar para el gráfico de barras de las gamas
    df_conteos = df_op_base.groupby('gama_nombre')['precio_numerico'].count().reset_index()
    df_conteos.columns = ['gama_nombre', 'count']
    
    fig, ax = plt.subplots(figsize=(10, 5))
    barras = sns.barplot(
        x="count", 
        y="gama_nombre", 
        data=df_conteos, 
        palette="Purples_r", 
        hue="gama_nombre", 
        legend=False, 
        ax=ax
    )
    
    # Poner la cantidad exacta al lado de cada barra de gama
    for barra in ax.patches:
        cantidad = barra.get_width()
        if cantidad > 0:
            ax.text(
                cantidad + 1, 
                barra.get_y() + barra.get_height() / 2, 
                f'{int(cantidad)}', 
                va='center', 
                ha='left', 
                fontsize=10, 
                weight='bold'
            )
            
    ax.set_xlabel("Cantidad de Equipos")
    ax.set_ylabel("Gama del Hardware (Predicción)")
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig)
    
    # Mostrar la tabla de auditoría operativa abajo
    if len(df_zona_alerta) > 0:
        st.subheader("Lista Detallada de Equipos en Alerta de Precio:")
        
        # Seleccionar columnas y darles formato limpio de dinero
        df_tabla_visible = df_zona_alerta[['marca', 'tienda', 'procesador', 'ram', 'precio_numerico', 'gama_nombre']].copy()
        df_tabla_visible['precio_numerico'] = df_tabla_visible['precio_numerico'].apply(lambda x: f"${int(x):,}".replace(",", "."))
        
        st.dataframe(
            df_tabla_visible.sort_values(by='gama_nombre'), 
            hide_index=True
        )