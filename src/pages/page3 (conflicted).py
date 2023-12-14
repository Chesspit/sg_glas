import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import date

token = open("../.env").read()

csequence = ['#8A972B', '#FDFDFD', '#C67500']


dash.register_page(__name__, name="Füllstände")

df_geo = pd.read_csv('assets/df_geo_cond.csv',  sep=",")
df_location = df_geo.groupby('Sensorname').first().reset_index()
# print("LOCATION: ", df_location)
# print("GEO: ", df_geo)

sorten_des3 = dbc.Card(dbc.CardBody("""Auf dieser Seite ist eine Durchsicht bis auf das Level eines einzelnen 
                                    Sammelcontainers möglich. Im ersten Schritt kann man die Sammelcontainer nach 
                                    den Kriterien Farbe, Datum und Füllstand filtern. Die Grafik wird entsprechend
                                    angepasst. Im zweiten Schritt erfolgt die Auswahl eines einzelnen Sammelcontainers.
                                    Der Verlauf des Füllstandslevels wird grafisch angezeigt"""), className="mx-5",)

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
                    # dcc.RangeSlider(   marks={ i: f"{i:.0f}" for i in range(2015, 2022, 1)})
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
)

auswahl2 = dbc.Card(
            [   
                dbc.CardBody(
                    [
                    html.H5("2. Auswahl des Sensors", className="card-title"),
                    # html.H6("Farbe", className="card-title"),
                    dcc.Dropdown(
                        id="liste",
                        # options=[
                        #         {'label': i, 'value': i} for i in dff.Sensorname.unique()
                        #         ],
                                value='107053 | 667E'
                                )
                    ],
                    style={"height": "7rem"},
                ),
            ],
    body=True,
)



# map_sammelcontainer = dbc.Card(dbc.CardBody("Auf der Grafik sind die Standorte von Glascontainer mit Sensoren zu sehen "), className="mx-5",)

# location_des3 = dbc.Card(dbc.CardBody("Auf der Grafik sind die Standorte von Glascontainer mit Sensoren zu sehen "), className="mx-5",)

graph_location3 = dbc.Card(dbc.CardBody("Auf der Grafik sind die Standorte von Glascontainer mit Sensoren zu sehen "), className="mx-5",)

layout = html.Div(
     [
     dbc.Row([dbc.Col(sorten_des3, width={"size": 10, "offset": 1}, align="center")]),
     dbc.Row([dbc.Col(auswahl, md=4, align="center"), dbc.Col(dcc.Graph(id="map_sammelcontainer"), md=8)]),
     dbc.Row([dbc.Col(auswahl2, md=4, align="center"), dbc.Col(dcc.Graph(id="graph_sensor"), md=8)]),
    ]
)

# layout = html.Div(
#      [dbc.Row([dbc.Col(sorten_des3, md=4, align="center"), dbc.Col(dcc.Graph(id="map_sammelcontainer"), md=8)]),
#      dbc.Row([dbc.Col(auswahl, md=4, align="center"), dbc.Col(graph_location3, md=8)])
#     ]
# )



# functions
def filter_df(farben, datum, slider_range ):
    # low, high = slider_range 
    low = slider_range[0] 
    high = slider_range[1] 
    # print("DATUM ", datum)
    df_filtered = df_geo.query('Zeitpunkt == @datum')
    # print("DF_FIL_D", df_filtered.tail())

    # print("FARBE ", checklist_farbe)
    df_filtered = df_filtered.query('color in @farben')
    # print("DF_FIL_C", df_filtered.tail())

    df_filtered = df_filtered.query('@low <= Füllstandsdistanz <= @high')
    # print("DF_FIL_R", df_filtered.tail())
    return df_filtered

# Callbacks
@callback(
    Output("map_sammelcontainer", "figure"),
    Input("checklist_farbe", "value"),
    Input("my-date-picker-single", "date"),  
    Input("slider_range", "value")
)
def fig_update(farben, datum, slider_range):
        # low, high = slider_range 
        # print("SLIDER ", slider_range)
        # print("DATUM ", datum)
        # print("FARBE ", farben)
        df_filtered = filter_df(farben, datum, slider_range)
        # print("DF_FIL_MAP1 ", df_filtered.tail())
        df_filtered = df_filtered.groupby('Sensorname').first().reset_index()
        # print("DF_FIL_MAP2 ", df_filtered.tail())

        fig = px.scatter_mapbox(df_filtered, lat="latitude", lon="longitude", color=df_filtered['color'], size=df_filtered['Füllstandsdistanz'],
                                color_discrete_map={"Grün": "8A972B", "Weiss": "#FDFDFD", "Braun": "#C67500"}, zoom=12, height=600)
        fig.update_layout(mapbox_style="streets", mapbox_accesstoken = token, legend = dict(bgcolor = '#F5F5F5', title_text=''))
        return fig

@callback(
    Output("liste", "options"),
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
    Output("graph_sensor", "figure"),
    Input("liste", "value"),
)
def graph_update(sensor):
       df_graph = df_geo[df_geo["Sensorname"] == sensor]
    #    print(sensor)
    #    print("GGG ", df_graph)
       fig=px.bar(df_graph, x="Zeitpunkt", y="Füllstandsdistanz")
       return fig