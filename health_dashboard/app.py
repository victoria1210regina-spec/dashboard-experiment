import pandas as pd
import plotly.express as px
import streamlit as st

from utils import (
    calcular_icq,
    classificar_pressao,
    classificar_risco_cintura,
    gerar_dados_simulados,
)

st.set_page_config(
    page_title="Dashboard de Avaliação de Saúde – Educação Física",
    layout="wide",
)

st.title("Dashboard de Avaliação de Saúde – Educação Física")
st.markdown(
    "Análise de indicadores antropométricos e cardiovasculares "
    "(PAS, PAD e FC)."
)

# ================================
# Fonte de dados
# ================================
st.sidebar.header("Fonte de dados")
upload = st.sidebar.file_uploader("Upload de CSV próprio", type=["csv"])

if upload is not None:
    try:
        df = pd.read_csv(upload)
        st.sidebar.success("CSV carregado com sucesso.")
    except Exception as exc:
        st.sidebar.error(f"Erro ao ler CSV: {exc}")
        st.stop()
else:
    try:
        df = gerar_dados_simulados("data/dados_simulados.csv", n=120)
    except Exception as exc:
        st.error(f"Erro ao gerar/carregar dados simulados: {exc}")
        st.stop()

colunas_obrigatorias = [
    "id",
    "sexo",
    "idade",
    "circunferencia_cintura",
    "circunferencia_quadril",
    "circunferencia_braco",
    "circunferencia_coxa",
    "pas",
    "pad",
    "fc",
]

faltantes = [col for col in colunas_obrigatorias if col not in df.columns]
if faltantes:
    st.error(f"CSV inválido. Colunas ausentes: {faltantes}")
    st.stop()

# Garante colunas derivadas para CSV externo
if "icq" not in df.columns:
    df["icq"] = df.apply(
        lambda row: calcular_icq(
            row["circunferencia_cintura"], row["circunferencia_quadril"]
        ),
        axis=1,
    )
if "classificacao_pressao" not in df.columns:
    df["classificacao_pressao"] = df.apply(
        lambda row: classificar_pressao(row["pas"], row["pad"]),
        axis=1,
    )
if "risco_cintura" not in df.columns:
    df["risco_cintura"] = df.apply(
        lambda row: classificar_risco_cintura(row["sexo"], row["circunferencia_cintura"]),
        axis=1,
    )

# ================================
# Filtros
# ================================
st.sidebar.header("Filtros")
sexo_opts = sorted(df["sexo"].dropna().unique().tolist())
sexo_sel = st.sidebar.multiselect("Sexo", sexo_opts, default=sexo_opts)

idade_min, idade_max = int(df["idade"].min()), int(df["idade"].max())
faixa_idade = st.sidebar.slider("Faixa etária", idade_min, idade_max, (idade_min, idade_max))

pas_min, pas_max = int(df["pas"].min()), int(df["pas"].max())
faixa_pas = st.sidebar.slider("PAS (mmHg)", pas_min, pas_max, (pas_min, pas_max))

fc_min, fc_max = int(df["fc"].min()), int(df["fc"].max())
faixa_fc = st.sidebar.slider("FC (bpm)", fc_min, fc_max, (fc_min, fc_max))

df_f = df[
    df["sexo"].isin(sexo_sel)
    & df["idade"].between(*faixa_idade)
    & df["pas"].between(*faixa_pas)
    & df["fc"].between(*faixa_fc)
].copy()

st.subheader("Indicadores principais")
if df_f.empty:
    st.warning("Nenhum registro encontrado para os filtros selecionados.")
else:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Média PAS", f"{df_f['pas'].mean():.1f} mmHg")
    c2.metric("Média PAD", f"{df_f['pad'].mean():.1f} mmHg")
    c3.metric("Média FC", f"{df_f['fc'].mean():.1f} bpm")
    c4.metric("Média cintura", f"{df_f['circunferencia_cintura'].mean():.1f} cm")
    c5.metric("ICQ médio", f"{df_f['icq'].mean():.2f}")

st.subheader("Download")
st.download_button(
    "Baixar dataset filtrado",
    data=df_f.to_csv(index=False).encode("utf-8"),
    file_name="dados_filtrados_dashboard.csv",
    mime="text/csv",
)

tab1, tab2, tab3, tab4 = st.tabs(
    ["Visão Geral", "Antropometria", "Cardiovascular", "Correlações"]
)

with tab1:
    fig_hist = px.histogram(
        df_f,
        x="pas",
        nbins=20,
        title="Histograma de PAS",
        labels={"pas": "PAS (mmHg)"},
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    dist_pressao = (
        df_f["classificacao_pressao"].value_counts().reset_index(name="quantidade")
    )
    dist_pressao.columns = ["classificacao", "quantidade"]
    fig_bar = px.bar(
        dist_pressao,
        x="classificacao",
        y="quantidade",
        color="classificacao",
        title="Distribuição das classificações de pressão",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    fig_box = px.box(
        df_f,
        x="sexo",
        y="circunferencia_cintura",
        color="sexo",
        points="all",
        title="Boxplot de cintura por sexo",
    )
    st.plotly_chart(fig_box, use_container_width=True)

with tab3:
    fig_scatter = px.scatter(
        df_f,
        x="circunferencia_cintura",
        y="pas",
        color="sexo",
        hover_data=["id", "idade", "pad", "fc", "classificacao_pressao"],
        title="Scatterplot PAS vs cintura",
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab4:
    cols_num = [
        "idade",
        "circunferencia_cintura",
        "circunferencia_quadril",
        "circunferencia_braco",
        "circunferencia_coxa",
        "pas",
        "pad",
        "fc",
        "icq",
    ]
    corr = df_f[cols_num].corr(numeric_only=True)
    fig_heat = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        title="Heatmap de correlação",
    )
    st.plotly_chart(fig_heat, use_container_width=True)
