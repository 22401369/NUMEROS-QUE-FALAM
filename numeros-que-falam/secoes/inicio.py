import streamlit as st
from layout import cabecalho


def mostrar(filtros, arquivo=None):
    cabecalho("O Brasil que cresce e o Brasil que encolhe", "Painel de crescimento demográfico para os prefeitos das capitais • Dados do IBGE", "Projeto Integrador • Números que Falam")
    st.markdown(
        "Somos a **Radar Urbano**, uma startup de análise de dados. Fomos contratados pelos prefeitos "
        "de cinco capitais para ajudar na revisão dos **Planos Diretores** e na divisão do orçamento "
        "de saúde e infraestrutura urbana."
    )

    c1, c2 = st.columns([3, 2])
    with c1:
        st.subheader("Nossos clientes")
        st.markdown(
            """
| Persona | Cargo |
|---|---|
| Carlos | Prefeito de Curitiba (PR) |
| Eduardo | Prefeito de Porto Alegre (RS) |
| Elisa | Prefeita de Belo Horizonte (MG) |
| Jorge | Prefeito de Salvador (BA) |
| Roberto | Prefeito de Florianópolis (SC) |
"""
        )
        st.subheader("Perguntas que vamos responder")
        st.markdown(
            "1. Qual é a **taxa média de crescimento populacional acumulada** por cidade?\n"
            "2. Onde estão os **outliers de crescimento**: cidades que cresceram exageradamente e cidades que encolheram?\n"
            "3. Quão rápido a população está **envelhecendo** nesses estados?\n"
            "4. Para onde a população caminha nos próximos anos?"
        )

    with c2:
        st.subheader("Equipe")
        st.markdown(
            """
| Integrante | Parte no painel |
|---|---|
| ALEXANDRE LUIZ SILVA FREITAS | Crescimento dos municípios e estatísticas |
| MATHEUS FERREIRA BELTHODO | Outliers, evolução, projeção e mapa |
| ANA JULIA GOIS DO NASCIMENTO | Pirâmide etária, envelhecimento e infográficos/notícias |
"""
        )
        st.info("Use o menu da barra lateral para navegar. Região e UF valem para todas as telas; "
                "Porte vale para as telas 1 e 2, Faixa etária para a 3 e Anos de Censo para a 4.")

    st.subheader("De onde vêm os dados")
    st.markdown(
        "- **Censo 2010 e Censo 2022**: população residente de 5.565 municípios (IBGE, tabela 4709 do SIDRA)\n"
        "- **Censo 2022 por sexo e idade**: tabela 9514 do SIDRA, por UF\n"
        "- **Série histórica dos Censos 1980, 1991, 2000 e 2010**: tabela 1286 do SIDRA\n"
        "- Os 5 municípios criados depois de 2010 não entram no cálculo de crescimento (não existiam no Censo 2010)"
    )
