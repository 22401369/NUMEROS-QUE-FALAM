# Secao 3 - Piramide etaria e envelhecimento (Censo 2022)
# ANA JULIA GOIS DO NASCIMENTO
#
# Aqui a variavel e a IDADE de cada pessoa. Como a tabela vem agrupada
# (quantas pessoas tem cada idade), as estatisticas sao calculadas com peso:
# cada idade "vale" a quantidade de pessoas que tem aquela idade.

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from layout import cabecalho
from estatisticas import ler_arquivo, fmt
from etl.tratar_piramide import tratar_tabela_9514, faixa_quinquenal

COLUNAS_UPLOAD = ["uf", "regiao", "idade", "sexo", "populacao"]
FAIXAS = [f"{i}-{i + 4}" for i in range(0, 100, 5)] + ["100+"]


@st.cache_data
def carregar_padrao():
    return pd.read_csv("dados/tratados/piramide_uf_2022.csv", dtype={"cod_uf": str})


def carregar(arquivo):
    if arquivo is None:
        return carregar_padrao()
    try:
        inicio = arquivo.read(200).decode("utf-8-sig", errors="ignore")
        arquivo.seek(0)
        if "Tabela 9514" in inicio:
            # arquivo cru exportado do SIDRA, passa pelo mesmo tratamento do ETL
            df = tratar_tabela_9514(arquivo)
        else:
            df = ler_arquivo(arquivo)
        faltam = [c for c in COLUNAS_UPLOAD if c not in df.columns]
        if faltam:
            st.error("Faltam colunas no arquivo: " + ", ".join(faltam) + ". Usando a base padrão.")
            return carregar_padrao()
        if "faixa_etaria" not in df.columns:
            df["faixa_etaria"] = df["idade"].apply(faixa_quinquenal)
        st.success(f"Arquivo carregado ({len(df)} linhas).")
        return df
    except Exception as erro:
        st.error(f"Não consegui ler o arquivo: {erro}. Usando a base padrão.")
        return carregar_padrao()


def estatisticas_ponderadas(idades, pesos):
    idades = np.array(idades, dtype=float)
    pesos = np.array(pesos, dtype=float)
    ordem = np.argsort(idades)
    idades, pesos = idades[ordem], pesos[ordem]
    total = pesos.sum()

    media = (idades * pesos).sum() / total
    variancia = (pesos * (idades - media) ** 2).sum() / total
    acumulado = np.cumsum(pesos) / total

    def quantil(p):
        return idades[np.searchsorted(acumulado, p)]

    q1, mediana, q3 = quantil(0.25), quantil(0.50), quantil(0.75)
    return {
        "media": media,
        "mediana": mediana,
        "moda": idades[np.argmax(pesos)],
        "q1": q1,
        "q3": q3,
        "iqr": q3 - q1,
        "amplitude": idades.max() - idades.min(),
        "desvio": np.sqrt(variancia),
    }


def indicadores(df):
    total = df["populacao"].sum()
    jovens = df.loc[df["idade"] <= 14, "populacao"].sum()
    idosos65 = df.loc[df["idade"] >= 65, "populacao"].sum()
    homens = df.loc[df["sexo"] == "Homens", "populacao"].sum()
    mulheres = df.loc[df["sexo"] == "Mulheres", "populacao"].sum()
    return {
        "total": total,
        "pct_jovens": jovens / total * 100,
        "pct_idosos": idosos65 / total * 100,
        "ind_envelhecimento": idosos65 / jovens * 100,  # idosos 65+ para cada 100 jovens de 0 a 14
        "razao_sexo": homens / mulheres * 100,          # homens para cada 100 mulheres
    }


def mostrar(filtros, arquivo=None):
    cabecalho("Pirâmide etária e envelhecimento", "Censo 2022, população por sexo e idade", "Seção 3 • ANA JULIA GOIS DO NASCIMENTO")

    base = carregar(arquivo)
    df = base[base["regiao"].isin(filtros["regioes"]) & base["uf"].isin(filtros["ufs"])]
    if df.empty:
        st.warning("Sem dados para os filtros.")
        return

    faixas_escolhidas = FAIXAS[filtros["faixa_ini"]: filtros["faixa_fim"] + 1]
    df_faixa = df[df["faixa_etaria"].isin(faixas_escolhidas)]
    if df_faixa.empty:
        st.warning("Não há registros para a faixa etária selecionada. Escolha um intervalo maior.")
        return

    ind = indicadores(df)  # indices usam todas as idades
    brasil = indicadores(base)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("População (UFs filtradas)", fmt(ind["total"]))
    k2.metric("Idosos 65+", f"{fmt(ind['pct_idosos'], 1)}%", f"{fmt(ind['pct_idosos'] - brasil['pct_idosos'], 1)} p.p. vs Brasil")
    k3.metric("Jovens 0 a 14", f"{fmt(ind['pct_jovens'], 1)}%", f"{fmt(ind['pct_jovens'] - brasil['pct_jovens'], 1)} p.p. vs Brasil")
    k4.metric("Índice de envelhecimento", fmt(ind["ind_envelhecimento"], 1),
              f"Brasil: {fmt(brasil['ind_envelhecimento'], 1)}", delta_color="off")
    st.caption("Índice de envelhecimento = (pessoas com 65 anos ou mais ÷ pessoas de 0 a 14 anos) × 100.")

    # ---- piramide
    pir = df_faixa.groupby(["faixa_etaria", "sexo"], as_index=False)["populacao"].sum()
    pir["ordem"] = pir["faixa_etaria"].apply(FAIXAS.index)
    pir = pir.sort_values("ordem")
    pir["pct"] = pir["populacao"] / ind["total"] * 100

    h = pir[pir["sexo"] == "Homens"]
    m = pir[pir["sexo"] == "Mulheres"]

    mostrar_pct = st.toggle("Mostrar em % da população", value=True)
    col = "pct" if mostrar_pct else "populacao"

    fig = go.Figure()
    fig.add_bar(y=h["faixa_etaria"], x=-h[col], orientation="h", name="Homens", marker_color="#155E75",
                customdata=h["populacao"], hovertemplate="Homens %{y}: %{customdata:,} pessoas<extra></extra>")
    fig.add_bar(y=m["faixa_etaria"], x=m[col], orientation="h", name="Mulheres", marker_color="#F59E0B",
                customdata=m["populacao"], hovertemplate="Mulheres %{y}: %{customdata:,} pessoas<extra></extra>")
    maximo = pir[col].max() * 1.1
    passos = np.linspace(0, maximo, 5)
    rotulos = [f"{v:.1f}%" if mostrar_pct else f"{v / 1e6:.1f} mi" for v in passos]
    fig.update_layout(
        barmode="relative", bargap=0.05, height=560,
        xaxis=dict(range=[-maximo, maximo], tickvals=list(-passos[::-1]) + list(passos[1:]),
                   ticktext=rotulos[::-1] + rotulos[1:], title="% da população" if mostrar_pct else "Pessoas"),
        yaxis=dict(title="Faixa etária", categoryorder="array", categoryarray=FAIXAS),
        legend=dict(orientation="h", y=1.05),
        title=f"Pirâmide etária 2022: {', '.join(filtros['ufs'])} ({filtros['faixa_texto']})",
    )
    st.plotly_chart(fig, width="stretch", theme=None)

    # ---- estatisticas da idade
    st.subheader(f"Estatísticas da idade ({filtros['faixa_texto']})")
    e = estatisticas_ponderadas(df_faixa["idade"], df_faixa["populacao"])
    c = st.columns(4)
    c[0].metric("Idade média", f"{fmt(e['media'], 1)} anos")
    c[1].metric("Idade mediana", f"{e['mediana']:.0f} anos")
    c[2].metric("Moda (idade mais comum)", f"{e['moda']:.0f} anos")
    c[3].metric("Desvio padrão", f"{fmt(e['desvio'], 1)} anos")
    c = st.columns(4)
    c[0].metric("Q1", f"{e['q1']:.0f} anos")
    c[1].metric("Q3", f"{e['q3']:.0f} anos")
    c[2].metric("IQR", f"{e['iqr']:.0f} anos")
    c[3].metric("Razão de sexo", f"{fmt(ind['razao_sexo'], 1)}", "homens p/ cada 100 mulheres", delta_color="off")
    st.markdown(
        f"Metade da população dessa faixa tem até **{e['mediana']:.0f} anos** e metade tem mais. "
        f"50% das pessoas estão entre **{e['q1']:.0f} e {e['q3']:.0f} anos** (IQR de {e['iqr']:.0f} anos). "
        "A base da pirâmide já é mais estreita que o meio: nascem menos crianças do que há 20 ou 30 anos."
    )

    # ---- comparacao entre UFs
    st.subheader("Índice de envelhecimento por estado")
    linhas = []
    for uf, g in base.groupby("uf"):
        i = indicadores(g)
        linhas.append({"uf": uf, "regiao": g["regiao"].iloc[0], "indice": i["ind_envelhecimento"], "pct_idosos": i["pct_idosos"]})
    todas = pd.DataFrame(linhas).sort_values("indice", ascending=False)
    todas["destaque"] = np.where(todas["uf"].isin(filtros["ufs"]), "UF selecionada", "Outras UFs")
    fig_ind = px.bar(todas, x="uf", y="indice", color="destaque",
                     color_discrete_map={"UF selecionada": "#0F766E", "Outras UFs": "#CBD5E1"},
                     labels={"uf": "UF", "indice": "Idosos 65+ para cada 100 jovens", "destaque": ""})
    fig_ind.add_hline(y=brasil["ind_envelhecimento"], line_dash="dash",
                      annotation_text=f"Brasil {brasil['ind_envelhecimento']:.1f}")
    fig_ind.update_layout(height=420)
    st.plotly_chart(fig_ind, width="stretch", theme=None)

    mais_velho = todas.iloc[0]
    st.markdown(
        f"O estado mais envelhecido do país é **{mais_velho['uf']}**, com {fmt(mais_velho['indice'], 1)} idosos "
        "para cada 100 jovens. Para os prefeitos, isso significa mais demanda por **saúde do idoso, "
        "acessibilidade urbana e transporte adaptado**, e menos pressão por novas vagas em creches."
    )
