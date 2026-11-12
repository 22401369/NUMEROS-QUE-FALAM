# Secao 4 - Evolucao dos censos, projecao simples, mapa e noticias
# MATHEUS FERREIRA BELTHODO

import json
import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from layout import cabecalho, CORES
from estatisticas import ler_arquivo, fmt

COLUNAS_UPLOAD = ["uf", "regiao", "ano", "populacao"]

NOTICIAS = [
    {
        "titulo": "População do país vai parar de crescer em 2041",
        "fonte": "Agência de Notícias IBGE (ago/2024)",
        "resumo": "Nas Projeções da População, o IBGE estima que o Brasil chega ao pico de habitantes no começo "
                  "da década de 2040 e depois começa a diminuir, com cada vez mais idosos.",
        "link": "https://agenciadenoticias.ibge.gov.br/pt/agencia-noticias/41056-populacao-do-pais-vai-parar-de-crescer-em-2041.html",
    },
    {
        "titulo": "População brasileira tem menor ritmo de crescimento desde 1872, aponta Censo",
        "fonte": "Forbes Brasil (jun/2023)",
        "resumo": "O Censo 2022 contou 203 milhões de pessoas, com crescimento de 0,52% ao ano, o menor "
                  "da série histórica dos censos.",
        "link": "https://forbes.com.br/forbes-money/2023/06/populacao-brasileira-tem-menor-ritmo-de-crescimento-desde-1872-aponta-censo/",
    },
    {
        "titulo": "Novo Censo: Brasil tem envelhecimento recorde e idosos já somam quase 11% da população",
        "fonte": "Gazeta do Povo (out/2023)",
        "resumo": "A população com 65 anos ou mais cresceu cerca de 57% em 12 anos, enquanto o número de "
                  "crianças diminuiu.",
        "link": "https://www.gazetadopovo.com.br/vida-e-cidadania/novo-censo-brasil-tem-envelhecimento-recorde-e-idosos-ja-somam-quase-11-da-populacao/",
    },
    {
        "titulo": "Censo 2022: Boa Vista e Florianópolis têm aumento populacional superior a 20% em 12 anos",
        "fonte": "CNN Brasil (jun/2023)",
        "resumo": "Enquanto algumas capitais perderam moradores, Florianópolis e Boa Vista estão entre as "
                  "que mais cresceram no país.",
        "link": "https://www.cnnbrasil.com.br/nacional/censo-2022-boa-vista-e-florianopolis-tem-aumento-populacional-superior-a-20-em-12-anos/",
    },
    {
        "titulo": "Censo 2022: o que explica a queda populacional em diferentes capitais",
        "fonte": "Gazeta SP (2023)",
        "resumo": "Reportagem sobre os motivos que levaram várias capitais a perder moradores entre 2010 e 2022, "
                  "como Salvador, Porto Alegre e Belo Horizonte.",
        "link": "https://www.gazetasp.com.br/brasil/censo-2022-o-que-explica-a-queda-populacional-em-diferentes-capitais/",
    },
    {
        "titulo": "Somos 203 milhões de pessoas no Brasil",
        "fonte": "Revista Pesquisa FAPESP (2023)",
        "resumo": "Reportagem sobre os primeiros resultados do Censo 2022 e a transição demográfica brasileira.",
        "link": "https://revistapesquisa.fapesp.br/somos-203-milhoes-de-pessoas-no-brasil/",
    },
]


@st.cache_data
def carregar_serie():
    return pd.read_csv("dados/tratados/serie_censos_uf.csv")


@st.cache_data
def carregar_mapa():
    with open("dados/brutos/brasil_uf.geojson", encoding="utf-8") as f:
        return json.load(f)


def projetar(serie_uf, ano_final):
    # projecao geometrica: P(t) = P2022 * (1 + r) ^ (t - 2022)
    # r = taxa anual observada entre 2010 e 2022
    p2010 = serie_uf.loc[serie_uf["ano"] == 2010, "populacao"].iloc[0]
    p2022 = serie_uf.loc[serie_uf["ano"] == 2022, "populacao"].iloc[0]
    r = (p2022 / p2010) ** (1 / 12) - 1
    anos = np.arange(2022, ano_final + 1)
    return pd.DataFrame({"ano": anos, "populacao": p2022 * (1 + r) ** (anos - 2022), "taxa": r * 100})


def mostrar(filtros, arquivo=None):
    cabecalho("Evolução, projeção e mapa", "Censos de 1980 a 2022 e uma projeção simples para os próximos anos", "Seção 4 • MATHEUS FERREIRA BELTHODO")

    serie = carregar_serie()
    if arquivo is not None:
        try:
            enviado = ler_arquivo(arquivo)
            if all(c in enviado.columns for c in COLUNAS_UPLOAD):
                serie = enviado
                st.success("Série enviada carregada.")
            else:
                st.error("O arquivo precisa ter as colunas: " + ", ".join(COLUNAS_UPLOAD))
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")

    sel = serie[serie["uf"].isin(filtros["ufs"]) & serie["regiao"].isin(filtros["regioes"])]
    sel_anos = sel[sel["ano"].isin(filtros["anos"])]

    if sel.empty:
        st.warning("Sem dados para os filtros.")
        return

    # ---- linha do tempo + projecao
    st.subheader("Evolução da população nos Censos")
    c1, c2 = st.columns([1, 3])
    with c1:
        horizonte = st.slider("Projetar até", 2025, 2050, 2040, step=5)
        escala = st.radio("Eixo Y", ["Milhões de habitantes", "Índice (1980 = 100)"])
        st.caption("A projeção usa a taxa geométrica anual 2010-2022 de cada estado, como se ela continuasse igual.")

    fig = go.Figure()
    cores = CORES
    for i, (uf, g) in enumerate(sel.groupby("uf")):
        g = g.sort_values("ano")
        g_anos = g[g["ano"].isin(filtros["anos"])]
        proj = projetar(g, horizonte) if {2010, 2022} <= set(g["ano"]) else None
        base80 = g.loc[g["ano"] == g["ano"].min(), "populacao"].iloc[0]
        y = g_anos["populacao"] / 1e6 if escala.startswith("Milhões") else g_anos["populacao"] / base80 * 100
        cor = cores[i % len(cores)]
        fig.add_scatter(x=g_anos["ano"], y=y, mode="lines+markers", name=uf, line=dict(color=cor, width=3))
        if proj is not None:
            yp = proj["populacao"] / 1e6 if escala.startswith("Milhões") else proj["populacao"] / base80 * 100
            fig.add_scatter(x=proj["ano"], y=yp, mode="lines", name=f"{uf} (projeção)",
                            line=dict(color=cor, dash="dash"), showlegend=False,
                            hovertemplate=f"{uf} projeção %{{x}}: %{{y:.2f}}<extra></extra>")
    fig.add_vrect(x0=2022, x1=horizonte, fillcolor="lightgray", opacity=0.2, line_width=0,
                  annotation_text="projeção", annotation_position="top left")
    fig.update_layout(height=480, xaxis_title="Ano", yaxis_title=escala, legend=dict(orientation="h", y=1.1))
    c2.plotly_chart(fig, width="stretch", theme=None)

    # tabela de taxas por periodo intercensitario
    st.markdown("**Taxa geométrica de crescimento anual (%) entre um Censo e outro**")
    taxas = sel.dropna(subset=["taxa_geometrica_anual"]).copy()
    taxas["periodo"] = taxas.groupby("uf")["ano"].shift(1).fillna(1980).astype(int).astype(str) + "-" + taxas["ano"].astype(str)
    tabela = taxas.pivot(index="uf", columns="periodo", values="taxa_geometrica_anual")
    try:
        # A formatação com .style depende da biblioteca Jinja2.
        st.dataframe(tabela.style.format("{:.2f}").background_gradient(cmap="RdYlGn", axis=None), width="stretch")
    except (ImportError, AttributeError):
        # Alternativa para ambientes sem Jinja2: mostra a tabela sem o gradiente.
        st.dataframe(tabela.round(2), width="stretch")
    if "2010-2022" in tabela.columns:
        menor_da_serie = tabela.idxmin(axis=1) == "2010-2022"
        excecoes = list(tabela.index[~menor_da_serie])
        texto_exc = f" A exceção é **{', '.join(excecoes)}**, que cresceu mais rápido do que em algum período anterior." if excecoes else ""
        st.markdown(f"Em **{menor_da_serie.sum()} de {len(tabela)}** estados selecionados, o período 2010-2022 teve a menor taxa da série.{texto_exc}")
    st.markdown(
        "Entre 1980 e 1991 o Brasil crescia 1,77% ao ano; entre 2010 e 2022 cresceu só **0,52% ao ano**. "
        "Atenção: nossa projeção é só uma extrapolação. O IBGE, que considera natalidade, mortalidade e migração, "
        "projeta que a população do Brasil vai **parar de crescer por volta de 2041** e depois diminuir."
    )

    # tabela da projecao
    linhas = []
    for uf, g in sel.groupby("uf"):
        if {2010, 2022} <= set(g["ano"]):
            p = projetar(g, horizonte)
            linhas.append([uf, g.loc[g["ano"] == 2022, "populacao"].iloc[0], p["taxa"].iloc[0], p["populacao"].iloc[-1]])
    proj_tab = pd.DataFrame(linhas, columns=["UF", "Pop. 2022", "Taxa anual 2010-2022 (%)", f"Projeção {horizonte}"])
    proj_tab["Pop. 2022"] = proj_tab["Pop. 2022"].apply(fmt)
    proj_tab["Taxa anual 2010-2022 (%)"] = proj_tab["Taxa anual 2010-2022 (%)"].round(3)
    proj_tab[f"Projeção {horizonte}"] = proj_tab[f"Projeção {horizonte}"].apply(fmt)
    st.dataframe(proj_tab, hide_index=True, width="stretch")

    # ---- mapa
    st.subheader("Mapa de calor do crescimento por UF")
    indicador = st.selectbox("Indicador do mapa", ["Crescimento acumulado 2010-2022 (%)", "Taxa geométrica anual 2010-2022 (%)"])
    s22 = serie[serie["ano"] == 2022][["uf", "nome_uf", "regiao", "taxa_geometrica_anual"]].copy() if "nome_uf" in serie.columns \
        else serie[serie["ano"] == 2022][["uf", "regiao", "taxa_geometrica_anual"]].copy()
    p10 = serie[serie["ano"] == 2010][["uf", "populacao"]].rename(columns={"populacao": "p10"})
    p22 = serie[serie["ano"] == 2022][["uf", "populacao"]].rename(columns={"populacao": "p22"})
    mapa_df = s22.merge(p10, on="uf").merge(p22, on="uf")
    mapa_df["crescimento"] = (mapa_df["p22"] / mapa_df["p10"] - 1) * 100
    mapa_df = mapa_df[mapa_df["regiao"].isin(filtros["regioes"])]
    coluna = "crescimento" if indicador.startswith("Crescimento") else "taxa_geometrica_anual"

    fig_mapa = px.choropleth(
        mapa_df, geojson=carregar_mapa(), locations="uf", featureidkey="properties.sigla",
        color=coluna, color_continuous_scale="Tealgrn", hover_name="uf",
        hover_data={"p10": ":,", "p22": ":,", "crescimento": ":.2f", "uf": False},
        labels={"crescimento": "Crescimento (%)", "taxa_geometrica_anual": "Taxa anual (%)", "p10": "Pop. 2010", "p22": "Pop. 2022"},
    )
    fig_mapa.update_geos(fitbounds="locations", visible=False)
    fig_mapa.update_layout(height=550, margin=dict(l=0, r=0, t=0, b=0))
    c1, c2 = st.columns([3, 2])
    c1.plotly_chart(fig_mapa, width="stretch", theme=None)
    ranking = mapa_df.sort_values("crescimento", ascending=False)[["uf", "crescimento"]]
    ranking.columns = ["UF", "Crescimento 2010-2022 (%)"]
    c2.dataframe(ranking.round(2), hide_index=True, width="stretch", height=550)

    if mapa_df.empty:
        st.warning("Não há dados suficientes para montar o mapa com os filtros selecionados.")
        return

    maior = mapa_df.sort_values("crescimento").iloc[-1]
    menor = mapa_df.sort_values("crescimento").iloc[0]
    st.markdown(f"O estado que mais cresceu foi **{maior['uf']} ({fmt(maior['crescimento'], 1)}%)** e o que menos cresceu foi "
                f"**{menor['uf']} ({fmt(menor['crescimento'], 1)}%)**. O Norte e o Centro-Oeste continuam puxando o crescimento, "
                "enquanto Sul e Sudeste crescem devagar e já envelhecem mais rápido.")

    # ---- noticias
    st.divider()
    st.subheader("Na imprensa: transição demográfica e expansão urbana")
    imagens = ["imagens/infografico_brasil_2010_2022.png", "imagens/infografico_capitais.png", "imagens/infografico_idosos.png"]
    cols = st.columns(3)
    for col, img in zip(cols, imagens):
        if os.path.exists(img):
            col.image(img, width="stretch")

    # fotos de expansao urbana (coloque os arquivos .jpg/.png na pasta imagens/fotos)
    # o nome do arquivo vira a legenda, ex: "Vista aérea de Florianópolis.jpg"
    pasta_fotos = "imagens/fotos"
    if os.path.isdir(pasta_fotos):
        fotos = sorted(f for f in os.listdir(pasta_fotos) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")))
        if fotos:
            st.markdown("**Expansão urbana nas capitais**")
            cols = st.columns(min(len(fotos), 3))
            for i, foto in enumerate(fotos):
                legenda = os.path.splitext(foto)[0]
                cols[i % len(cols)].image(os.path.join(pasta_fotos, foto), caption=legenda, width="stretch")

    for i in range(0, len(NOTICIAS), 2):
        cols = st.columns(2)
        for col, n in zip(cols, NOTICIAS[i:i + 2]):
            with col.container(border=True):
                st.markdown(f"**{n['titulo']}**")
                st.caption(n["fonte"])
                st.write(n["resumo"])
                st.markdown(f"[Ler a matéria]({n['link']})")
