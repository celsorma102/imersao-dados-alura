import pandas as pd
import streamlit as st
import plotly.express as px

# Configuração da pagina
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide"
)


# Carregar dados da imersão
df = pd.read_csv("https://raw.githubusercontent.com/celsorma102/imersao-dados-alura/refs/heads/main/df_imersao_dados.csv")

# Cabeçalho do Sidebar
st.sidebar.header("Filtros")

# Filtro de ano
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# Filtro Senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionados = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

# Filtro de Contratos
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Contratos", contratos_disponiveis, default=contratos_disponiveis)

# Filtro de Porte da Empresa
portes_disponiveis = sorted(df["porte_empresa"].unique())
portes_selecionados = st.sidebar.multiselect("Porte da Empresa", portes_disponiveis,default=portes_disponiveis)

# Filtragem do DataFrame, para interatividade
df_filtrado = df[
    (df["ano"].isin(anos_selecionados)) &
    (df["senioridade"].isin(senioridades_selecionados)) &
    (df["contrato"].isin(contratos_selecionados)) &
    (df["porte_empresa"].isin(portes_selecionados))             
                 ]

# Conteudo Principal
st.title("Dashboard de Análise de Salários na Área de Dados")
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")

# KPIs Principais
st.subheader("Métricas gerais (Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado["usd"].mean()
    salario_maximo = df_filtrado["usd"].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_maximo, total_registros, cargo_mais_frequente = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário Médio", f"${salario_medio:,.0f}")
col2.metric("Salário Máximo", f"${salario_maximo:,.0f}")
col3.metric("Registros Totais", f"{total_registros:}")
col4.metric("Cargos Mais Frequentes", cargo_mais_frequente)

st.markdown("----")

# Analises Visuais com Plotly
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''}
        )
        grafico_cargos.update_layout(title_x= 0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd':'Faixa Salarial (USD)', 'count':''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title="Proporção dos tipos de trabalho",
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo= 'percent+label')
        grafico_remoto.update_layout(title_x= 0.1)
        st.plotly_chart(grafico_remoto, use_container_width= True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()
        grafico_paises = px.choropleth(media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário médio de Cientista de Dados por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

# Adicionando meu resultado do desafio da aula 3 com o grafico de top 10
df_data_scientist = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
df_data_scientist = df_data_scientist.groupby('residencia_iso3')['usd'].mean().sort_values(ascending=False).reset_index()
df_data_scientist = df_data_scientist.head(10)
grafico_top10 = px.bar(df_data_scientist,
                             x='residencia_iso3',
                             y='usd',
                             title='Top 10 - Média salarial por país de um Cientista de Dados (Ano)',
                             labels={'usd':'Salário médio (USD)','residencia_iso3':'País'}

)
grafico_top10.update_layout(title_x=0.1)
st.plotly_chart(grafico_top10, use_container_width=True)

# Tabela de Dados Detalhados
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)