import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import date

# Da die App via RENDER deployed wird, erfolgt der Zugriff auf den Token via .yaml-File
import os
token = os.environ.get('mapbox_token')

# Dies ist die Variante für eine lokale Verwendung
# token = open("../.env").read()


dash.register_page(__name__, name="Füllstände")

# Read and prep data
df_geo = pd.read_csv('assets/df_geo_cond.csv',  sep=",")
df_location = df_geo.groupby('Sensorname').first().reset_index()

# Components
control = html.Div
sorten_des3 = dbc.Card(dbc.CardBody([
                                    html.H5("Diese Seite ist interaktiv...", className="card-title"),
                                    html.Hr(),
                                    html.H6('''-Im 1. Schritt können die Sammelbehälter (Sensoren) nach
                                            Farbe, Datum und Füllstand gefiltert werden. Die Karte rechts neben dem 
                                            Filter zeigt die verbleibenden Sammelbehälter'''),
                                    html.H6('''-Der 2. Schritt basiert auf dieser Vorauswahl. In der Drop-Down-Liste 
                                            zur Auswahl des Sensons sind nur die Sammelcontainer zu finden, welche die 
                                            Kriterien zu Farbe, Datum und Füllstand erfüllen. Zum ausgewählten Sensor wird
                                            ein Barchart mit maximal verfügbarer Länge gezeigt.'''),
                                    html.P("""DISCLAIMER: Die Sensordaten wurden im Sommer 2023 von dem Open Data Portal
                                           gezogen. Mir scheint, dass es im Sinne der Datenqualität noch Potential nach 
                                           oben gibt. Da es mir für meinen Zweck primär um die Erstellung einer Multipage-App 
                                           mit DASH ging, habe ich auf eine EDA (Explorative Datenanalyse) verzichtet! """),
                                    
                                    ]) , className="mx-5")


auswahl = dbc.Card(
            [   
                dbc.CardBody(
                    [
                    html.H5("1. Filtern der Sammelcontainer", className="card-title"),
                    html.H6("Farbe", className="card-title"),
                    dbc.Checklist(
                                id="checklist_farbe",
                                options=[{'label': "Grün", 'value': "Grün"},
                                         {'label': "Weiss", 'value': "Weiss"},
                                         {'label': "Braun", 'value': "Braun"},
                                          ],   
                                value=["Grün", "Weiss", "Braun"],
                                inline=True
                        )
                    ],
                    style={"height": "7rem"},

                ),
                dbc.CardBody(
                    [
                    html.H6("Datum", className="card-title"),
                    dcc.DatePickerSingle(
                        id='my-date-picker-single',
                        min_date_allowed=date(2021, 9, 8),
                        max_date_allowed=date(2022, 5, 21),
                        initial_visible_month=date(2021, 9, 8),
                        date=date(2021, 9, 8)
                        )
                    ],
                    style={"height": "6rem"},                    
                ),
                dbc.CardBody(
                    [
                    html.H6("Füllstand (einstellbar in 100-Schritten)", className="card-title"),
                    dcc.RangeSlider(
                        id='slider_range',
                        min=0,
                        max=2500,
                        step=100,
                        marks={ i: f"{i:.0f}" for i in range(0, 2501, 500)},
                        value=[400,1000],
                        included=False,
                        )
                    ],
                    style={"height": "8rem"},                    
                ),
            ],
    body=True,
    className="mx-5",
)

auswahl2 = dbc.Card(
            [   
                dbc.CardBody(
                    [
                    html.H5("2. Auswahl des Sensors", className="card-title"),
                    dcc.Dropdown(
                        id="dd",
# Die Options werden dynamisch mittels Callback definiert
                                value='107053 | 667E'
                                )
                    ],
                    style={"height": "7rem"},
                ),
            ],
    body=True,
    className="mx-5",
)

# Layout
control = html.Div
layout = html.Div(
     [
     dbc.Row([dbc.Col(sorten_des3, width={"size": 10, "offset": 1}, align="center")]),
     dbc.Row([dbc.Col(auswahl, style={'margin-top': '55px'}, md=4, align="top"), dbc.Col(dcc.Graph(id="map_container"), md=8)]),
     dbc.Row([dbc.Col(auswahl2, style={'margin-top': '55px'}, md=4, align="top"), dbc.Col(dcc.Graph(id="bar_sensor"), md=8)]),
    ]
)


# functions
def filter_df(farben, datum, slider_range ):
    low = slider_range[0] 
    high = slider_range[1] 
    df_filtered = df_geo.query('Zeitpunkt == @datum')

    df_filtered = df_filtered.query('color in @farben')

    df_filtered = df_filtered.query('@low <= Füllstandsdistanz <= @high')
    return df_filtered

# Callbacks
@callback(
    Output("map_container", "figure"),
    Input("checklist_farbe", "value"),
    Input("my-date-picker-single", "date"),  
    Input("slider_range", "value")
)
def fig_update(farben, datum, slider_range):
        df_filtered = filter_df(farben, datum, slider_range)
        df_filtered = df_filtered.groupby('Sensorname').first().reset_index()

        fig = px.scatter_mapbox(df_filtered, lat="latitude", lon="longitude", color=df_filtered['color'], 
                                size=df_filtered['Füllstandsdistanz'],
                                color_discrete_map={"Grün": "#8A972B", "Weiss": "#D2B48C", "Braun": "#8E5100"}, 
                                hover_data={'longitude':False, 'latitude':False, 'color':True, 'Füllstandsdistanz':True, 'Sensorname':True},
                                zoom=12, height=500)
        fig.update_layout(mapbox_style="streets", mapbox_accesstoken = token, legend = dict(bgcolor = '#FDFDFD', title_text=''))
        return fig

@callback(
    Output("dd", "options"),
    Input("checklist_farbe", "value"),
    Input("my-date-picker-single", "date"),  
    Input("slider_range", "value"),
)
def list_update(farben, datum, slider_range):
        df_filtered = filter_df(farben, datum, slider_range)
        auswahl=[{'label': i, 'value': i} for i in df_filtered.Sensorname.unique()]
        # print("AAA ", auswahl)
        return auswahl

@callback(
    Output("bar_sensor", "figure"),
    Input("dd", "value"),
)
def graph_update(sensor):
       df_graph = df_geo[df_geo["Sensorname"] == sensor]
    #    print(sensor)
    #    print("GGG ", df_graph)
       fig=px.bar(df_graph, x="Zeitpunkt", y="Füllstandsdistanz", 
                  labels={'Zeitpunkt': '','Füllstandsdistanz': 'Füllstand'})
       return fig