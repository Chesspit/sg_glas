import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


dash.register_page(__name__, path='/', name="Mengen")

# Read and prep data
df = pd.read_csv('assets/entsorgungsstatistik-stadt-stgallen.csv' , sep=";")
df=df.drop(df.columns[4:9], axis=1)
df=df[df['Abfallfraktion'] == 'Glas']
df.sort_values('Monat_Jahr', inplace=True)
df['Jahr'] = df['Monat_Jahr'].str.split('-').str[0].astype(int)
df['Monat'] = df['Monat_Jahr'].str.split('-').str[1].astype(int)
df['Jahr_str'] = df['Monat_Jahr'].str.split('-').str[0].astype(str)

# define color schemes
color_dict_int = {
    2015: '#b2b2b2',
    2016: '#999999',
    2017: '#7f7f7f',
    2018: '#666666',
    2019: '#4c4c4c',
    2020: '#333333',
    2021: '#1a1a1a',
    2022: '#000000'
}

color_dict_str = {
    '2015': '#b2b2b2',
    '2016': '#999999',
    '2017': '#7f7f7f',
    '2018': '#666666',
    '2019': '#4c4c4c',
    '2020': '#333333',
    '2021': '#1a1a1a',
    '2022': '#000000'
}
  
color_seq=[ '#e5e5e5', '#cccccc', '#b2b2b2', '#999999', '#7f7f7f', '#666666', '#4c4c4c', '#333333']


# Components
control = html.Div(
    [
        html.Label("Einstellung Zeitraum", style={'margin': '5px', 'margin-left': '20px', 'color': 'gray', 'font-weight': 'bold'}, htmlFor="my-range-slider"),
        dcc.RangeSlider(min=2015, max=2021, step=1, value=[2017, 2021], id='my-range-slider',  marks={ i: f"{i:.0f}" for i in range(2015, 2022, 1)})
    ] 
)

einleitung = dbc.Card(dbc.CardBody([
                                    html.H5("Einleitung", className="card-title"),
                                    html.Hr(), 
                                    html.P('''Diese App basiert auf Informationen, die auf dem 
                                            Open Data Portal der Stadt St. Gallen zu finden sind. 
                                           Auf 3 Seiten ist zu sehen, wie die Granularität der Daten
                                           immer besser wird. Für die ersten Jahre gibt es nur eine
                                            Gesamtmenge, dann erfolgt eine Aufsplittung in Farben und
                                           ab Ende 2021 wurden die Sammelcontainer mit Sensoren ausgestattet,
                                           die den Füllstand messen.'''),
                                    html.H6("1. Grafik: Monatliche Entwicklung der Gesamtmengen")
                                    ]) , className="mx-5")


graph_gesamt = dcc.Graph(id="bar")

saison_des = dbc.Card(dbc.CardBody([html.H6("2. Grafik: Saisonalitäten"),
                                    html.P("Bei den Saisonalitäten zeigen sich die geringsten Mengen im \
                                   Spätsommer, während über den Winter ein Anstieg zu beobachten ist")
                                   ]), className="mx-5",)

graph_saison = dcc.Graph(id="bar2",  style={'height': '480px'})

# Layout
layout = html.Div(
    [
    dbc.Row([ dbc.Col( control, width={"size": 6, "offset": 5})]),
    dbc.Row([dbc.Col(einleitung, style={'margin-top': '55px'}, md=4, align="top"), dbc.Col(graph_gesamt, md=8)]),
    dbc.Row([dbc.Col(saison_des, style={'margin-top': '85px'}, md=4, align="top"), dbc.Col(graph_saison, md=8)], style={'margin-top': '-50px'})
    ]
)

# Callbacks
@callback(
    Output("bar", "figure"),
    Input("my-range-slider", "value"),
)
def update_barchart(slider_range):
    low, high = slider_range 
    mask = (df["Jahr"] >= low) & (df["Jahr"] <= high)
    fig1 = px.bar(
        df[mask],
        x="Monat_Jahr",
        y="Gewicht in t",
        color='Jahr_str',
        color_discrete_map=color_dict_str,
        # Hier verwende ich ...dict_str, weil Jahr_str ein String ist. Und ohne Strings könnte ich kein diskretes Mapping verwenden
        labels={'Monat_Jahr': 'Zeitpunkt', 'Gewicht in t': 'Gewicht (in Tonnen)'},
        hover_data={'Monat_Jahr':False, 'Jahr_str': False, 'Gewicht in t': ':.1f', 'Monat': True }
    )
    fig1.update_layout(yaxis_range=[140,280], xaxis_tickangle=20, showlegend=False) 
    fig1.update_xaxes(title='')
    return fig1


@callback(
    Output("bar2", "figure"),
    Input("my-range-slider", "value"),
)
def update_linechart(slider_range):
    low, high = slider_range
    years = range(low, high+1)
    fig2 = go.Figure()
    for year in years: 
        fig2 = fig2.add_trace(go.Bar(name=year, x = df.loc[df["Jahr"] == year, "Monat"], 
                                        y= df.loc[df["Jahr"] == year, "Gewicht in t"],
                                        hovertemplate= '<b>Gewicht</b>: %{y:.1f}',
                                        marker=dict(color=color_dict_int[year]
                                # Hier verwende ich ...dict_int, weil year ein numerischer Wert ist
                                                    )))
    fig2.update_layout(yaxis_range=[140,280], 
                       xaxis=dict(title='Monat', tickmode = 'array', tickvals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], 
                                  ticktext = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']), 
                       yaxis={'title':'Gewicht (in Tonnen)'},
                       legend=dict(x=0.02, y=1.02, orientation="h", yanchor='bottom')
                       )
    fig2.update_xaxes(title='')
    return fig2


# if __name__ == '__main__':
#     app.run_server(debug=True, port = 8055)