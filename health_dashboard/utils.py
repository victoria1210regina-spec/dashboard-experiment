from pathlib import Path
import numpy as np
import pandas as pd


def classificar_pressao(pas: float, pad: float) -> str:
    """Classifica pressão arterial por regra simplificada."""
    try:
        pas = float(pas)
        pad = float(pad)
    except (TypeError, ValueError):
        return "Indefinida"

    if pas >= 140 or pad >= 90:
        return "Hipertensão Estágio 2"
    if 130 <= pas <= 139 or 80 <= pad <= 89:
        return "Hipertensão Estágio 1"
    if 120 <= pas <= 129 and pad < 80:
        return "Elevada"
    return "Normal"


def calcular_icq(cintura: float, quadril: float) -> float:
    """Calcula o índice cintura-quadril (ICQ)."""
    try:
        cintura = float(cintura)
        quadril = float(quadril)
        if quadril <= 0:
            return np.nan
        return cintura / quadril
    except (TypeError, ValueError):
        return np.nan


def classificar_risco_cintura(sexo: str, cintura: float) -> str:
    """Classificação de risco cardiovascular baseada na cintura."""
    try:
        cintura = float(cintura)
    except (TypeError, ValueError):
        return "Indefinido"

    sexo = str(sexo).strip().lower()

    if sexo == "masculino":
        if cintura < 94:
            return "Baixo"
        if cintura < 102:
            return "Aumentado"
        return "Muito Aumentado"

    # Feminino como padrão
    if cintura < 80:
        return "Baixo"
    if cintura < 88:
        return "Aumentado"
    return "Muito Aumentado"


def gerar_dados_simulados(caminho_csv: str = "data/dados_simulados.csv", n: int = 120, seed: int = 42) -> pd.DataFrame:
    """Gera dataset simulado (ou carrega caso já exista)."""
    caminho = Path(caminho_csv)

    if caminho.exists():
        try:
            return pd.read_csv(caminho)
        except Exception:
            # Se arquivo estiver inválido, recria
            pass

    caminho.parent.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)

    sexo = rng.choice(["Masculino", "Feminino"], size=n)
    idade = rng.integers(18, 76, size=n)

    cintura = np.array([
        rng.uniform(75, 120) if s == "Masculino" else rng.uniform(65, 110)
        for s in sexo
    ])
    quadril = np.array([
        rng.uniform(85, 125) if s == "Masculino" else rng.uniform(85, 130)
        for s in sexo
    ])
    braco = np.array([
        rng.uniform(26, 42) if s == "Masculino" else rng.uniform(22, 38)
        for s in sexo
    ])
    coxa = np.array([
        rng.uniform(45, 70) if s == "Masculino" else rng.uniform(45, 75)
        for s in sexo
    ])

    pas = rng.uniform(100, 160, size=n)
    pad = rng.uniform(60, 100, size=n)
    fc = rng.uniform(50, 100, size=n)

    df = pd.DataFrame({
        "id": np.arange(1, n + 1),
        "sexo": sexo,
        "idade": idade.astype(int),
        "circunferencia_cintura": np.round(cintura, 1),
        "circunferencia_quadril": np.round(quadril, 1),
        "circunferencia_braco": np.round(braco, 1),
        "circunferencia_coxa": np.round(coxa, 1),
        "pas": np.round(pas, 0).astype(int),
        "pad": np.round(pad, 0).astype(int),
        "fc": np.round(fc, 0).astype(int),
    })

    df["icq"] = df.apply(
        lambda r: calcular_icq(r["circunferencia_cintura"], r["circunferencia_quadril"]),
        axis=1,
    )
    df["classificacao_pressao"] = df.apply(
        lambda r: classificar_pressao(r["pas"], r["pad"]),
        axis=1,
    )
    df["risco_cintura"] = df.apply(
        lambda r: classificar_risco_cintura(r["sexo"], r["circunferencia_cintura"]),
        axis=1,
    )

    df.to_csv(caminho, index=False, encoding="utf-8")
    return df
