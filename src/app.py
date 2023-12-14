import dash 
from dash import Dash, dcc, html, callback
import dash_bootstrap_components as dbc

app = Dash(__name__, suppress_callback_exceptions=True, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Seite 1: Historie & Mengen   ", href="/", style={'font-weight': 'bold'})),
        dbc.NavItem(dbc.NavLink("Seite 2: Farbe & Standorte   ", href="/page2", style={'font-weight': 'bold'})),
        dbc.NavItem(dbc.NavLink("Seite 3: Sensoren & Füllstände", href="/page3", style={'font-weight': 'bold'})),
    ],
    brand="Glasabfall in der Stadt St. Gallen", 
    brand_href="#",
    color="success",
    dark=True,
)

app.layout = html.Div(
    [
        navbar,
        # html.Hr(),
        dash.page_container,
    ]
)


if __name__ == "__main__":
    app.run_server(debug=True, port=8054)