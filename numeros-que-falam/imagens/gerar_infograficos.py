# Gera as imagens/infograficos da secao de noticias (ANA JULIA GOIS DO NASCIMENTO)
# python imagens/gerar_infograficos.py

import pandas as pd
import matplotlib.pyplot as plt

serie = pd.read_csv("dados/tratados/serie_censos_uf.csv")
mun = pd.read_csv("dados/tratados/crescimento_municipios.csv")
pir = pd.read_csv("dados/tratados/piramide_uf_2022.csv")

AZUL = "#1E293B"
FUNDO = "#FFFFFF"


def salvar(fig, nome):
    fig.savefig("imagens/" + nome, dpi=150, bbox_inches="tight", facecolor=FUNDO)
    plt.close(fig)
    print("salvo", nome)


# 1) Brasil nos censos
tot = serie.groupby("ano")["populacao"].sum() / 1e6
fig, ax = plt.subplots(figsize=(6, 4), facecolor=FUNDO)
ax.set_facecolor(FUNDO)
barras = ax.bar(tot.index.astype(str), tot.values, color=["#99D5CF"] * 4 + ["#0F766E"])
for b, v in zip(barras, tot.values):
    ax.text(b.get_x() + b.get_width() / 2, v + 2, f"{v:.1f}".replace(".", ","), ha="center", fontsize=11, color=AZUL)
ax.set_title("Brasil: população nos Censos (milhões)", fontsize=13, color=AZUL, weight="bold")
ax.text(0.5, -0.18, "Entre 2010 e 2022: +0,52% ao ano, o menor ritmo da história", transform=ax.transAxes,
        ha="center", fontsize=10, color=AZUL)
ax.spines[["top", "right", "left"]].set_visible(False)
ax.set_yticks([])
salvar(fig, "infografico_brasil_2010_2022.png")

# 2) capitais do cenario
caps = mun[mun["municipio"].isin(["Curitiba", "Porto Alegre", "Belo Horizonte", "Salvador", "Florianópolis"]) & mun["capital"]]
caps = caps.sort_values("crescimento_acumulado")
fig, ax = plt.subplots(figsize=(6, 4), facecolor=FUNDO)
ax.set_facecolor(FUNDO)
cores = ["#DC2626" if v < 0 else "#0F766E" for v in caps["crescimento_acumulado"]]
ax.barh(caps["municipio"], caps["crescimento_acumulado"], color=cores)
for y, v in enumerate(caps["crescimento_acumulado"]):
    ax.text(v + (0.8 if v >= 0 else -0.8), y, f"{v:+.1f}%".replace(".", ","), va="center",
            ha="left" if v >= 0 else "right", fontsize=11, color=AZUL)
ax.axvline(0, color="gray", lw=1)
ax.set_xlim(-18, 36)
ax.set_title("Capitais do cenário: crescimento 2010-2022", fontsize=13, color=AZUL, weight="bold")
ax.spines[["top", "right", "bottom"]].set_visible(False)
ax.set_xticks([])
salvar(fig, "infografico_capitais.png")

# 3) idosos x criancas
fig, ax = plt.subplots(figsize=(6, 4), facecolor=FUNDO)
ax.set_facecolor(FUNDO)
idosos = pir.loc[pir["idade"] >= 65, "populacao"].sum()
criancas = pir.loc[pir["idade"] <= 14, "populacao"].sum()
ax.bar(["Crianças (0 a 14)", "Idosos (65+)"], [criancas / 1e6, idosos / 1e6], color=["#99D5CF", "#F59E0B"])
ax.text(0, criancas / 1e6 + 1, f"{criancas / 1e6:.1f} mi".replace(".", ","), ha="center", fontsize=12, color=AZUL)
ax.text(1, idosos / 1e6 + 1, f"{idosos / 1e6:.1f} mi".replace(".", ","), ha="center", fontsize=12, color=AZUL)
ax.set_ylim(0, criancas / 1e6 * 1.2)
ax.set_title("Censo 2022: para cada 100 crianças, %d idosos" % round(idosos / criancas * 100),
             fontsize=13, color=AZUL, weight="bold")
ax.spines[["top", "right", "left"]].set_visible(False)
ax.set_yticks([])
salvar(fig, "infografico_idosos.png")
