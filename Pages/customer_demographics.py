import dash
from dash import callback, dcc, html, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

dash.register_page(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    path="/customer_demographics",
)

# dataset
df = pd.read_parquet("data/ready/customer_demographics.parquet")
user_count = df["Customer ID"].nunique()
# layout
layout = dbc.Container(
    [
        html.Div(
            [
                html.H2(
                    "Customer demographics",  # title
                    className="title",
                ),
                html.H3(f"{user_count:,} Users", className="subtitle-small"),  # subtitle
               
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Loading(
                                dcc.Graph(
                                    id="gender-chart",
                                    config={"displayModeBar": False},
                                    className="chart-card",
                                    style={"height": "280px"},
                                ),
                                type="circle",
                                color="#f79500",
                            ),
                            width=4,
                        ),
                        dbc.Col(
                            dcc.Loading(
                                dcc.Graph(
                                    id="age-chart",
                                    config={"displayModeBar": False},
                                    className="chart-card",
                                    style={"height": "280px"},
                                ),
                                type="circle",
                                color="#f79500",
                            ),
                            width=4,
                        ),
                         dbc.Col(
                            dcc.Loading(
                                dcc.Graph(
                                    id="subscription-chart",
                                    config={"displayModeBar": False},
                                    className="chart-card",
                                    style={"height": "280px"},
                                ),
                                type="circle",
                                color="#f79500",
                            ),
                            width=4,
                        ),
                        
                    ],
                ),
                html.Br(),
                dbc.Row(
                    [
                        dbc.Col(
                            
                            dcc.Loading(
                                dcc.Graph(
                                    id="state-chart",
                                    config={"displayModeBar": False},
                                    className="chart-card",
                                    style={"height": "337px"},
                                ),
                                type="circle",
                                color="#f79500",
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            
                            dcc.Loading(
                                dcc.Graph(
                                    id="age_histogram-chart",
                                    config={"displayModeBar": False},
                                    className="chart-card",
                                    style={"height": "337px"},
                                ),
                                type="circle",
                                color="#f79500",
                            ),
                            width=6,
                        ),
                    ],
                ),
            ],
            className="page-content",
        )
    ],
    fluid=True,
)


# callback cards and graphs
@callback(
    [
       
        Output("gender-chart", "figure"),
        Output("age-chart", "figure"),
        Output("subscription-chart", "figure"),
        Output("state-chart", "figure"),
        Output("age_histogram-chart", "figure"),
     
        Input("gender-chart", "id"),
        Input("age-chart", "id"),
        Input("subscription-chart", "id"),
        Input("age_histogram-chart", "id"),
        Input("state-chart", "id"),
        
     
    ],
)

def update_chart(gender, age,subscription,age_histogram, state):

    # gender
    gender_chart = px.pie(
        df,
        names="Gender",
        hole=0.4,
        title="Gender Distribution",
        color="Gender",
        color_discrete_map={"Male": "#b05611", "Female": "#f79500"}
    )

    gender_chart.update_traces(
    textposition="outside",
    textinfo="percent+label",
    rotation=180,
    showlegend=True,
    texttemplate="%{label}<br>%{percent:.1%}",
    hoverlabel=dict(bgcolor="rgba(255, 255, 255, 0.1)", font_size=12),
    hovertemplate="<b>%{label}</b><br>Value: %{value:,}<br>"
    )

    gender_chart.update_layout(
        yaxis=dict(showticklabels=False), margin=dict(l=15, r=15, t=60, b=15)
    )
    # Crear rangos de edad
    bins = [18, 24, 34, 44, 54, 64, 100]  # Definir los intervalos
    labels = ["18 - 24", "25 - 34", "35 - 44", "45 - 54", "55 - 64", "65+"]  # Etiquetas
    df["Age Group"] = pd.cut(df["Age"], bins=bins, labels=labels, right=True)

    # Contar la cantidad de usuarios en cada rango de edad
    age_counts = df["Age Group"].value_counts().reset_index()
    age_counts.columns = ["Age", "Count"]

    # Ordenar los grupos de edad en el orden correcto
    age_counts["Age"] = pd.Categorical(age_counts["Age"], categories=labels, ordered=True)
    age_counts = age_counts.sort_values(by="Age")

    # Crear gráfico de barras
    age_chart = px.bar(
        age_counts,
        x="Age",
        y="Count",
        text_auto=".2s",
        title="Age Distribution",
    )

    # Mejorar visualización
    age_chart.update_traces(
        marker_color="#b05611",
        textposition="auto",
        hoverlabel=dict(bgcolor="rgba(255, 255, 255, 0.1)", font_size=12),
        hovertemplate="<b>%{x}</b><br>Count: %{y:,}<extra></extra>",
    )

    age_chart.update_layout(
        xaxis_title="Age Group",
        yaxis_title="Number of Customers",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        margin=dict(l=15, r=15, t=60, b=15),
    )


    subscription_pie = px.pie(
    df, names="Subscription Status",
    title="Subscription Status Distribution",
    color="Subscription Status",
    color_discrete_map={"Yes": "#f79500", "No": "#b05611"}
    )
    # Filtrar solo los clientes suscritos (los que compran)
    df_subscribed = df[df["Subscription Status"] == "Yes"]

    # Calcular el promedio de edad de los compradores
    mean_age = df_subscribed["Age"].mean()

    # Definir un rango alrededor del promedio (ej. ±10 años)
    age_range_min = mean_age - 10
    age_range_max = mean_age + 10

    # Filtrar datos dentro del rango
    df_filtered = df_subscribed[(df_subscribed["Age"] >= age_range_min) & (df_subscribed["Age"] <= age_range_max)]

    # Contar compras por género en ese rango de edad
    age_gender_counts = df_filtered["Gender"].value_counts().reset_index()
    age_gender_counts.columns = ["Gender", "Count"]

    # Asegurar que ambos géneros estén presentes (si falta "Female" o "Male", agregar con valor 0)
    for gender in ["Male", "Female"]:
        if gender not in age_gender_counts["Gender"].values:
            age_gender_counts = pd.concat([age_gender_counts, pd.DataFrame({"Gender": [gender], "Count": [0]})], ignore_index=True)

    # Crear gráfico de barras
    age_gender_bar = px.bar(
        age_gender_counts,
        x="Gender",
        y="Count",
        color="Gender",
        title=f"Comparison of Purchases in the Age Range {int(age_range_min)} - {int(age_range_max)}",
        color_discrete_map={"Male": "#1f77b4", "Female": "#ff7f0e"},
        text="Count"
    )

    age_gender_bar.update_traces(textposition="outside")

    age_gender_bar.update_layout(
        xaxis_title="Gender",
        yaxis_title="Number of Purchases",
        plot_bgcolor="rgba(0, 0, 0, 0)",
    )
    # state
    df_filtered = df.loc[df["Location"] != "No information"]
    state_abbreviations = {
    'Alabama': 'AL',
    'California': 'CA',
    'Texas': 'TX',
    'Florida': 'FL',
    'New York': 'NY',
    'Illinois': 'IL',
    'Pennsylvania': 'PA',
    'Ohio': 'OH',
    'Georgia': 'GA',
    'North Carolina': 'NC',
    'Michigan': 'MI',
    'New Jersey': 'NJ',
    'Virginia': 'VA',
    'Washington': 'WA',
    'Arizona': 'AZ',
    'Massachusetts': 'MA',
    'Tennessee': 'TN',
    'Indiana': 'IN',
    'Missouri': 'MO',
    'Maryland': 'MD',
    'Wisconsin': 'WI',
    'Colorado': 'CO',
    'Minnesota': 'MN',
    'South Carolina': 'SC',
    'Alabama': 'AL',
    'Louisiana': 'LA',
    'Kentucky': 'KY',
    'Oregon': 'OR',
    'Oklahoma': 'OK',
    'Connecticut': 'CT',
    'Iowa': 'IA',
    'Mississippi': 'MS',
    'Arkansas': 'AR',
    'Kansas': 'KS',
    'Nevada': 'NV',
    'Utah': 'UT',
    'Idaho': 'ID',
    'Hawaii': 'HI',
    'New Mexico': 'NM',
    'Nebraska': 'NE',
    'West Virginia': 'WV',
    'Florida': 'FL',
    'Maine': 'ME',
    'New Hampshire': 'NH',
    'Rhode Island': 'RI',
    'Montana': 'MT',
    'Delaware': 'DE',
    'South Dakota': 'SD',
    'North Dakota': 'ND',
    'Alaska': 'AK',
    'Vermont': 'VT',
    'Wyoming': 'WY',
    'District of Columbia': 'DC',
    'Puerto Rico': 'PR',
    'Guam': 'GU',
    'American Samoa': 'AS',
    'U.S. Virgin Islands': 'VI',
    'Northern Mariana Islands': 'MP',
    

    }
    df['State_Abbr'] = df['Location'].map(state_abbreviations)
    state_counts = df_filtered["Location"].value_counts().reset_index()
    state_counts.columns = ["Location", "Customer ID"]
    df_state = df_filtered.merge(state_counts, on="Location")
    custom_colorscale = [(0, "#ffb803"), (0.5, "#cb7721"), (1, "#803f0c")]
    state_chart = px.choropleth(
    df,
    locations="State_Abbr", 
    featureidkey="properties.abbreviation",  
    locationmode="USA-states",
    color="Customer ID",  
    color_continuous_scale="Viridis", 
    scope="usa",
    title="Users by State",
    hover_data=["Location"],
)
    state_chart.update_traces(
    hoverlabel=dict(bgcolor="rgba(255, 255, 255, 0.1)", font_size=12),
    hovertemplate="<b>%{customdata[0]}</b><br>Value: %{z:,}<extra></extra>",
)


    state_chart.update_layout(
        margin=dict(l=15, r=15, t=60, b=15),
    )
    state_chart.update_layout(
    margin=dict(l=15, r=15, t=60, b=15),
)


  
    return (
        gender_chart,
        age_chart,
        subscription_pie,
        age_gender_bar,
        state_chart,
      
    )
