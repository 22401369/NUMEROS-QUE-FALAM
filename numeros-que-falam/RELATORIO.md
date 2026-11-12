# Relatório do grupo: Radar Urbano

**Indicador:** População e Crescimento Demográfico
**Clientes:** Carlos (Curitiba), Eduardo (Porto Alegre), Elisa (Belo Horizonte), Jorge (Salvador) e Roberto (Florianópolis)
**Fonte:** IBGE, Censos Demográficos 1980 a 2022 (SIDRA)

## Divisão da equipe (3 integrantes)

- **ALEXANDRE LUIZ SILVA FREITAS:** crescimento dos municípios e estatísticas.
- **MATHEUS FERREIRA BELTHODO:** outliers, evolução histórica, projeção e mapa (inclui a antiga parte do Integrante 4).
- **ANA JULIA GOIS DO NASCIMENTO:** pirâmide etária, envelhecimento e infográficos/notícias (inclui a parte visual da antiga parte do Integrante 4).

## O problema

Os prefeitos estão revisando os Planos Diretores e o orçamento de saúde e infraestrutura. Eles precisam saber a que velocidade a população está crescendo, onde estão as cidades fora do padrão e o quanto a população está envelhecendo.

## 1. Taxa média de crescimento acumulada por cidade

Analisamos os 2.458 municípios dos cinco estados dos clientes (BA, MG, PR, RS e SC) entre 2010 e 2022.

| Medida | Valor |
|---|---|
| Média | 2,55% |
| Mediana | 0,77% |
| Moda (classe modal) | -5% a 0% (471 municípios) |
| Q1 / Q3 | -5,91% / 7,99% |
| IQR | 13,90 p.p. |
| Amplitude | 153,96 p.p. (de -45,67% a 108,29%) |
| Desvio padrão | 13,88 p.p. |

A média (2,55%) é maior que a mediana (0,77%), ou seja, a distribuição tem assimetria à direita: poucas cidades que cresceram muito puxam a média para cima. A classe mais comum é a de quem **perdeu** até 5% da população. Quase metade das cidades (47%) encolheu.

Por estado, a mediana do crescimento foi: SC 6,84%, PR 1,69%, MG 0,98%, BA -0,85% e RS -2,65%. Santa Catarina é o único estado em que a maioria das cidades cresceu com folga; no Rio Grande do Sul, 58,5% dos municípios perderam moradores.

Nas capitais: Florianópolis cresceu 27,5%, Curitiba 1,2%, Belo Horizonte caiu 2,5%, Porto Alegre caiu 5,4% e Salvador caiu 9,6% (perdeu 257.978 moradores). A população está saindo das capitais para as cidades vizinhas e para o litoral.

## 2. Outliers de crescimento

Pela regra de 1,5 × IQR, qualquer município fora da faixa de -26,75% a 28,83% é outlier. Encontramos **94 cidades que cresceram exageradamente** (Itapoá/SC +108%, Barra Velha/SC +103%, Passo de Torres/SC +95%, Extrema/MG +87%) e **11 que encolheram demais** (Caatiba/BA -45,7%, Ubatã/BA -35,6%). 91% dos outliers que encolheram são cidades pequenas, de até 20 mil habitantes.

Sem os outliers a média cai de 2,55% para 0,96%, uma mudança de 1,59 p.p., enquanto a mediana muda só 0,54 p.p. Isso mostra que a média é sensível a valores extremos e que a mediana é a melhor referência de crescimento típico.

## 3. Envelhecimento

No Censo 2022 o Brasil tem 55,2 idosos (65+) para cada 100 jovens de 0 a 14 anos, e 10,9% da população tem 65 anos ou mais. O Rio Grande do Sul é o estado mais envelhecido do país (80,4), seguido de Minas Gerais (68,6). Paraná (59,2), Santa Catarina (55,8) e Bahia (52,6) vêm logo depois. A idade mediana dos cinco estados é de 36 anos e a pirâmide já tem a base mais estreita que o meio.

## 4. Evolução e projeção

O Brasil crescia 1,77% ao ano entre 1980 e 1991 e passou para 0,52% ao ano entre 2010 e 2022, o menor ritmo da história. Em quatro dos cinco estados, 2010-2022 foi o período de menor crescimento; a exceção é Santa Catarina (1,66% ao ano). Nossa projeção geométrica simples é só uma extrapolação; o IBGE projeta que a população do país vai parar de crescer por volta de 2041.

## Recomendações para os prefeitos

- **Salvador, Porto Alegre e Belo Horizonte:** a população diminui e envelhece. Priorizar saúde do idoso, acessibilidade e transporte adaptado, e planejar em conjunto com as cidades da região metropolitana, que estão recebendo os moradores.
- **Florianópolis:** crescimento forte e concentrado no litoral catarinense (vários outliers). Priorizar saneamento, mobilidade e moradia, antes que a infraestrutura fique para trás.
- **Curitiba:** crescimento quase parado, mas o Paraná continua crescendo. Atenção à expansão das cidades vizinhas.
- **Para todos:** usar a mediana, e não a média, como referência de crescimento típico, e tratar as cidades outliers como casos especiais no planejamento.
