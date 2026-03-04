"""Funções utilitárias para o dashboard de avaliação física longitudinal.

Este arquivo concentra cálculos e validações para manter o app.py mais limpo e didático.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

# Colunas obrigatórias definidas no enunciado.
COLUNAS_OBRIGATORIAS = [
    "nome",
    "data_avaliacao",
    "sexo",
    "idade",
    "peitoral",
    "cintura",
    "quadril",
    "coxa",
    "panturrilha",
    "biceps_contraido",
    "biceps_relaxado",
    "peso",
    "altura",
]

# Colunas opcionais futuras.
COLUNAS_OPCIONAIS_COMPOSICAO = [
    "percentual_gordura",
    "massa_magra",
    "massa_gorda",
    "agua_corporal",
]


def validar_colunas(df: pd.DataFrame, colunas_obrigatorias: Iterable[str] = COLUNAS_OBRIGATORIAS) -> list[str]:
    """Retorna a lista de colunas obrigatórias ausentes."""
    colunas_ausentes = [col for col in colunas_obrigatorias if col not in df.columns]
    return colunas_ausentes


def calcular_imc(peso: pd.Series | float, altura: pd.Series | float) -> pd.Series | float:
    """Calcula IMC: peso / altura².

    - Se a altura for zero ou inválida, retorna NaN para evitar erro matemático.
    """
    altura_segura = pd.to_numeric(altura, errors="coerce")
    altura_segura = altura_segura.replace(0, np.nan)
    peso_numerico = pd.to_numeric(peso, errors="coerce")
    return peso_numerico / (altura_segura**2)


def calcular_icq(cintura: pd.Series | float, quadril: pd.Series | float) -> pd.Series | float:
    """Calcula ICQ (Índice Cintura-Quadril): cintura / quadril."""
    quadril_seguro = pd.to_numeric(quadril, errors="coerce").replace(0, np.nan)
    cintura_numerica = pd.to_numeric(cintura, errors="coerce")
    return cintura_numerica / quadril_seguro


def calcular_diferenca_biceps(
    biceps_contraido: pd.Series | float,
    biceps_relaxado: pd.Series | float,
) -> pd.Series | float:
    """Diferença entre bíceps contraído e relaxado."""
    return pd.to_numeric(biceps_contraido, errors="coerce") - pd.to_numeric(
        biceps_relaxado,
        errors="coerce",
    )


def calcular_variacao_absoluta(valor_atual: float, valor_referencia: float) -> float:
    """Calcula variação absoluta: atual - referência."""
    if pd.isna(valor_atual) or pd.isna(valor_referencia):
        return np.nan
    return valor_atual - valor_referencia


def calcular_variacao_percentual(valor_atual: float, valor_referencia: float) -> float:
    """Calcula variação percentual: ((atual - referência) / referência) * 100."""
    if pd.isna(valor_atual) or pd.isna(valor_referencia) or valor_referencia == 0:
        return np.nan
    return ((valor_atual - valor_referencia) / valor_referencia) * 100


def organizar_dados_longitudinais(df: pd.DataFrame) -> pd.DataFrame:
    """Padroniza tipos e ordena os dados por nome e data.

    Etapas:
    1) Converte data_avaliacao para datetime.
    2) Converte colunas numéricas para formato numérico.
    3) Calcula colunas derivadas (IMC, ICQ e diferença de bíceps).
    4) Ordena para análise longitudinal.
    """
    df_tratado = df.copy()

    # Converte data, gerando NaT quando formato é inválido.
    df_tratado["data_avaliacao"] = pd.to_datetime(
        df_tratado["data_avaliacao"],
        errors="coerce",
        dayfirst=True,
    )

    colunas_numericas = [
        "idade",
        "peitoral",
        "cintura",
        "quadril",
        "coxa",
        "panturrilha",
        "biceps_contraido",
        "biceps_relaxado",
        "peso",
        "altura",
        *[c for c in COLUNAS_OPCIONAIS_COMPOSICAO if c in df_tratado.columns],
    ]

    for coluna in colunas_numericas:
        df_tratado[coluna] = pd.to_numeric(df_tratado[coluna], errors="coerce")

    df_tratado["imc"] = calcular_imc(df_tratado["peso"], df_tratado["altura"])
    df_tratado["icq"] = calcular_icq(df_tratado["cintura"], df_tratado["quadril"])
    df_tratado["dif_biceps"] = calcular_diferenca_biceps(
        df_tratado["biceps_contraido"],
        df_tratado["biceps_relaxado"],
    )

    return df_tratado.sort_values(["nome", "data_avaliacao"]).reset_index(drop=True)


def montar_resumo_variacoes(df_individuo: pd.DataFrame, coluna: str) -> dict[str, float]:
    """Retorna um dicionário com variações de uma coluna para um indivíduo.

    Métricas retornadas:
    - atual
    - primeira
    - anterior
    - var_abs_primeira, var_pct_primeira
    - var_abs_anterior, var_pct_anterior
    """
    if df_individuo.empty:
        return {}

    atual = df_individuo[coluna].iloc[-1]
    primeira = df_individuo[coluna].iloc[0]
    anterior = df_individuo[coluna].iloc[-2] if len(df_individuo) > 1 else np.nan

    return {
        "atual": atual,
        "primeira": primeira,
        "anterior": anterior,
        "var_abs_primeira": calcular_variacao_absoluta(atual, primeira),
        "var_pct_primeira": calcular_variacao_percentual(atual, primeira),
        "var_abs_anterior": calcular_variacao_absoluta(atual, anterior),
        "var_pct_anterior": calcular_variacao_percentual(atual, anterior),
    }
