from datetime import datetime

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from evaluatorapp import evaluator_layout, update_evaluator
from postgres import aggregator

longitudes, latitudes, income, centroid, rect = aggregator()
income_mapping = {
    "10001 to 25000": 2.5,
    "25001 to 50000": 5,
    "More than 50000": 10,
    "Below Rs.10000": 1,
    "No Income": 0,
}
numerical_values = [income_mapping[range_] for range_ in income]
print(numerical_values)


app = dash.Dash(
    __name__, update_title=None, external_stylesheets=[dbc.themes.BOOTSTRAP]
)
app.title = "Analytics Dashboard"

# Define the navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/")),
        dbc.NavItem(dbc.NavLink("3D Analysis of Differential Privacy", href="/page1")),
        dbc.NavItem(dbc.NavLink("User Management", href="/page2")),
    ],
    brand="",
    color="#119dff",
    dark=True,
    style={
        "height": "80px",
        "line-height": "80px",
    },
)


# Define the page 1 layout
page1_layout = dbc.Container(
    [navbar, evaluator_layout()],
    fluid=True,
)
# Define the page 2 layout
page2_layout = html.Div(
    children=[navbar, html.H1("Page 2"), html.P("Welcome to Page 2!")], className="page"
)

homelayout = dbc.Container(
    [
        navbar,
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    html.H1(
                        "GDPR conform Analytics Dashboard for Food Delivery",
                        className="mb-4",
                    ),
                    width=6,
                ),
                dbc.Col(
                    dcc.Slider(0, 1, 0.1, value=0, id="epsilon"),
                    width=2,
                ),
                dbc.Col(
                    html.Div(
                        [
                            dcc.Loading(
                                id="loading",
                                type="circle",
                                children=[
                                    html.Button(
                                        "Reload",
                                        id="submit-button",
                                        n_clicks=0,
                                        style={
                                            "align": "center",
                                            "width": "50%",
                                            "height": "1cm",
                                            "display": "inline-block",
                                            "background-color": "#119dff",
                                            "border": "none",
                                            "color": "black",
                                        },
                                    ),
                                    html.Div(id="output"),
                                ],
                            )
                        ]
                    ),
                    width=2,
                ),
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id="density-heatmap",
                        figure=go.Figure(
                            data=go.Densitymapbox(
                                lon=longitudes,
                                lat=latitudes,
                                z=np.ones_like(latitudes),
                                radius=30,
                            ),
                            layout=go.Layout(
                                title="Areas with the highest number of Orders:",
                                mapbox=dict(
                                    style="open-street-map",
                                    center={"lat": 12.995, "lon": 77.5773},
                                    zoom=10,
                                ),
                                height=650,
                            ),
                        ),
                    ),
                    width=6,  # Set the width of the first column to 6
                ),
                dbc.Col(
                    dcc.Graph(
                        id="density-heatmap2",
                        figure=go.Figure(
                            data=go.Densitymapbox(
                                lon=longitudes,
                                lat=latitudes,
                                z=numerical_values,
                                radius=30,
                            ),
                            layout=go.Layout(
                                title="Areas with the highest Income:",
                                mapbox=dict(
                                    style="open-street-map",
                                    center={"lat": 12.995, "lon": 77.5773},
                                    zoom=10,
                                ),
                                height=650,
                            ),
                        ),
                    ),
                    width=6,  # Set the width of the second column to 6
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        children=[
                            dcc.Graph(
                                id="map-graph",
                                figure=px.scatter_mapbox(
                                    lat=[centroid[0]],
                                    lon=[centroid[1]],
                                    zoom=10,
                                    size=[10],
                                ).update_layout(
                                    title="Centroid:",
                                    height=650,
                                    mapbox={
                                        "style": "open-street-map",
                                        "center": {
                                            "lat": centroid[0],
                                            "lon": centroid[1],
                                        },
                                        "zoom": 15,
                                    },
                                ),
                            )
                        ]
                    ),
                    width=6,
                ),
                dbc.Col(
                    html.Div(
                        children=[
                            dcc.Graph(
                                id="map-graph1",
                                figure=go.Figure(
                                    data=go.Scattermapbox(
                                        lat=[i[1] for i in rect],
                                        lon=[i[0] for i in rect],
                                        fill="toself",
                                        marker={"size": 10, "color": "orange"},
                                    ),
                                    layout=go.Layout(
                                        height=650,
                                        title="Bounding Rectangle:",
                                        mapbox={
                                            "style": "open-street-map",
                                            "center": {
                                                "lat": 12.977,
                                                "lon": 77.5773,
                                            },  # Set the map's center
                                            "zoom": 9,
                                        },
                                    ),
                                ),
                            )
                        ]
                    )
                ),
            ]
        ),
    ],
    fluid=True,
)

app.layout = html.Div(
    children=[dcc.Location(id="url", refresh=False), html.Div(id="page-content")]
)

update_evaluator(app)


@app.callback(Output("output", "children"), [Input("submit-button", "n_clicks")])
def update_variable(n_clicks):
    global longitudes
    global latitudes
    global income
    global centroid
    global rect
    global numerical_values
    if n_clicks is not None:
        longitudes, latitudes, income, centroid, rect = aggregator()
        numerical_values = [income_mapping[range_] for range_ in income]
    return f'Refreshed: {datetime.now().strftime("%H:%M:%S")}'


# Callback to update the page content based on the URL
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page(pathname):
    if pathname == "/page1":
        return page1_layout
    elif pathname == "/page2":
        return page2_layout
    else:
        return homelayout


if __name__ == "__main__":
    app.run_server(debug=True)
