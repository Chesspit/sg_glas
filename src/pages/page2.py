import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Da die App via RENDER deployed wird, erfolgt der Zugriff auf den Token via .yaml-File
import os
token = os.environ.get('mapbox_token')

# Dies ist die Variante für eine lokale Verwendung
# token = open("../.env").read()

dash.register_page(__name__, name="Farbe und Standort")


# Hier beginnt das Einlesen und Bearbeiten der Daten für die Glassorten, dh die 3 Farben
df = pd.read_csv('assets/entsorgungsstatistik-stadt-stgallen.csv',  sep=";", parse_dates=['Monat_Jahr'])
df=df.drop(df.columns[0:1], axis=1)
df=df.drop(df.columns[3:8], axis=1)
df=df[df['Abfallfraktion'] == 'Glas']
df=df[df['Unterkategorie'].notna()]
df.rename(columns={'Gewicht in t': 'Gewicht', 'Unterkategorie': 'Glassorte'}, inplace=True)
df['Glassorte'] = df['Glassorte'].str[:-4]
# Der Dataframe für die erste Grafik ist fertig. Diese wird mit den nächsten beiden Zeilen erzeugt.

csequence = ['#8A972B', '#F5F5DC', '#8E5100']
csequence_map = ['#8A972B', '#D2B48C', '#8E5100']

bar_sorten = px.bar(df, x="Monat_Jahr", y="Gewicht", color="Glassorte", opacity=0.7, color_discrete_sequence=csequence, 
                    labels={'Monat_Jahr': 'Zeitpunkt','Gewicht': 'Gewicht (in Tonnen)'}, range_x=['2021-12-15', '2023-12-31'], height=450)
bar_sorten.update_layout(legend = dict(bgcolor = '#FDFDFD', title_text=''))

# Hier beginnt das Einlesen und Bearbeiten der Daten für die Füllstandssensoren
df_geo = pd.read_csv('assets/df_geo_cond.csv',  sep=",")
df_location = df_geo.groupby('Sensorname').first().reset_index()

fig_location = px.scatter_mapbox(df_location, lat="latitude", lon="longitude", color=df_location['color'], size=df_location['Füllstandsdistanz'],
                          color_discrete_sequence=csequence_map, 
                          hover_data={'longitude':True, 'latitude':True, 'color':True, 'Füllstandsdistanz':False}, 
                            zoom=12, height=500)
fig_location.update_layout(mapbox_style="streets", mapbox_accesstoken = token, legend = dict(bgcolor = '#FDFDFD', title_text=''))


# Components
sorten_des = dbc.Card(dbc.CardBody([
                                    html.H5("Ab 2022 wird es bunt...", className="card-title"),
                                    html.Hr(), 
                                    html.P('''Die Daten zu den Glasabfällen werden nun in die Farben Grün, Weiss und Braun aufgeteilt.
                                           In der Regel ist die Menge an eingeworfenen grünen Flaschen etwas grösser
                                           als die der Weissen. Die genauen Zahlen lassen sich durch Bewegen des Mauszeigers
                                           über die Grafik ablesen.'''),
                                    html.H6("3. Grafik: Monatliche Entwicklung der Gesamtmengen nach Farbe")
                                    ]) , className="mx-5")

graph_sorten = dcc.Graph(id="bar_sorten", figure=bar_sorten)

location_des = dbc.Card(dbc.CardBody([html.H6("4. Grafik: Sammelcontainer in St. Gallen mit Füllstandsmessung"), 
                                      html.P('''Hinweis: Durch Scrollen mit der Maus kann in die Karte hineingezoomt
                                             werden.'''),       
                                    ]), className="mx-5",)

graph_location = dcc.Graph(id="map_location", figure=fig_location)

# Layout
layout = html.Div(
     [dbc.Row([dbc.Col(sorten_des, style={'margin-top': '55px'}, md=4, align="top"), dbc.Col(graph_sorten, md=8)]),
     dbc.Row([dbc.Col(location_des, style={'margin-top': '55px'}, md=4, align="top"), dbc.Col(graph_location, md=8)])
    ]
)


# if __name__ == '__main__':
#     app.run_server(debug=True, port = 8056)