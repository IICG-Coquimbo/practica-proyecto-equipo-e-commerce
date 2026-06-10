import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración
st.set_page_config(page_title="Dashboard E-commerce", layout="wide")

st.title("📊 Dashboard Ejecutivo E-commerce")
st.markdown("---")

# Cargar datos
@st.cache_data
def cargar_datos():
    return pd.read_csv("datos_dashboard.csv")

df = cargar_datos()

# Tabs
tab_est, tab_tac, tab_op = st.tabs([
    "📊 Estratégico",
    "📈 Táctico",
    "⚙️ Operacional"
])

# ==========================================
# 🔵 ESTRATÉGICO
# ==========================================
with tab_est:
    st.header("Concentración del mercado por marca")

    total = len(df)

    df_est = df["marca"].value_counts().reset_index()
    df_est.columns = ["marca", "cantidad"]
    df_est["participacion"] = (df_est["cantidad"] / total) * 100

    col1, col2 = st.columns([1,2])

    with col1:
        st.metric("Total productos", total)
        st.metric("Marca líder", df_est["marca"].iloc[0])

    with col2:
        fig, ax = plt.subplots()
        sns.barplot(data=df_est, x="participacion", y="marca", ax=ax)
        ax.set_title("Participación por Marca (%)")
        st.pyplot(fig)

# ==========================================
# 🟡 TÁCTICO
# ==========================================
with tab_tac:
    st.header("Dispersión de precios por marca")

    df_tac = df.groupby("marca")["precio_numerico"].agg(["min","mean","max"]).reset_index()

    fig, ax = plt.subplots(figsize=(10,5))

    ax.vlines(
        x=df_tac["marca"],
        ymin=df_tac["min"],
        ymax=df_tac["max"],
        color="gray"
    )

    ax.scatter(df_tac["marca"], df_tac["mean"], label="Promedio")
    ax.scatter(df_tac["marca"], df_tac["min"], label="Min")
    ax.scatter(df_tac["marca"], df_tac["max"], label="Max")

    plt.xticks(rotation=45)
    ax.legend()

    st.pyplot(fig)

# ==========================================
# 🔴 OPERACIONAL
# ==========================================
with tab_op:
    st.header("Rango de precios por marca")

    df_op = df.groupby("marca")["precio_numerico"].agg(["min","max"]).reset_index()
    df_op["rango"] = df_op["max"] - df_op["min"]

    df_op = df_op.sort_values(by="rango", ascending=False)

    col1, col2 = st.columns([1,2])

    with col1:
        st.dataframe(df_op)

    with col2:
        fig, ax = plt.subplots()

        sns.barplot(
            data=df_op,
            x="rango",
            y="marca",
            ax=ax
        )

        ax.set_title("Rango de precios")
        st.pyplot(fig)