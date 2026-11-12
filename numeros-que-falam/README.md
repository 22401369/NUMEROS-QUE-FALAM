# Números que Falam: Crescimento Demográfico

Projeto Integrador Python e Matemática (Etapa 3), desenvolvido por uma equipe de 3 integrantes.
Dashboard em Streamlit sobre o crescimento da população dos municípios brasileiros entre o Censo 2010 e o Censo 2022, feito pela nossa "startup" **Radar Urbano** para os prefeitos de Curitiba, Porto Alegre, Belo Horizonte, Salvador e Florianópolis.

## Integrantes

| Integrante | Parte | Arquivos |
|---|---|---|
| ALEXANDRE LUIZ SILVA FREITAS | Crescimento dos municípios e estatísticas | `etl/tratar_crescimento.py`, `secoes/crescimento.py`, `estatisticas.py` |
| MATHEUS FERREIRA BELTHODO | Outliers, evolução, projeção e mapa | `etl/tratar_outliers.py`, `secoes/outliers.py`, `etl/tratar_serie.py`, `secoes/projecao.py` |
| ANA JULIA GOIS DO NASCIMENTO | Pirâmide etária, envelhecimento e infográficos/notícias | `etl/tratar_piramide.py`, `secoes/piramide.py`, `imagens/gerar_infograficos.py` |

## Como rodar

```bash
pip install -r requirements.txt
streamlit run app.py
```

O app abre em http://localhost:8501. Precisa de internet só para desenhar o mapa (o Plotly baixa o contorno do mapa).

Se quiser refazer as bases tratadas a partir dos arquivos brutos (rodar da pasta do projeto):

```bash
python etl/tratar_crescimento.py
python etl/tratar_outliers.py
python etl/tratar_piramide.py
python etl/tratar_serie.py
python imagens/gerar_infograficos.py
```

**Divisão da equipe:** o trabalho que estava atribuído ao antigo Integrante 4 foi redistribuído entre os três integrantes: evolução/projeção/mapa ficou com o MATHEUS FERREIRA BELTHODO, e infográficos/notícias com o ANA JULIA GOIS DO NASCIMENTO.

## Estrutura

```
app.py                  menu lateral, filtros e upload (integração do grupo)
layout.py               cores, tema dos gráficos e cabeçalho das telas
.streamlit/config.toml  tema do Streamlit
estatisticas.py         média, mediana, moda, quartis, IQR, amplitude, desvio padrão, outliers
secoes/                 uma tela por integrante
etl/                    scripts de tratamento dos dados
dados/brutos/           arquivos do IBGE como vieram
dados/tratados/         bases limpas que o app usa
imagens/                logo e infográficos da seção de notícias
imagens/fotos/          fotos de expansão urbana (aparecem sozinhas na tela 4)
RELATORIO.md            síntese do grupo
```

## Dados (IBGE / SIDRA)

- **Tabela 4709**: população residente dos municípios, Censo 2022
- **Censo 2010 x 2022 por município**: população dos 5.565 municípios que já existiam em 2010
- **Tabela 9514**: população por sexo e idade, Censo 2022, por UF
- **Tabela 1286**: população nos Censos de 1980, 1991, 2000 e 2010, por UF
- Contorno dos estados: `brasil_uf.geojson`

Tratamentos feitos: separação do nome do município e da UF, remoção dos 5 municípios criados depois de 2010 (Mojuí dos Campos/PA, Pescaria Brava/SC, Balneário Rincão/SC, Pinto Bandeira/RS e Paraíso das Águas/MS), conferência dos totais (Brasil 2010 = 190.755.799 e 2022 = 203.080.756), limpeza do cabeçalho e do rodapé da tabela do SIDRA, troca de "-" por zero e conversão da idade em texto para número.

## Fórmulas usadas

- Crescimento acumulado (%) = (Pop 2022 / Pop 2010 - 1) × 100
- Taxa geométrica anual (%) = ((Pop 2022 / Pop 2010)^(1/12) - 1) × 100
- IQR = Q3 - Q1; outlier se valor < Q1 - 1,5 × IQR ou valor > Q3 + 1,5 × IQR
- Índice de envelhecimento = (pessoas com 65 anos ou mais / pessoas de 0 a 14 anos) × 100
- Projeção: P(t) = P2022 × (1 + r)^(t - 2022), com r = taxa anual 2010-2022

## Execução no Windows

Também é possível iniciar o painel com dois cliques em `executar.bat`. O arquivo abre o terminal na pasta correta, instala as dependências e inicia o Streamlit. Para executar manualmente, abra o terminal nesta pasta e rode:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

O aplicativo agora define automaticamente a pasta do próprio projeto como diretório de trabalho, evitando erros de caminho quando iniciado pelo VS Code ou por um terminal aberto em outra pasta.
