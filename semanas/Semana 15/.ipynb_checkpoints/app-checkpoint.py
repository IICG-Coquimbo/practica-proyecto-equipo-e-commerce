import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA WEB
# ==========================================
st.set_page_config(page_title="Dashboard Ejecutivo de Portafolio", layout="wide")

st.title("📊 Cuadro de Mando Integral - Analítica Comercial de Notebooks")
st.markdown("---")

# ==========================================
# 2. CARGA DE DATOS
# ==========================================
@st.cache_data
def cargar_datos():
    return pd.read_csv("datos_practica.csv")

try:
    df = cargar_datos()
except FileNotFoundError:
    st.error("⚠️ No se encontró el archivo 'datos_practica.csv'. Por favor, asegúrate de colocarlo en la misma carpeta que este script.")
    st.stop()

# ==========================================
# 3. CREACIÓN DE LAS PESTAÑAS (TABS)
# ==========================================
tab_est, tab_tac, tab_op = st.tabs([
    "📈 Nivel Estratégico (CEO)", 
    "🎯 Nivel Táctico (Gerente)", 
    "⚙️ Nivel Operacional (Supervisor)"
])

# ==========================================
# PESTAÑA 1: NIVEL ESTRATÉGICO
# ==========================================
with tab_est:
    st.header("Concentración del Portafolio de Notebooks por Marca")
    st.caption("Frecuencia: Mensual | Objetivo: Evaluar la dependencia y volumen de fabricantes en el catálogo")
    
    # Procesamiento de la participación de marcas
    total_sku = len(df)
    df_est = df['marca'].value_counts().reset_index()
    df_est.columns = ['marca', 'Cantidad_SKUs']
    df_est['Participacion'] = (df_est['Cantidad_SKUs'] / total_sku) * 100
    
    # Diseño en columnas (Métricas a la izquierda, gráfico a la derecha)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(label="Total SKUs en Catálogo", value=f"{total_sku} Equipos")
        marca_lider = df_est['marca'].iloc[0]
        part_lider = df_est['Participacion'].iloc[0]
        st.metric(label="Marca Líder en Góndola", value=marca_lider, delta=f"{part_lider:.2f}% del catálogo")
        st.dataframe(df_est.head(10), hide_index=True)
        
    with col2:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        sns.barplot(x="Participacion", y="marca", data=df_est.head(10), hue="marca", palette="Blues_r", legend=False, ax=ax)
        sns.despine(left=True, bottom=False)
        ax.set_xlabel("Participación en el Catálogo (%)")
        ax.set_ylabel("")
        st.pyplot(fig)

# ==========================================
# PESTAÑA 2: NIVEL TÁCTICO
# ==========================================
with tab_tac:
    st.header("Bandas de Competitividad y Dispersión de Precios por Tienda")
    st.caption("Frecuencia: Semanal | Objetivo: Monitorear mínimos, máximos y promedios para definir estrategias comerciales")
    
    # Filtro interactivo de tiendas
    tiendas_disponibles = df['tienda'].unique()
    tiendas_seleccionadas = st.multiselect(
        "Filtrar Tiendas para Análisis de Competencia:", 
        options=tiendas_disponibles, 
        default=tiendas_disponibles[:6]
    )
    
    if tiendas_seleccionadas:
        df_filtrado_tac = df[df['tienda'].isin(tiendas_seleccionadas)]
        
        # Agrupación por tienda calculando la dispersión comercial
        df_tac = df_filtrado_tac.groupby('tienda')['precio_raw'].agg(['min', 'mean', 'max']).reset_index().sort_values(by='mean')
        
        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.vlines(x=df_tac['tienda'], ymin=df_tac['min'], ymax=df_tac['max'], colors='#B0BEC5', alpha=0.7, linewidth=3)
        ax.scatter(df_tac['tienda'], df_tac['mean'], color='#1A237E', s=120, zorder=3, label="Precio Promedio")
        ax.scatter(df_tac['tienda'], df_tac['min'], color='#2E7D32', marker='^', s=80, zorder=3, label="Precio Mínimo")
        ax.scatter(df_tac['tienda'], df_tac['max'], color='#C62828', marker='v', s=80, zorder=3, label="Precio Máximo")
        
        ax.set_ylabel("Precio del Equipo ($)")
        plt.xticks(rotation=25, ha='right')
        ax.legend()
        sns.despine(left=True)
        st.pyplot(fig)
    else:
        st.info("Por favor, selecciona al menos una tienda para visualizar las bandas de precios.")

# ==========================================
# PESTAÑA 3: NIVEL OPERACIONAL
# ==========================================
with tab_op:
    st.header("Matriz de Control Comercial: Límites de Precio por Marca")
    st.caption("Frecuencia: Diario | Objetivo: Establecer techos de precio y detectar desvíos o sobreprecios por fabricante")
    
    # Selección de marcas para la auditoría operacional
    marcas_disponibles = df['marca'].unique()
    marcas_seleccionadas = st.multiselect(
        "Seleccionar Marcas para Control de Umbrales:",
        options=marcas_disponibles,
        default=marcas_disponibles[:5]
    )
    
    if marcas_seleccionadas:
        df_filtrado_op = df[df['marca'].isin(marcas_seleccionadas)]
        
        # Configuración del control de precio límite basado en la selección
        min_p = int(df_filtrado_op['precio_raw'].min())
        max_p = int(df_filtrado_op['precio_raw'].max())
        mean_p = int(df_filtrado_op['precio_raw'].mean())
        
        limite_precio = st.slider(
            "Establecer Límite Máximo Permitido ($):", 
            min_value=min_p, 
            max_value=max_p, 
            value=mean_p, 
            step=50000
        )
        
        # Captura de SKUs fuera de los límites operacionales
        zona_exceso = df_filtrado_op[df_filtrado_op['precio_raw'] > limite_precio]
        
        if len(zona_exceso) > 0:
            st.error(f"🚨 Alerta Operacional: Se han detectado {len(zona_exceso)} SKUs que exceden el límite de precio de control establecido.")
        else:
            st.success("✅ Control Operacional Óptimo: Ningún modelo de las marcas seleccionadas supera el límite.")
        
        # Gráfico de control de distribución por marcas seleccionadas
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.stripplot(x="marca", y="precio_raw", data=df_filtrado_op, jitter=0.2, alpha=0.5, size=6, color="#78909C", ax=ax)
        
        # Resaltar en rojo los productos que rompen el techo comercial
        if len(zona_exceso) > 0:
            sns.stripplot(x="marca", y="precio_raw", data=zona_exceso, jitter=0.2, size=7, color="#D32F2F", edgecolor="black", linewidth=1, ax=ax)
            
        ax.axhline(y=limite_precio, color='#C62828', linestyle='--', alpha=0.7, label=f"Límite de Control (${limite_precio:,})")
        
        ax.set_xlabel("Marca")
        ax.set_ylabel("Precio ($)")
        plt.xticks(rotation=15)
        ax.legend()
        sns.despine(left=True)
        st.pyplot(fig)
        
        if len(zona_exceso) > 0:
            st.subheader("📋 Lista de Modelos bajo Alerta de Techo de Precio:")
            st.dataframe(zona_exceso[['marca', 'tienda', 'precio_raw']].sort_values(by='precio_raw', ascending=False), hide_index=True)
    else:
        st.info("Por favor, selecciona al menos una marca para inicializar la matriz de control operacional.")