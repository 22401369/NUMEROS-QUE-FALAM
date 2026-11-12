# ANA JULIA GOIS DO NASCIMENTO - tratamento da tabela 9514 do SIDRA (populacao por sexo e idade, Censo 2022)
# O arquivo vem do SIDRA com 4 linhas de cabecalho e um monte de notas no final,
# entao precisa limpar antes de usar.

import pandas as pd

SIGLAS = {
    "Rondônia": "RO", "Acre": "AC", "Amazonas": "AM", "Roraima": "RR", "Pará": "PA",
    "Amapá": "AP", "Tocantins": "TO", "Maranhão": "MA", "Piauí": "PI", "Ceará": "CE",
    "Rio Grande do Norte": "RN", "Paraíba": "PB", "Pernambuco": "PE", "Alagoas": "AL",
    "Sergipe": "SE", "Bahia": "BA", "Minas Gerais": "MG", "Espírito Santo": "ES",
    "Rio de Janeiro": "RJ", "São Paulo": "SP", "Paraná": "PR", "Santa Catarina": "SC",
    "Rio Grande do Sul": "RS", "Mato Grosso do Sul": "MS", "Mato Grosso": "MT",
    "Goiás": "GO", "Distrito Federal": "DF",
}
REGIOES = {"1": "Norte", "2": "Nordeste", "3": "Sudeste", "4": "Sul", "5": "Centro-Oeste"}


def idade_para_numero(texto):
    # "Menos de 1 ano" -> 0 ; "1 ano" -> 1 ; "37 anos" -> 37 ; "100 anos ou mais" -> 100
    if texto.startswith("Menos de 1"):
        return 0
    return int(texto.split(" ")[0])


def faixa_quinquenal(idade):
    if idade >= 100:
        return "100+"
    inicio = (idade // 5) * 5
    return f"{inicio}-{inicio + 4}"


def tratar_tabela_9514(caminho_ou_arquivo):
    bruto = pd.read_csv(caminho_ou_arquivo, sep=";", skiprows=4, dtype=str,
                        encoding="utf-8-sig", engine="python", on_bad_lines="skip")
    bruto.columns = ["cod_uf", "nome_uf", "idade_texto", "sexo", "populacao"]

    # tira as linhas de notas/legenda do rodape (elas nao tem sexo preenchido)
    df = bruto[bruto["sexo"].isin(["Homens", "Mulheres"])].copy()

    # no SIDRA "-" significa zero
    df["populacao"] = df["populacao"].replace("-", "0").astype(int)

    df["idade"] = df["idade_texto"].apply(idade_para_numero)
    df["faixa_etaria"] = df["idade"].apply(faixa_quinquenal)
    df["uf"] = df["nome_uf"].map(SIGLAS)
    df["regiao"] = df["cod_uf"].str[0].map(REGIOES)

    df = df[["cod_uf", "uf", "nome_uf", "regiao", "idade", "faixa_etaria", "sexo", "populacao"]]
    return df


if __name__ == "__main__":
    df = tratar_tabela_9514("dados/brutos/tabela9514_uf_idade_sexo_2022.csv")
    print(df.head())
    print("total de linhas:", len(df))
    print("UFs:", df["uf"].nunique())
    print("populacao total:", df["populacao"].sum())  # tem que dar 203.080.756
    df.to_csv("dados/tratados/piramide_uf_2022.csv", index=False)
