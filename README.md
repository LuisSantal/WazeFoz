# 🚦 WazeFoz — Análise da Mobilidade Urbana em Foz do Iguaçu

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge.svg)](https://wazefoz.streamlit.app/)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/downloads/)

> Plataforma de pesquisa para explorar, visualizar e comparar registros colaborativos de mobilidade urbana em Foz do Iguaçu, Paraná.

**Aplicação web:** [wazefoz.streamlit.app](https://wazefoz.streamlit.app/)

O WazeFoz organiza registros de alertas viários e congestionamentos associados ao programa Waze for Cities. O dashboard permite examinar ocorrências por período, categoria e via, identificar concentrações espaciais e comparar padrões históricos. A análise de **buracos na via** é o recorte detalhado da pesquisa apresentada no EICTI 2026.

Os mapas e indicadores oferecem **apoio exploratório à decisão**: ajudam a localizar questões que merecem investigação, mas não substituem inspeções de campo, dados institucionais ou avaliações de engenharia.

## Pesquisa e equipe

O projeto está vinculado ao plano de trabalho **PID 4021-2025**, *“Exploração de Dados Disponíveis na Plataforma Waze Partner Hub para Análise de Mobilidade Urbana”*, desenvolvido na Universidade Federal da Integração Latino-Americana (UNILA), com bolsa de iniciação científica financiada pelo CNPq.

| Participação | Pessoa |
|---|---|
| Bolsista | Luis Enrique Santacruz Alvarez |
| Colaborador | Joylan Nunes Maciel |
| Coorientador | Ricardo Morel Hartmann |
| Orientador | Diego Moraes Flores |

## Objetivos

- Organizar registros de incidentes viários e congestionamentos em formatos adequados à análise.
- Investigar padrões de ocorrência no tempo e no espaço.
- Identificar períodos de maior frequência e vias com mais registros.
- Apresentar resultados em gráficos, tabelas e mapas interativos.
- Apoiar a definição de prioridades **para inspeção e estudos posteriores**.

## Funcionalidades

A disponibilidade de algumas visualizações depende dos arquivos carregados e da configuração do Google Drive.

### Mapas e exploração temporal

- Visualização de alertas pontuais, incluindo acidentes, perigos, obras e buracos.
- Visualização das geometrias de congestionamento quando a base contém a coluna `line`.
- Filtros por data, horário, categoria e via.
- Mapa de concentração de ocorrências.
- Exploração em 2D e visualizações 3D de densidade ou quantidade de registros.

No mapa 3D, a altura das colunas representa **volume de registros**, não edifícios reais. Arcos visuais não representam trajetos ou fluxos efetivamente observados.

### Análise anual de buracos

- Comparação mensal dos registros de 2024, 2025 e 2026.
- Ranking das vias com mais registros em cada ano.
- Tabelas e mapas para inspeção dos resultados.
- Conferência entre valores calculados a partir dos arquivos disponíveis e os valores apresentados no resumo da pesquisa.

**Atenção:** os resultados de 2026 apresentados no resumo abrangem **janeiro a agosto**. Esse período parcial não deve ser tratado como um ano completo em comparações diretas.

### Criticidade viária

O aplicativo contém uma análise exploratória que combina o volume de registros de congestionamento e o atraso médio por via. No código examinado, os pesos utilizados são 40% para volume e 60% para atraso:

\[
I_{\text{crit}} =
100 \left(
0{,}4 \frac{V_{\text{via}}}{V_{\text{máx}}}
+
0{,}6 \frac{A_{\text{via}}}{A_{\text{máx}}}
\right)
\]

O índice ordena as vias **dentro da base analisada**. Não equivale a uma medição absoluta de risco, nem determina automaticamente a necessidade de uma obra.

### Resultados visuais

Quando houver figuras publicadas em `assets/resultados/`, a aba de resultados visuais pode mostrá-las separadamente dos mapas interativos. Cada figura deve ser acompanhada de fonte, período e legenda adequados.

## Resultados descritos no resumo acadêmico

| Período | Registros de buracos | Mês de maior frequência | Via com mais registros |
|---|---:|---|---|
| 2024 | 7.296 | Maio: 1.460 | Avenida Paraná: 581 |
| 2025 | 17.608 | Agosto: 3.166 | Avenida das Cataratas: 1.206 |
| Janeiro–agosto de 2026 | 6.168 | Março: 1.175 | Avenida Felipe Wandscheer: 936 |

Esses valores são **resultados apresentados no resumo**, não números impostos ao dashboard. Divergências entre eles e a aplicação exigem verificar a versão dos arquivos, a cobertura temporal, a interpretação das datas, os nomes das vias e os critérios de desduplicação.

## Dados e processamento

O projeto utiliza arquivos históricos CSV de alertas e, quando configurado, arquivos HDF5 acessados pelo Google Drive. O processamento inclui normalização de datas e categorias, extração de coordenadas, filtragem, agregação por período e via e criação de visualizações.

A caixa de coordenadas utilizada em partes da aplicação é um **recorte geográfico aproximado** da área estudada, não o limite administrativo oficial do município.

## Limitações

- Os dados são colaborativos e podem conter registros incompletos ou imprecisos.
- Um registro não corresponde necessariamente a um problema físico distinto.
- Pode haver duplicidades, subnotificação e diferentes níveis de cobertura ao longo do tempo.
- Nem todos os eventos possuem coordenadas ou geometrias de linha válidas.
- A frequência de registros não mede, isoladamente, severidade ou custo de intervenção.
- Rankings, mapas de concentração e índices relativos exigem validação com outras fontes e inspeções de campo.

## Executar localmente

Recomenda-se Python 3.11 para reproduzir o ambiente de desenvolvimento.

```bash
git clone [https://github.com/LuisSantal/WazeFoz.git](https://github.com/LuisSantal/WazeFoz.git)
cd WazeFoz

python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

No Windows, ative o ambiente virtual com:

```powershell
.venv\Scripts\Activate.ps1
```

Os CSVs devem estar nos caminhos esperados pelo aplicativo. Para habilitar a leitura dos HDF5 no Google Drive, configure a conta de serviço nos **secrets do Streamlit** sob a chave `gcp_service_account`. Nunca publique chaves privadas, tokens ou arquivos de credenciais no repositório.

O `requirements.txt` define predominantemente **versões mínimas** (`>=`), não um conjunto integralmente travado de versões.

## Próximas etapas

- Documentar e testar regras de limpeza e desduplicação.
- Validar indicadores com inspeções de campo e bases institucionais.
- Avaliar diferenças de cobertura entre períodos e fontes.
- Aperfeiçoar a apresentação de mapas e séries temporais.
- Desenvolver modelos adicionais **somente após calibração e validação**, antes de apresentá-los como previsões operacionais.

## Créditos

Desenvolvido por **Luis Enrique Santacruz Alvarez** no contexto da pesquisa de iniciação científica na UNILA, com colaboração e orientação da equipe identificada acima. Dados de mobilidade associados ao programa **Waze for Cities**.
