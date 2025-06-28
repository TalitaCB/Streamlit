import streamlit as st
import pandas as pd
import plotly.express as px

# 1) Carregamento e pré-processamento
@st.cache_data
def load_data(f):
    df = pd.read_csv(f, encoding='utf-8-sig', sep=';')  # ajuste sep conforme preciso
    # normaliza nomes: tira espaços, converte p/ lowercase
    df.columns = df.columns.str.strip().str.lower()
    # aí já temos 'data' “limpinho”
    df['data'] = pd.to_datetime(df['data'], dayfirst=True)
    # gera mes, semana, etc...
    # ...
    return df

st.set_page_config(layout="wide", page_title="Dashboard de Vendas")
st.title("📊 Dashboard de Vendas")

# 2) Upload do CSV
uploaded = st.file_uploader("📥 Carregue seu arquivo CSV", type="csv")
if not uploaded:
    st.info("Aguardando o upload do arquivo CSV com as colunas definidas.")
    st.stop()

df = load_data(uploaded)

# 3) Sidebar de filtros
st.sidebar.header("⛓️ Filtros")
min_data, max_data = df['data'].min(), df['data'].max()
data_inicial = st.sidebar.date_input("Data inicial", min_data, min_value=min_data, max_value=max_data)
data_final   = st.sidebar.date_input("Data final",   max_data, min_value=min_data, max_value=max_data)

# filtros de atributos
campos = ['categoria','modalidade','linha','grupo','subgrupo','classe',
          'marca','modelo','cor','modelocor','udn','produto']
filtros = {}
for c in campos:
    valores = df[c].dropna().unique().tolist()
    selecionados = st.sidebar.multiselect(c.capitalize(), valores)
    if selecionados:
        filtros[c] = selecionados

# aplica filtros
mask = (df['data'] >= pd.to_datetime(data_inicial)) & (df['data'] <= pd.to_datetime(data_final))
df = df.loc[mask]
for c, vs in filtros.items():
    df = df[df[c].isin(vs)]

# 4) Escolha de métricas e agrupamento
st.sidebar.header("🔢 Métricas e Layout")
metricas = ['valor da venda','quantidade de itens','cmv','cmv_u','valor medio itens','lucro bruto']
selecionadas = st.sidebar.multiselect("Colunas a mostrar", metricas, default=metricas)

agrup = st.sidebar.selectbox(
    "Ver dados por",
    ['Resumo Geral','Mês','Semana','Dia','Dia da Semana']
)

# 5) Agregação
if agrup == 'Resumo Geral':
    df_out = df.groupby('categoria')[selecionadas].sum().reset_index()
    eixo_x = 'categoria'
else:
    eixo_x = {
        'Mês': 'mes',
        'Semana': 'semana',
        'Dia': 'dia',
        'Dia da Semana': 'dia_da_semana'
    }[agrup]
    df_out = (
        df
        .groupby(['categoria', eixo_x])[selecionadas]
        .sum()
        .reset_index()
    )

# 6) Exibição da tabela
st.subheader("📋 Tabela de Resultados")
st.dataframe(df_out, use_container_width=True)

# 7) Gráfico de linhas opcional
if st.sidebar.checkbox("Mostrar gráfico de linhas"):
    st.subheader("📈 Gráfico de Tendência")
    # se for resumo geral, não faz sentido gráfico de tempo
    if agrup == 'Resumo Geral':
        st.warning("Selecione um agrupamento temporal (Mês/Semana/Dia) para ver o gráfico.")
    else:
        met_graf = st.sidebar.selectbox("Métrica no gráfico", selecionadas)
        fig = px.line(
            df_out,
            x=eixo_x,
            y=met_graf,
            color='categoria',
            markers=True,
            title=f"{met_graf} por {agrup.lower()}"
        )
        st.plotly_chart(fig, use_container_width=True)

# 8) Extras (download)
st.sidebar.header("📥 Exportar")
if st.sidebar.button("⬇️ Baixar CSV filtrado"):
    st.download_button(
        label="Download CSV",
        data=df_out.to_csv(index=False, sep=';'),
        file_name="vendas_filtradas.csv",
        mime="text/csv"
    )
