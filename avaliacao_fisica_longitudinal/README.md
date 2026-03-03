# Projeto: Avaliação Física Longitudinal com Streamlit

Este projeto cria um **dashboard interativo** para acompanhar a evolução física de **um indivíduo ao longo do tempo**.

> Objetivo principal: comparar cada pessoa com ela mesma (primeira avaliação, avaliação anterior e avaliação atual).

---

## 1) O que é Streamlit?

O **Streamlit** é uma biblioteca Python para criar aplicações web de dados de forma simples.

Com poucos comandos, você consegue:
- montar interface com barra lateral;
- mostrar tabelas e métricas;
- criar gráficos interativos;
- permitir upload e download de arquivos.

Você escreve Python e o Streamlit transforma isso em uma página web.

---

## 2) Estrutura do projeto

```bash
avaliacao_fisica_longitudinal/
│
├── app.py
├── utils.py
├── requirements.txt
├── README.md
├── exemplo_planilha.csv
└── data/
```

- **app.py**: interface principal e fluxo do dashboard.
- **utils.py**: funções de cálculo e organização de dados.
- **requirements.txt**: bibliotecas necessárias.
- **exemplo_planilha.csv**: arquivo exemplo para testes.
- **data/**: pasta reservada para futuros dados auxiliares.

---

## 3) Instalação do Python

Se você ainda não tiver Python:
1. Acesse: https://www.python.org/downloads/
2. Baixe a versão estável mais recente.
3. Durante instalação no Windows, marque a opção **"Add Python to PATH"**.

### Verificar se instalou corretamente
No terminal:

```bash
python --version
```

Se aparecer algo como `Python 3.x.x`, está tudo certo.

---

## 4) Criar ambiente virtual (recomendado)

Dentro da pasta do projeto, execute:

```bash
python -m venv venv
```

### Ativar ambiente virtual

**Windows:**

```bash
venv\Scripts\activate
```

**Mac/Linux:**

```bash
source venv/bin/activate
```

---

## 5) Instalar dependências

```bash
pip install -r requirements.txt
```

---

## 6) Executar o dashboard

```bash
streamlit run app.py
```

O terminal mostrará uma URL local (normalmente `http://localhost:8501`).
Abra no navegador.

---

## 7) Fluxo do programa (passo a passo)

1. O app tenta ler um CSV enviado na sidebar.
2. Se não houver upload, usa `exemplo_planilha.csv`.
3. Valida colunas obrigatórias.
4. Converte e organiza datas em ordem temporal.
5. Calcula automaticamente:
   - IMC
   - ICQ (cintura/quadril)
   - diferença bíceps contraído vs relaxado
6. Usuário escolhe **um único indivíduo**.
7. Usuário pode filtrar por intervalo de datas.
8. O app mostra 4 abas:
   - **Resumo Atual**
   - **Evolução Temporal**
   - **Análise de Circunferências**
   - **Composição Corporal**
9. Usuário pode baixar:
   - relatório resumido em CSV;
   - dados filtrados em CSV.

---

## 8) Formato da planilha CSV

### Colunas obrigatórias

- `nome`
- `data_avaliacao`
- `sexo`
- `idade`
- `peitoral`
- `cintura`
- `quadril`
- `coxa`
- `panturrilha`
- `biceps_contraido`
- `biceps_relaxado`
- `peso`
- `altura`

### Colunas opcionais (futuras)

- `percentual_gordura`
- `massa_magra`
- `massa_gorda`
- `agua_corporal`

Se essas colunas opcionais não existirem, o sistema continua funcionando normalmente.

---

## 9) Tratamento de erros implementado

O sistema mostra mensagens claras quando:
- faltam colunas obrigatórias;
- datas estão mal formatadas;
- altura é zero (evita divisão por zero no IMC).

---

## 10) Como adicionar novos indicadores no futuro

Para evoluir o projeto:

1. Crie uma nova função em `utils.py` com o cálculo do novo indicador.
2. Em `organizar_dados_longitudinais()`, adicione a nova coluna calculada.
3. Em `app.py`, inclua o novo indicador em:
   - métricas da aba de resumo;
   - opções da aba de evolução temporal;
   - relatório resumido (se fizer sentido).
4. Se depender de nova coluna no CSV, atualize validação e README.

Esse padrão deixa o código organizado e fácil para manutenção.

---

## 11) Dica para iniciantes

Se você está começando em programação, tente estudar nesta ordem:
1. Ler `utils.py` primeiro (funções pequenas e focadas).
2. Depois ler `app.py` para entender como a interface usa essas funções.
3. Fazer pequenas mudanças (por exemplo, mudar títulos de gráficos) e rodar novamente para ver o resultado.

Aprender com ciclos curtos de teste acelera muito o entendimento. 🚀
