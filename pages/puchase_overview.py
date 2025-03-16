import dash
from dash import callback, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from utils.functions import create_card
import pandas as pd
import plotly.express as px

dash.register_page(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    path="/puchase_overview",
)

import warnings

warnings.filterwarnings("ignore")

# dataset
df = pd.read_parquet(
    "data/ready/purchases.parquet",
    columns=[
    "Customer ID",
    "Item Purchased",
    "Category",
    "Purchase Amount (USD)",
    "Season",
    "Review Rating",
    "Payment Method",
    ],
)

# df = pd.read_parquet("data/ready/amazon_purchases.parquet")

layout = dbc.Container(
    [
        # Título del dashboard
        html.Div(
            children=[
                html.H1("Customer Purchase Analysis Dashboard", className="text-center", style={"margin-top": "20px"}),
                html.Hr(),
            ]
        ),

        # Filtros (se colocan en una fila con 3 columnas)
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id='category-filter',
                        options=[{'label': 'All Categories', 'value': 'All'}] + [{'label': cat, 'value': cat} for cat in df['Category'].unique()],
                        value='All',
                        placeholder="Select Category",
                    ),
                    width=4,
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id='season-filter',
                        options=[{'label': 'All Seasons', 'value': 'All'}] + [{'label': season, 'value': season} for season in df['Season'].unique()],
                        value='All',
                        placeholder="Select Season",
                    ),
                    width=4,
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id='payment-method-filter',
                        options=[{'label': 'All Payment Methods', 'value': 'All'}] + [{'label': method, 'value': method} for method in df['Payment Method'].unique()],
                        value='All',
                        placeholder="Select Payment Method",
                    ),
                    width=4,
                ),
            ],
            style={"margin-top": "20px"},
        ),

    html.Br(),
                dbc.Row(
                    [
                        dbc.Col(
                            create_card("Purchases", "purchases-card", "fa-list"),
                            width=4,
                        ),
                        dbc.Col(
                            create_card("Total Spend", "spend-card", "fa-coins"),
                            width=4,
                        ),
                        dbc.Col(
                            create_card("Top Category", "category-card", "fa-tags"),
                            width=4,
                        ),
                    ],
                ),
                html.Br(),
        # Gráficos (se ajustan en una cuadrícula de 2 columnas)
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='sales-chart'), width=6),
                dbc.Col(dcc.Graph(id='category-chart'), width=6),
            ],
            style={'margin-top': '20px'},
        ),
        
        # Gráfico adicional (rating-chart en otra fila si es necesario)
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='rating-chart'), width=12),  # Se ocupa toda la fila
            ],
            style={'margin-top': '20px'},
        )
    ],
    fluid=True,
)


# callback cards and graphs

@callback(
    [Output('purchases-card', 'children'),
     Output('spend-card', 'children'),
     Output('category-card', 'children'),
     Output('sales-chart', 'figure'),
     Output('category-chart', 'figure'),
     Output('rating-chart', 'figure')],
    [Input('category-filter', 'value'),
     Input('season-filter', 'value'),
     Input('payment-method-filter', 'value')]
)
def update_values(select_category=None, select_season=None, select_payment_method=None):
    filtered_df = df.copy()

    # Filtros
    if select_category and select_category != "All":
        filtered_df = filtered_df[filtered_df["Category"] == select_category]

    if select_season and select_season != "All":
        filtered_df = filtered_df[filtered_df["Season"] == select_season]

    if select_payment_method and select_payment_method != "All":
        filtered_df = filtered_df[filtered_df["Payment Method"] == select_payment_method]

    # Tarjetas
    purchases_card = f"{filtered_df['Customer ID'].nunique():,.0f}"  # Contar usuarios únicos
    spend_card = f"$ {round(filtered_df['Purchase Amount (USD)'].sum(), -2):,.0f}"  # Gasto total
    category_card = filtered_df.groupby("Category")["Item Purchased"].count().idxmax()  # Categoría más comprada

    # Gráfico de ventas (Total de compras por temporada)
    sales_chart = px.bar(
        filtered_df.groupby("Season", observed=True)["Purchase Amount (USD)"]
        .sum()
        .reset_index(),
        x="Season",
        y="Purchase Amount (USD)",
        text_auto=".2s",
        title="Total Spend by Season",
    )

    sales_chart.update_traces(
        textposition="outside",
        marker_color="#f79500",
        hoverlabel=dict(bgcolor="rgba(255, 255, 255, 0.1)", font_size=12),
        hovertemplate="<b>%{x}</b><br>Value: %{y:,}<extra></extra>",
    )

    sales_chart.update_layout(
        xaxis_title="Season",
        yaxis_title="Total Spend (USD)",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        margin=dict(l=35, r=35, t=60, b=40),
    )

    # Gráfico de categorías más compradas
    category_chart = px.treemap(
        filtered_df.groupby("Category", as_index=False, observed=True)["Item Purchased"]
        .count()
        .nlargest(5, columns="Item Purchased"),
        path=["Category"],
        values="Item Purchased",
        title="Top 5 Purchase Categories",
        color="Category",
        color_discrete_sequence=["#cb7721", "#b05611", "#ffb803", "#F79500", "#803f0c"],
    )

    category_chart.data[0].textinfo = "label+value"

    category_chart.update_traces(textfont=dict(size=13))

    category_chart.update_layout(margin=dict(l=35, r=35, t=60, b=35), hovermode=False)
    top_rated_products = (
    filtered_df.groupby(['Item Purchased', 'Review Rating'], as_index=False)
    .agg({'Purchase Amount (USD)': 'sum'})  
    .sort_values(by='Review Rating', ascending=False)
    .head(5)  
)


    top_rated_products_with_ties = (
        filtered_df[filtered_df['Review Rating'].isin(top_rated_products['Review Rating'])]
        .groupby(['Item Purchased', 'Review Rating'], as_index=False)
        .agg({'Purchase Amount (USD)': 'sum'})
        .sort_values(by='Review Rating', ascending=False)
    )

    # Crear el gráfico de barras
    rating_chart = px.bar(
        top_rated_products_with_ties,
        x="Item Purchased",  # Nombre del producto
        y="Purchase Amount (USD)",  # Cantidad comprada
        color="Review Rating",  # Colorear por calificación
        title="Top 5 Products with Best Ratings (Including Ties)", 
        color_continuous_scale="Viridis", 
        labels={"Item Purchased": "Product", "Purchase Amount (USD)": "Total Purchase Amount (USD)", "Review Rating": "Rating"},
    )

    rating_chart.update_traces(
        textposition="outside",
        marker_color="#f79500",
        hoverlabel=dict(bgcolor="rgba(255, 255, 255, 0.1)", font_size=12),
        hovertemplate="<b>%{x}</b><br>Value: %{y:,}<extra></extra>",
    )

    rating_chart.update_layout(
        xaxis_title="Product",
        yaxis_title="Total Purchase Amount (USD)",
      
        xaxis_tickangle=-45,  
        margin=dict(l=40, r=40, t=60, b=40),  
     
        showlegend=True  
    )


    return purchases_card, spend_card, category_card, sales_chart, category_chart, rating_chart
