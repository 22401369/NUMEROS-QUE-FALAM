# MATHEUS FERREIRA BELTHODO
# Monta a serie historica dos censos por UF (1980, 1991, 2000, 2010 e 2022)
# 1980 a 2010: tabela 1286 do SIDRA
# 2022: soma dos municipios da tabela 4709 (Censo 2022)

import pandas as pd

siglas = {
    "Rondônia": "RO", "Acre": "AC", "Amazonas": "AM", "Roraima": "RR", "Pará": "PA",
    "Amapá": "AP", "Tocantins": "TO", "Maranhão": "MA", "Piauí": "PI", "Ceará": "CE",
    "Rio Grande do Norte": "RN", "Paraíba": "PB", "Pernambuco": "PE", "Alagoas": "AL",
    "Sergipe": "SE", "Bahia": "BA", "Minas Gerais": "MG", "Espírito Santo": "ES",
    "Rio de Janeiro": "RJ", "São Paulo": "SP", "Paraná": "PR", "Santa Catarina": "SC",
    "Rio Grande do Sul": "RS", "Mato Grosso do Sul": "MS", "Mato Grosso": "MT",
    "Goiás": "GO", "Distrito Federal": "DF",
}
regiao_por_uf = {
    "RO": "Norte", "AC": "Norte", "AM": "Norte", "RR": "Norte", "PA": "Norte", "AP": "Norte", "TO": "Norte",
    "MA": "Nordeste", "PI": "Nordeste", "CE": "Nordeste", "RN": "Nordeste", "PB": "Nordeste",
    "PE": "Nordeste", "AL": "Nordeste", "SE": "Nordeste", "BA": "Nordeste",
    "MG": "Sudeste", "ES": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "SC": "Sul", "RS": "Sul",
    "MS": "Centro-Oeste", "MT": "Centro-Oeste", "GO": "Centro-Oeste", "DF": "Centro-Oeste",
}

# ---- censos antigos
antigos = pd.read_csv("dados/brutos/tabela1286_censos_uf.csv", sep=";", skiprows=2,
                      skipfooter=1, engine="python")
antigos = antigos.rename(columns={"Unidade da Federação": "nome_uf"})
antigos["uf"] = antigos["nome_uf"].map(siglas)
antigos = antigos.melt(id_vars=["nome_uf", "uf"], var_name="ano", value_name="populacao")
antigos["ano"] = antigos["ano"].astype(int)

# ---- censo 2022 (somando os municipios, inclusive os 5 criados depois de 2010)
mun = pd.read_csv("dados/brutos/tabela4709_municipios.csv", encoding="utf-8-sig")
mun.columns = ["cod_mun", "municipio", "populacao"]
mun["uf"] = mun["municipio"].str.extract(r"\(([A-Z]{2})\)$")[0]
c2022 = mun.groupby("uf", as_index=False)["populacao"].sum()
c2022["ano"] = 2022
nomes = antigos[["uf", "nome_uf"]].drop_duplicates()
c2022 = c2022.merge(nomes, on="uf")

serie = pd.concat([antigos, c2022[["nome_uf", "uf", "ano", "populacao"]]], ignore_index=True)
serie["regiao"] = serie["uf"].map(regiao_por_uf)
serie = serie.sort_values(["uf", "ano"]).reset_index(drop=True)

# taxa geometrica anual entre um censo e o anterior
# r = (P_final / P_inicial) ^ (1 / anos) - 1
serie["pop_anterior"] = serie.groupby("uf")["populacao"].shift(1)
serie["ano_anterior"] = serie.groupby("uf")["ano"].shift(1)
anos = serie["ano"] - serie["ano_anterior"]
serie["taxa_geometrica_anual"] = ((serie["populacao"] / serie["pop_anterior"]) ** (1 / anos) - 1) * 100
serie["taxa_geometrica_anual"] = serie["taxa_geometrica_anual"].round(3)
serie = serie.drop(columns=["pop_anterior", "ano_anterior"])

print(serie.groupby("ano")["populacao"].sum())
serie.to_csv("dados/tratados/serie_censos_uf.csv", index=False)
print("ok, serie salva")
