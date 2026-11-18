# ============================================================
# DASHBOARD INTERATIVO DE E-COMMERCE
# Bibliotecas: Pandas, Plotly e Dash
#
# Como executar:
#   1) Deixe este arquivo e ecommerce_estatistica.csv na mesma pasta.
#   2) Instale: pip install pandas plotly dash
#   3) Execute: python app.py
#   4) Abra: http://127.0.0.1:8050/
# ============================================================

from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output


# 1. LEITURA DO ARQUIVO CSV
PASTA_PROJETO = Path(__file__).resolve().parent
CAMINHO_CSV = PASTA_PROJETO / "ecommerce_estatistica.csv"

if not CAMINHO_CSV.exists():
    raise FileNotFoundError(
        "O arquivo 'ecommerce_estatistica.csv' não foi encontrado. "
        "Coloque o CSV na mesma pasta do app.py."
    )

df = pd.read_csv(CAMINHO_CSV)

# Remove a coluna de índice que pode vir gravada no CSV.
if "Unnamed: 0" in df.columns:
    df = df.drop(columns=["Unnamed: 0"])

# Colunas numéricas existentes no arquivo e usadas nas análises.
variaveis_numericas = [
    coluna for coluna in [
        "Nota",
        "N_Avaliações",
        "Desconto",
        "Preço",
        "Nota_MinMax",
        "N_Avaliações_MinMax",
        "Desconto_MinMax",
        "Preço_MinMax",
        "Marca_Cod",
        "Material_Cod",
        "Temporada_Cod",
        "Qtd_Vendidos_Cod",
        "Marca_Freq",
        "Material_Freq",
    ]
    if coluna in df.columns
]

nomes_variaveis = {
    "Nota": "Nota do produto",
    "N_Avaliações": "Número de avaliações",
    "Desconto": "Desconto (%)",
    "Preço": "Preço (R$)",
    "Nota_MinMax": "Nota normalizada",
    "N_Avaliações_MinMax": "Avaliações normalizadas",
    "Desconto_MinMax": "Desconto normalizado",
    "Preço_MinMax": "Preço normalizado",
    "Marca_Cod": "Marca (código)",
    "Material_Cod": "Material (código)",
    "Temporada_Cod": "Temporada (código)",
    "Qtd_Vendidos_Cod": "Quantidade vendida (código)",
    "Marca_Freq": "Frequência da marca",
    "Material_Freq": "Frequência do material",
}

# Garante que as variáveis usadas nos gráficos sejam numéricas.
for coluna in variaveis_numericas:
    df[coluna] = pd.to_numeric(df[coluna], errors="coerce")

if not variaveis_numericas:
    raise ValueError("O CSV não contém as colunas numéricas esperadas para os gráficos.")


# 2. FUNÇÕES AUXILIARES
def opcoes_coluna(nome_coluna):
    """Cria opções para filtros categóricos."""
    if nome_coluna not in df.columns:
        return [{"label": "Todos", "value": "Todos"}]

    valores = sorted(df[nome_coluna].dropna().astype(str).unique())
    return [{"label": "Todos", "value": "Todos"}] + [
        {"label": valor, "value": valor} for valor in valores
    ]


def filtrar_dados(genero, marca):
    """Aplica os filtros escolhidos pelo usuário."""
    dados = df.copy()

    if genero != "Todos" and "Gênero" in dados.columns:
        dados = dados[dados["Gênero"].astype(str) == genero]

    if marca != "Todos" and "Marca" in dados.columns:
        dados = dados[dados["Marca"].astype(str) == marca]

    return dados


def formatar_media(dados, coluna, prefixo="", sufixo=""):
    """Retorna uma média formatada ou informa que não há dados."""
    if coluna not in dados.columns or dados[coluna].dropna().empty:
        return "Não disponível"
    return f"{prefixo}{dados[coluna].mean():,.2f}{sufixo}".replace(",", "X").replace(".", ",").replace("X", ".")


# 3. CONFIGURAÇÃO DO DASH
app = Dash(__name__)
app.title = "Dashboard de E-commerce"

estilo_card = {
    "backgroundColor": "white",
    "padding": "18px",
    "borderRadius": "10px",
    "boxShadow": "0 1px 5px rgba(0,0,0,0.08)",
    "marginBottom": "16px",
}

estilo_titulo = {
    "color": "#243447",
    "marginBottom": "6px",
}

opcoes_variaveis = [
    {"label": nomes_variaveis.get(v, v), "value": v}
    for v in variaveis_numericas
]

variavel_x_inicial = "Preço" if "Preço" in variaveis_numericas else variaveis_numericas[0]
variavel_y_inicial = "Nota" if "Nota" in variaveis_numericas else variaveis_numericas[-1]

app.layout = html.Div(
    style={
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": "#f3f5f8",
        "minHeight": "100vh",
        "padding": "24px",
        "color": "#263238",
    },
    children=[
        html.Div(
            style={"maxWidth": "1250px", "margin": "0 auto"},
            children=[
                html.H1(
                    "Dashboard de Análise de E-commerce",
                    style={"textAlign": "center", **estilo_titulo},
                ),
                html.P(
                    "Explore os produtos, compare indicadores e visualize "
                    "as relações estatísticas de forma interativa.",
                    style={"textAlign": "center", "color": "#596579"},
                ),

                html.Div(
                    style=estilo_card,
                    children=[
                        html.H2("1. Filtros", style=estilo_titulo),
                        html.Label("Gênero dos produtos"),
                        dcc.Dropdown(
                            id="filtro-genero",
                            options=opcoes_coluna("Gênero"),
                            value="Todos",
                            clearable=False,
                        ),
                        html.Br(),
                        html.Label("Marca"),
                        dcc.Dropdown(
                            id="filtro-marca",
                            options=opcoes_coluna("Marca"),
                            value="Todos",
                            clearable=False,
                        ),
                    ],
                ),

                html.Div(
                    style=estilo_card,
                    children=[
                        html.H2("2. Resumo dos dados filtrados", style=estilo_titulo),
                        html.Div(
                            id="indicadores",
                            style={
                                "display": "grid",
                                "gridTemplateColumns": "repeat(auto-fit, minmax(180px, 1fr))",
                                "gap": "12px",
                            },
                        ),
                    ],
                ),

                html.Div(
                    style=estilo_card,
                    children=[
                        html.H2("3. Comparação entre variáveis", style=estilo_titulo),
                        html.P(
                            "Escolha as variáveis dos eixos X e Y. Passe o mouse "
                            "sobre os pontos para consultar os detalhes."
                        ),
                        html.Label("Variável do eixo X"),
                        dcc.Dropdown(
                            id="variavel-x",
                            options=opcoes_variaveis,
                            value=variavel_x_inicial,
                            clearable=False,
                        ),
                        html.Br(),
                        html.Label("Variável do eixo Y"),
                        dcc.Dropdown(
                            id="variavel-y",
                            options=opcoes_variaveis,
                            value=variavel_y_inicial,
                            clearable=False,
                        ),
                        dcc.Graph(id="grafico-dispersao"),
                    ],
                ),

                html.Div(
                    style=estilo_card,
                    children=[
                        html.H2("4. Materiais mais frequentes", style=estilo_titulo),
                        dcc.Graph(id="grafico-materiais"),
                    ],
                ),

                html.Div(
                    style=estilo_card,
                    children=[
                        html.H2("5. Correlação estatística", style=estilo_titulo),
                        html.P(
                            "Pearson avalia relações lineares. Spearman avalia "
                            "relações monotônicas com base nas posições dos valores."
                        ),
                        dcc.RadioItems(
                            id="metodo-correlacao",
                            options=[
                                {"label": " Pearson", "value": "pearson"},
                                {"label": " Spearman", "value": "spearman"},
                            ],
                            value="pearson",
                            inline=True,
                        ),
                        dcc.Graph(id="grafico-correlacao"),
                    ],
                ),

                html.Div(
                    style=estilo_card,
                    children=[
                        html.H2("6. Informações estatísticas", style=estilo_titulo),
                        dcc.Checklist(
                            id="mostrar-informacoes",
                            options=[
                                {
                                    "label": " Exibir informações estatísticas",
                                    "value": "mostrar",
                                }
                            ],
                            value=["mostrar"],
                        ),
                        html.Div(id="informacoes-estatisticas"),
                    ],
                ),

                html.P(
                    "Desenvolvido com Pandas, Plotly e Dash.",
                    style={"textAlign": "center", "color": "#748094", "padding": "12px"},
                ),
            ],
        )
    ],
)


# 4. CALLBACK: INDICADORES RESUMIDOS
@app.callback(
    Output("indicadores", "children"),
    Input("filtro-genero", "value"),
    Input("filtro-marca", "value"),
)
def atualizar_indicadores(genero, marca):
    dados = filtrar_dados(genero, marca)

    indicadores = [
        ("Produtos encontrados", f"{len(dados)}"),
        ("Nota média", formatar_media(dados, "Nota")),
        ("Preço médio", formatar_media(dados, "Preço", "R$ ")),
        ("Desconto médio", formatar_media(dados, "Desconto", sufixo="%")),
    ]

    return [
        html.Div(
            [
                html.P(rotulo, style={"margin": "0", "color": "#667085"}),
                html.H3(valor, style={"margin": "8px 0 0", "color": "#243447"}),
            ],
            style={
                "backgroundColor": "#f3f6fa",
                "padding": "14px",
                "borderRadius": "8px",
            },
        )
        for rotulo, valor in indicadores
    ]


# 5. CALLBACK: GRÁFICO DE DISPERSÃO
@app.callback(
    Output("grafico-dispersao", "figure"),
    Input("filtro-genero", "value"),
    Input("filtro-marca", "value"),
    Input("variavel-x", "value"),
    Input("variavel-y", "value"),
)
def atualizar_dispersao(genero, marca, x, y):
    dados = filtrar_dados(genero, marca)
    colunas = [x, y]
    dados = dados.dropna(subset=colunas)

    hover_name = "Título" if "Título" in dados.columns else None
    color = "Gênero" if "Gênero" in dados.columns else None

    fig = px.scatter(
        dados,
        x=x,
        y=y,
        color=color,
        hover_name=hover_name,
        title=f"{nomes_variaveis.get(x, x)} x {nomes_variaveis.get(y, y)}",
        labels=nomes_variaveis,
        template="plotly_white",
    )
    fig.update_layout(margin={"l": 30, "r": 20, "t": 60, "b": 35})
    return fig


# 6. CALLBACK: GRÁFICO DE MATERIAIS
@app.callback(
    Output("grafico-materiais", "figure"),
    Input("filtro-genero", "value"),
    Input("filtro-marca", "value"),
)
def atualizar_materiais(genero, marca):
    dados = filtrar_dados(genero, marca)

    if "Material" not in dados.columns or dados["Material"].dropna().empty:
        fig = px.bar(title="Coluna Material não disponível")
        return fig

    materiais = (
        dados["Material"]
        .fillna("Não informado")
        .value_counts()
        .head(10)
        .rename_axis("Material")
        .reset_index(name="Quantidade")
    )

    fig = px.bar(
        materiais,
        x="Material",
        y="Quantidade",
        text="Quantidade",
        title="Até 10 materiais mais frequentes",
        template="plotly_white",
    )
    fig.update_layout(margin={"l": 30, "r": 20, "t": 60, "b": 35})
    return fig


# 7. CALLBACK: MATRIZ DE CORRELAÇÃO
@app.callback(
    Output("grafico-correlacao", "figure"),
    Input("filtro-genero", "value"),
    Input("filtro-marca", "value"),
    Input("metodo-correlacao", "value"),
)
def atualizar_correlacao(genero, marca, metodo):
    dados = filtrar_dados(genero, marca)
    matriz = dados[variaveis_numericas].corr(method=metodo)

    fig = px.imshow(
        matriz,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        aspect="auto",
        title=f"Matriz de correlação - {metodo.capitalize()}",
        labels={"x": "Variáveis", "y": "Variáveis", "color": "Correlação"},
    )
    fig.update_layout(margin={"l": 30, "r": 20, "t": 60, "b": 35})
    return fig


# 8. CALLBACK: CHECKLIST E INFORMAÇÕES ESTATÍSTICAS
@app.callback(
    Output("informacoes-estatisticas", "children"),
    Input("filtro-genero", "value"),
    Input("filtro-marca", "value"),
    Input("mostrar-informacoes", "value"),
)
def atualizar_informacoes(genero, marca, mostrar):
    if "mostrar" not in (mostrar or []):
        return html.P("As informações estatísticas estão ocultas.")

    dados = filtrar_dados(genero, marca)

    if dados.empty:
        return html.P("Não há produtos para os filtros selecionados.")

    textos = [
        f"Quantidade de produtos: {len(dados)}",
        f"Nota média: {formatar_media(dados, 'Nota')}",
        f"Preço médio: {formatar_media(dados, 'Preço', 'R$ ')}",
        f"Desconto médio: {formatar_media(dados, 'Desconto', sufixo='%')}",
    ]

    return html.Ul([html.Li(texto) for texto in textos])


# 9. EXECUÇÃO DA APLICAÇÃO
if __name__ == "__main__":
    app.run(debug=True)
