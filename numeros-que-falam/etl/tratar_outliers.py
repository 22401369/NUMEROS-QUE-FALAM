"""
ETL da parte de outliers (MATHEUS FERREIRA BELTHODO)

Pega a base de crescimento ja tratada e marca, dentro de cada UF,
quais municipios sao outliers pela regra de 1,5 x IQR.
Gera tambem uma tabelinha com os limites de cada estado.

python etl/tratar_outliers.py
"""
import pandas as pd

entrada = "dados/tratados/crescimento_municipios.csv"
saida_municipios = "dados/tratados/outliers_crescimento.csv"
saida_limites = "dados/tratados/limites_outliers_uf.csv"


def limites_iqr(valores):
    q1 = valores.quantile(0.25)
    q3 = valores.quantile(0.75)
    iqr = q3 - q1
    return q1, q3, iqr, q1 - 1.5 * iqr, q3 + 1.5 * iqr


def classificar(df, coluna="crescimento_acumulado"):
    q1, q3, iqr, li, ls = limites_iqr(df[coluna])
    situacao = pd.Series("Normal", index=df.index)
    situacao[df[coluna] > ls] = "Outlier: cresceu demais"
    situacao[df[coluna] < li] = "Outlier: encolheu demais"
    return situacao


if __name__ == "__main__":
    df = pd.read_csv(entrada)

    linhas = []
    df["situacao_na_uf"] = ""
    for uf, grupo in df.groupby("uf"):
        q1, q3, iqr, li, ls = limites_iqr(grupo["crescimento_acumulado"])
        df.loc[grupo.index, "situacao_na_uf"] = classificar(grupo)
        n_out = (df.loc[grupo.index, "situacao_na_uf"] != "Normal").sum()
        linhas.append([uf, len(grupo), q1, q3, iqr, li, ls, n_out])

    limites = pd.DataFrame(linhas, columns=["uf", "municipios", "q1", "q3", "iqr",
                                            "limite_inferior", "limite_superior", "qtd_outliers"])
    limites = limites.round(2)

    # brasil inteiro tambem, pra comparar
    df["situacao_brasil"] = classificar(df)

    df.to_csv(saida_municipios, index=False)
    limites.to_csv(saida_limites, index=False)

    print(limites.to_string(index=False))
    print()
    print(df["situacao_brasil"].value_counts())
