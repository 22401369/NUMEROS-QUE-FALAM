"""
Secao 2 - Outliers de crescimento
MATHEUS FERREIRA BELTHODO

Ideia: usar a regra do 1,5 x IQR para achar as cidades que cresceram
exageradamente e as que encolheram demais, e mostrar como elas mexem na media.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

from layout import cabecalho
from estatisticas import calcular_estatisticas, fmt
from secoes.crescimento import carregar, aplicar_filtros, COLUNAS_UPLOAD  # mesma base da secao 1

COR = {"Normal": "#CBD5E1", "Outlier: cresceu demais": "#0F766E", "Outlier: encolheu demais": "#DC2626"}


def marcar_outliers(df, li, ls):
    df = df.copy()
    df["situacao"] = "Normal"
    df.loc[df["crescimento_acumulado"] > ls, "situacao"] = "Outlier: cresceu demais"
    df.loc[df["crescimento_acumulado"] < li, "situacao"] = "Outlier: encolheu demais"
    return df


def mostrar(filtros, arquivo=None):
    cabecalho("Outliers de crescimento", "Regra de 1,5 × IQR aplicada ao crescimento acumulado 2010-2022", "Seção 2 • MATHEUS FERREIRA BELTHODO")

    df = aplicar_filtros(carregar(arquivo), filtros)
    if len(df) < 4:
        st.warning("Poucos municípios com esses filtros para calcular quartis.")
        return

    comparar = st.radio("Calcular os limites de outlier:", ["Juntando todos os estados filtrados", "Dentro de cada estado"],
                        horizontal=True)

    est = calcular_estatisticas(df["crescimento_acumulado"])

    if comparar == "Dentro de cada estado":
        partes = []
        for uf, g in df.groupby("uf"):
            e = calcular_estatisticas(g["crescimento_acumulado"])
            partes.append(marcar_outliers(g, e["lim_inferior"], e["lim_superior"]))
        df = pd.concat(partes)
    else:
        df = marcar_outliers(df, est["lim_inferior"], est["lim_superior"])

    altos = df[df["situacao"] == "Outlier: cresceu demais"]
    baixos = df[df["situacao"] == "Outlier: encolheu demais"]
    normais = df[df["situacao"] == "Normal"]
    if normais.empty:
        st.warning("Todos os municípios foram classificados como outliers com os filtros atuais. Ajuste os filtros para comparar a média sem os outliers.")
        return

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Q1 | Q3", f"{fmt(est['q1'], 1)}% | {fmt(est['q3'], 1)}%")
    k2.metric("IQR", f"{fmt(est['iqr'], 2)} p.p.")
    k3.metric("Outliers que cresceram demais", len(altos))
    k4.metric("Outliers que encolheram demais", len(baixos))

    if comparar != "Dentro de cada estado":
        st.markdown(
            f"**Como calculamos:** IQR = Q3 - Q1 = {fmt(est['q3'], 2)} - {fmt(est['q1'], 2)} = **{fmt(est['iqr'], 2)}**. "
            f"Limite inferior = Q1 - 1,5 × IQR = **{fmt(est['lim_inferior'], 2)}%**. "
            f"Limite superior = Q3 + 1,5 × IQR = **{fmt(est['lim_superior'], 2)}%**. "
            "Qualquer cidade fora dessa faixa é outlier."
        )
    else:
        st.markdown("Cada estado tem seus próprios Q1, Q3 e limites. Assim um município é comparado só com os vizinhos do mesmo estado.")

    # boxplot
    fig_box = px.box(df, x="uf", y="crescimento_acumulado", points="outliers", color="uf",
                     hover_name="municipio", hover_data={"pop_2010": ":,", "pop_2022": ":,", "uf": False},
                     labels={"uf": "UF", "crescimento_acumulado": "Crescimento acumulado 2010-2022 (%)"})
    fig_box.update_layout(showlegend=False, height=480)
    fig_box.add_hline(y=0, line_dash="dot", line_color="gray")
    st.plotly_chart(fig_box, width="stretch", theme=None)
    st.caption("A caixa vai do Q1 ao Q3, a linha do meio é a mediana e os pontos soltos são os outliers. "
               "Passe o mouse para ver o nome da cidade.")

    # efeito dos outliers na media
    st.subheader("O quanto os outliers distorcem a média?")
    media_sem = normais["crescimento_acumulado"].mean()
    mediana_sem = normais["crescimento_acumulado"].median()
    efeito = pd.DataFrame({
        "": ["Com outliers", "Sem outliers"],
        "Média (%)": [df["crescimento_acumulado"].mean(), media_sem],
        "Mediana (%)": [df["crescimento_acumulado"].median(), mediana_sem],
        "Desvio padrão": [df["crescimento_acumulado"].std(), normais["crescimento_acumulado"].std()],
    }).round(2)
    c1, c2 = st.columns([2, 3])
    c1.dataframe(efeito, hide_index=True, width="stretch")
    dif_media = df["crescimento_acumulado"].mean() - media_sem
    dif_mediana = df["crescimento_acumulado"].median() - mediana_sem
    c2.markdown(
        f"Tirando os outliers, a média muda **{fmt(dif_media, 2)} p.p.** e a mediana muda só "
        f"**{fmt(dif_mediana, 2)} p.p.**. Isso mostra na prática que a **média é sensível a valores extremos** "
        "e a mediana é **robusta**. Por isso a gente recomenda usar a mediana como referência de crescimento típico "
        "e tratar os outliers como casos especiais no planejamento."
    )

    # dispersao tamanho x crescimento
    st.subheader("Tamanho da cidade x crescimento")
    fig_disp = px.scatter(df, x="pop_2010", y="crescimento_acumulado", color="situacao", color_discrete_map=COR,
                          hover_name="municipio", log_x=True, opacity=0.7,
                          labels={"pop_2010": "População em 2010 (escala log)", "crescimento_acumulado": "Crescimento (%)",
                                  "situacao": ""})
    fig_disp.update_layout(height=450, legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_disp, width="stretch", theme=None)
    if len(baixos) > 0:
        pequenos = (baixos["porte"] == "Pequeno (até 20 mil)").mean() * 100
        st.caption(f"{fmt(pequenos, 0)}% dos outliers que encolheram são cidades pequenas (até 20 mil habitantes). "
                   "Quanto menor a cidade, mais o crescimento varia: poucas pessoas a mais ou a menos já mudam muito o percentual.")

    # rankings
    st.subheader("Quem são os outliers")
    colunas = ["municipio", "uf", "pop_2010", "pop_2022", "crescimento_acumulado"]
    nomes = ["Município", "UF", "Pop. 2010", "Pop. 2022", "Crescimento (%)"]
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Cresceram exageradamente (top 15)**")
        t = altos.sort_values("crescimento_acumulado", ascending=False)[colunas].head(15)
        t.columns = nomes
        st.dataframe(t, hide_index=True, width="stretch")
    with c2:
        st.markdown("**Encolheram (os 15 que mais perderam)**")
        t = df.sort_values("crescimento_acumulado")[colunas + ["situacao"]].head(15)
        t.columns = nomes + ["Situação"]
        st.dataframe(t, hide_index=True, width="stretch")

    # outliers por porte
    st.markdown("**Outliers por porte de município**")
    tab = pd.crosstab(df["porte"], df["situacao"])
    st.dataframe(tab, width="stretch")
