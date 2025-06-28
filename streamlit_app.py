import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Carregamento e pré-processamento do CSV
@st.cache_data
def load_data(file):
    df = pd.read_csv(file, sep=';', encoding='utf-8-sig')  # ajuste sep se for vírgula
    df.columns = df.columns.str.strip().str.lower()
    df['data'] = pd.to_datetime(df['data'], dayfirst=True)
    df['mes']           = df['data'].dt.to_period('M').astype(str)
    df['semana']        = df['data'].dt.isocalendar().week
    df['dia']           = df['data'].dt.date
    df['dia_da_semana'] = df['data'].dt.day_name(locale='pt_BR')
    return df

# 2. Configuração da página
st.set_page_config(layout="wide", page_title="Dashboard de Vendas")
st.title("📊 Dashboard de Vendas")

# 3. Upload do CSV
uploaded = st.file_uploader("📥 Carregue seu arquivo CSV", type="csv")
if not uploaded:
    st.info("Faça o upload de um CSV que contenha as colunas descritas.")
    st.stop()

df = load_data(uploaded)

# 4. Filtros no topo
st.markdown("## 🔎 Filtros")

# 4.1 Filtro de data
col_data1, col_data2 = st.columns(2)
with col_data1:
    data_inicio = st.date_input(
        "Data inicial",
        value=df['data'].min(),
        min_value=df['data'].min(),
        max_value=df['data'].max()
    )
with col_data2:
    data_fim = st.date_input
