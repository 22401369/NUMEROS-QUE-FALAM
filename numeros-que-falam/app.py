import os
from pathlib import Path

# Garante que os caminhos relativos funcionem mesmo quando o app for iniciado
# a partir de outra pasta (por exemplo, pelo VS Code ou atalho).
PASTA_PROJETO = Path(__file__).resolve().parent
os.chdir(PASTA_PROJETO)

import streamlit as st
import pandas as pd

from secoes import inicio, crescimento, outliers, piramide, projecao
from layout import aplicar_estilo, configurar_graficos

st.set_page_config(page_title="Radar Urbano | Crescimento Demográfico", page_icon="📊", layout="wide")
aplicar_estilo()
configurar_graficos()

REGIOES_UF = {
    "Norte": ["AC", "AM", "AP", "PA", "RO", "RR", "TO"],
    "Nordeste": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
    "Sudeste": ["ES", "MG", "RJ", "SP"],
    "Sul": ["PR", "RS", "SC"],
    "Centro-Oeste": ["DF", "GO", "MS", "MT"],
}
# estados dos prefeitos do cenario (Curitiba, Porto Alegre, BH, Salvador, Florianopolis)
UFS_PERSONAS = ["BA", "MG", "PR", "RS", "SC"]
FAIXAS = [f"{i}-{i + 4}" for i in range(0, 100, 5)] + ["100+"]

PAGINAS = {
    "Início": inicio,
    "1. Crescimento dos municípios": crescimento,
    "2. Outliers de crescimento": outliers,
    "3. Pirâmide etária e envelhecimento": piramide,
    "4. Evolução, projeção e mapa": projecao,
}

# ---------------- barra lateral ----------------
st.sidebar.image("imagens/logo.png", width="stretch")
st.sidebar.caption("Startup de análise de dados • Indicador: Crescimento Demográfico")

ICONES = {
    "Início": ":material/home:",
    "1. Crescimento dos municípios": ":material/trending_up:",
    "2. Outliers de crescimento": ":material/scatter_plot:",
    "3. Pirâmide etária e envelhecimento": ":material/groups:",
    "4. Evolução, projeção e mapa": ":material/map:",
}
st.sidebar.subheader("Navegação")
pagina = st.sidebar.radio("Navegação", list(PAGINAS.keys()), format_func=lambda p: f"{ICONES[p]} {p}",
                          label_visibility="collapsed")

st.sidebar.divider()
st.sidebar.subheader("Filtros")
st.sidebar.caption("Região e UF valem para todas as telas.")

regioes = st.sidebar.multiselect("Região", list(REGIOES_UF.keys()), default=list(REGIOES_UF.keys()))

opcoes_uf = sorted([uf for r in regioes for uf in REGIOES_UF[r]])
padrao_uf = [uf for uf in UFS_PERSONAS if uf in opcoes_uf]
ufs = st.sidebar.multiselect("Unidade da Federação", opcoes_uf, default=padrao_uf,
                             help="Vem marcado com os estados das capitais do cenário. Deixe vazio para usar todas as UFs das regiões escolhidas.")
if not ufs:
    ufs = opcoes_uf

faixa = st.sidebar.select_slider("Faixa etária (tela 3)", options=FAIXAS, value=("0-4", "100+"))

anos = st.sidebar.multiselect("Anos de Censo (tela 4)", [1980, 1991, 2000, 2010, 2022], default=[1980, 1991, 2000, 2010, 2022])
if not anos:
    anos = [1980, 1991, 2000, 2010, 2022]

portes = st.sidebar.multiselect(
    "Porte do município (telas 1 e 2)",
    ["Pequeno (até 20 mil)", "Médio (20 a 100 mil)", "Grande (100 a 500 mil)", "Metrópole (mais de 500 mil)"],
    default=["Pequeno (até 20 mil)", "Médio (20 a 100 mil)", "Grande (100 a 500 mil)", "Metrópole (mais de 500 mil)"],
)

filtros = {
    "regioes": regioes,
    "ufs": ufs,
    "faixa_ini": FAIXAS.index(faixa[0]),
    "faixa_fim": FAIXAS.index(faixa[1]),
    "faixa_texto": f"{faixa[0]} até {faixa[1]} anos",
    "anos": sorted(anos),
    "portes": portes,
}

# upload da base da pagina atual (opcional)
arquivo = None
modulo = PAGINAS[pagina]
if hasattr(modulo, "COLUNAS_UPLOAD"):
    st.sidebar.divider()
    st.sidebar.subheader("Upload de dados")
    arquivo = st.sidebar.file_uploader(
        "Enviar base desta seção (CSV ou XLSX)", type=["csv", "xlsx"], key="upload_" + pagina
    )
    st.sidebar.caption("Colunas esperadas: " + ", ".join(modulo.COLUNAS_UPLOAD))
    st.sidebar.caption("Sem upload, o app usa a base do IBGE que já está na pasta dados/tratados.")

st.sidebar.divider()
st.sidebar.caption("Fonte: IBGE, Censos Demográficos 1980 a 2022 (SIDRA)")

# ---------------- conteudo ----------------
modulo.mostrar(filtros, arquivo)
