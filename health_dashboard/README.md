# Dashboard de Avaliação de Saúde – Educação Física

Projeto em **Python + Streamlit** para análise de indicadores antropométricos e cardiovasculares.

## Estrutura

```text
health_dashboard/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── dados_simulados.csv
└── utils.py
```

## Configuração do ambiente

### 1) Instalar Python (caso não tenha)
- Baixe em: https://www.python.org/downloads/
- No Windows, marque a opção **Add Python to PATH**.

### 2) Criar ambiente virtual
```bash
python -m venv venv
```

### 3) Ativar ambiente virtual
- **Windows**:
```bash
venv\Scripts\activate
```
- **Mac/Linux**:
```bash
source venv/bin/activate
```

### 4) Instalar dependências
```bash
pip install -r requirements.txt
```

### 5) Executar o projeto
```bash
streamlit run app.py
```

## Funcionalidades
- Filtros por sexo, faixa etária, PAS e FC.
- Métricas com médias de PAS, PAD, FC, cintura e ICQ.
- Cálculos automáticos: ICQ, classificação de risco por cintura e classificação de pressão arterial.
- Visualizações interativas com Plotly:
  - Histograma de PAS
  - Boxplot de cintura por sexo
  - Scatterplot PAS vs cintura
  - Barras com classificações de pressão
  - Heatmap de correlação
- Upload de CSV próprio
- Download do dataset filtrado

## Regras de classificação da pressão
- **Hipertensão Estágio 2**: PAS ≥ 140 ou PAD ≥ 90
- **Hipertensão Estágio 1**: PAS 130–139 ou PAD 80–89
- **Elevada**: PAS 120–129 e PAD < 80
- **Normal**: abaixo disso

## Observações
- O arquivo `data/dados_simulados.csv` é gerado automaticamente caso não exista.
- Para CSV próprio, as colunas mínimas obrigatórias são:
  - `id, sexo, idade, circunferencia_cintura, circunferencia_quadril, circunferencia_braco, circunferencia_coxa, pas, pad, fc`
