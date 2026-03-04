"""Aplicação Streamlit para avaliação física longitudinal individual."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils import (
    COLUNAS_OPCIONAIS_COMPOSICAO,
    COLUNAS_OBRIGATORIAS,
    montar_resumo_variacoes,
    organizar_dados_longitudinais,
    validar_colunas,
)

st.set_page_config(page_title="Avaliação Física Longitudinal", layout="wide")

st.title("📈 Dashboard de Avaliação Física Longitudinal")
st.caption(
    "Compare cada indivíduo com ele mesmo ao longo do tempo, sem comparação entre pessoas.",
)


@st.cache_data
def carregar_csv(uploaded_file) -> pd.DataFrame:
    """Lê CSV de forma segura e retorna DataFrame."""
    return pd.read_csv(uploaded_file)


def formatar_delta(valor: float) -> str:
    """Formata deltas para exibição amigável no st.metric."""
    if pd.isna(valor):
        return "N/A"
    return f"{valor:+.2f}"



def construir_relatorio_resumido(df_individuo: pd.DataFrame) -> pd.DataFrame:
    """Monta tabela-resumo com principais variáveis e variações."""
    variaveis = {
        "peso": "Peso (kg)",
        "imc": "IMC",
        "cintura": "Cintura (cm)",
        "icq": "Relação Cintura/Quadril",
        "dif_biceps": "Diferença Bíceps (cm)",
    }

    linhas = []
    for coluna, nome_exibicao in variaveis.items():
        resumo = montar_resumo_variacoes(df_individuo, coluna)
        if not resumo:
            continue

        linhas.append(
            {
                "variavel": nome_exibicao,
                "valor_atual": resumo["atual"],
                "valor_primeira": resumo["primeira"],
                "valor_anterior": resumo["anterior"],
                "var_abs_desde_primeira": resumo["var_abs_primeira"],
                "var_pct_desde_primeira": resumo["var_pct_primeira"],
                "var_abs_vs_anterior": resumo["var_abs_anterior"],
                "var_pct_vs_anterior": resumo["var_pct_anterior"],
            }
        )

    return pd.DataFrame(linhas)


# =====================
# Sidebar: entrada de dados
# =====================
st.sidebar.header("Configurações")
arquivo_upload = st.sidebar.file_uploader("Faça upload da planilha CSV", type=["csv"])

if arquivo_upload is not None:
    arquivo_fonte = arquivo_upload
else:
    arquivo_fonte = "exemplo_planilha.csv"
    st.sidebar.info("Nenhum arquivo enviado. Usando o arquivo de exemplo local.")

try:
    df_bruto = carregar_csv(arquivo_fonte)
except Exception as erro_leitura:
    st.error(f"Erro ao ler o CSV: {erro_leitura}")
    st.stop()

colunas_ausentes = validar_colunas(df_bruto, COLUNAS_OBRIGATORIAS)
if colunas_ausentes:
    st.error(
        "A planilha não possui todas as colunas obrigatórias. "
        f"Ausentes: {', '.join(colunas_ausentes)}",
    )
    st.stop()

df = organizar_dados_longitudinais(df_bruto)

if df["data_avaliacao"].isna().any():
    st.error(
        "Existem datas inválidas em 'data_avaliacao'. Corrija o formato no CSV "
        "(ex.: 31/12/2025).",
    )
    st.stop()

if (df["altura"] == 0).any():
    st.error(
        "Foi encontrada altura igual a zero. Corrija os dados para calcular IMC corretamente.",
    )
    st.stop()

nomes_disponiveis = sorted(df["nome"].dropna().unique().tolist())
individuo = st.sidebar.selectbox("Selecione o indivíduo", options=nomes_disponiveis)

df_individuo = df[df["nome"] == individuo].copy().sort_values("data_avaliacao")

if df_individuo.empty:
    st.warning("Não há dados para o indivíduo selecionado.")
    st.stop()

min_data = df_individuo["data_avaliacao"].min().date()
max_data = df_individuo["data_avaliacao"].max().date()
intervalo_datas = st.sidebar.date_input(
    "Filtrar intervalo de datas",
    value=(min_data, max_data),
    min_value=min_data,
    max_value=max_data,
)

if isinstance(intervalo_datas, tuple) and len(intervalo_datas) == 2:
    data_inicio, data_fim = intervalo_datas
else:
    data_inicio, data_fim = min_data, max_data

mascara_periodo = (df_individuo["data_avaliacao"].dt.date >= data_inicio) & (
    df_individuo["data_avaliacao"].dt.date <= data_fim
)
df_filtrado = df_individuo[mascara_periodo].copy()

if df_filtrado.empty:
    st.warning("Nenhuma avaliação encontrada para o período selecionado.")
    st.stop()

# Relatórios para download
relatorio_resumido = construir_relatorio_resumido(df_filtrado)

st.sidebar.download_button(
    "⬇️ Baixar relatório resumido (CSV)",
    data=relatorio_resumido.to_csv(index=False).encode("utf-8"),
    file_name=f"relatorio_resumido_{individuo}.csv",
    mime="text/csv",
)

st.sidebar.download_button(
    "⬇️ Baixar dados filtrados (CSV)",
    data=df_filtrado.to_csv(index=False).encode("utf-8"),
    file_name=f"dados_filtrados_{individuo}.csv",
    mime="text/csv",
)

# =====================
# Abas do dashboard
# =====================
aba1, aba2, aba3, aba4 = st.tabs(
    [
        "Resumo Atual",
        "Evolução Temporal",
        "Análise de Circunferências",
        "Composição Corporal",
    ]
)

with aba1:
    st.subheader("Resumo da avaliação mais recente")

    ultima = df_filtrado.iloc[-1]

    resumo_peso = montar_resumo_variacoes(df_filtrado, "peso")
    resumo_imc = montar_resumo_variacoes(df_filtrado, "imc")
    resumo_cintura = montar_resumo_variacoes(df_filtrado, "cintura")
    resumo_icq = montar_resumo_variacoes(df_filtrado, "icq")
    resumo_biceps = montar_resumo_variacoes(df_filtrado, "dif_biceps")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(
        "Peso atual (kg)",
        f"{ultima['peso']:.2f}",
        delta=formatar_delta(resumo_peso["var_abs_anterior"]),
        help="Delta = variação em relação à avaliação anterior.",
    )
    col2.metric(
        "IMC atual",
        f"{ultima['imc']:.2f}",
        delta=formatar_delta(resumo_imc["var_abs_anterior"]),
    )
    col3.metric(
        "Cintura atual (cm)",
        f"{ultima['cintura']:.2f}",
        delta=formatar_delta(resumo_cintura["var_abs_anterior"]),
    )
    col4.metric(
        "Relação cintura/quadril",
        f"{ultima['icq']:.3f}",
        delta=formatar_delta(resumo_icq["var_abs_anterior"]),
    )
    col5.metric(
        "Diferença bíceps (cm)",
        f"{ultima['dif_biceps']:.2f}",
        delta=formatar_delta(resumo_biceps["var_abs_anterior"]),
    )

    st.markdown("### Variações desde a primeira avaliação e vs anterior")
    st.dataframe(relatorio_resumido, use_container_width=True)

with aba2:
    st.subheader("Evolução temporal")

    variaveis_disponiveis = {
        "Peso (kg)": "peso",
        "IMC": "imc",
        "Cintura (cm)": "cintura",
        "Relação Cintura/Quadril": "icq",
        "Peitoral (cm)": "peitoral",
        "Quadril (cm)": "quadril",
        "Coxa (cm)": "coxa",
        "Panturrilha (cm)": "panturrilha",
        "Bíceps Contraído (cm)": "biceps_contraido",
        "Bíceps Relaxado (cm)": "biceps_relaxado",
    }

    variavel_escolhida_label = st.selectbox(
        "Escolha a variável para visualizar", list(variaveis_disponiveis.keys())
    )
    variavel_escolhida = variaveis_disponiveis[variavel_escolhida_label]

    fig = px.line(
        df_filtrado,
        x="data_avaliacao",
        y=variavel_escolhida,
        markers=True,
        title=f"{variavel_escolhida_label} ao longo do tempo",
    )
    fig.update_layout(xaxis_title="Data", yaxis_title=variavel_escolhida_label)
    st.plotly_chart(fig, use_container_width=True)

with aba3:
    st.subheader("Análise de circunferências: primeira vs última avaliação")

    colunas_circunferencias = [
        "peitoral",
        "cintura",
        "quadril",
        "coxa",
        "panturrilha",
        "biceps_contraido",
        "biceps_relaxado",
    ]

    primeira = df_filtrado.iloc[0]
    ultima = df_filtrado.iloc[-1]

    tabela_circ = pd.DataFrame(
        {
            "circunferencia": colunas_circunferencias,
            "valor_inicial": [primeira[c] for c in colunas_circunferencias],
            "valor_final": [ultima[c] for c in colunas_circunferencias],
        }
    )

    tabela_circ["dif_absoluta"] = tabela_circ["valor_final"] - tabela_circ["valor_inicial"]
    tabela_circ["dif_percentual"] = (
        (tabela_circ["dif_absoluta"] / tabela_circ["valor_inicial"]) * 100
    )

    fig_circ = px.bar(
        tabela_circ.melt(
            id_vars="circunferencia",
            value_vars=["valor_inicial", "valor_final"],
            var_name="momento",
            value_name="valor",
        ),
        x="circunferencia",
        y="valor",
        color="momento",
        barmode="group",
        title="Comparativo de circunferências (inicial vs final)",
    )
    st.plotly_chart(fig_circ, use_container_width=True)

    st.dataframe(tabela_circ, use_container_width=True)

with aba4:
    st.subheader("Composição corporal")

    colunas_presentes = [c for c in COLUNAS_OPCIONAIS_COMPOSICAO if c in df_filtrado.columns]
    if not colunas_presentes:
        st.info("Dados de composição corporal ainda não foram incluídos nas avaliações.")
    else:
        variavel_comp = st.selectbox("Variável de composição", colunas_presentes)
        fig_comp = px.line(
            df_filtrado,
            x="data_avaliacao",
            y=variavel_comp,
            markers=True,
            title=f"{variavel_comp} ao longo do tempo",
        )
        st.plotly_chart(fig_comp, use_container_width=True)

st.markdown("---")
st.caption("Projeto didático em Streamlit para iniciantes em Python.")
