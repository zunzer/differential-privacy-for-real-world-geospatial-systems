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


def plot_number_orders(longitudes, latitudes):
    figure = go.Figure(
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
        ))

    return figure

def plot_income(longitudes, latitudes, numerical_values):
    figure = go.Figure(
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
    )
    return figure

def plot_centroid(centroid):
    figure = px.scatter_mapbox(
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
    return figure

def plot_rect(rect):
    figure = go.Figure(
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
        )
    )
    return figure

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
                    dcc.Graph(id="density-heatmap"),
                    width=6,  # Set the width of the first column to 6
                ),
                dbc.Col(
                    dcc.Graph(
                        id="density-heatmap2",
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


@app.callback([Output("output", "children"), Output("density-heatmap", "figure"), Output("density-heatmap2", "figure"), Output("map-graph", "figure"), Output("map-graph1", "figure")], [Input("epsilon","value"), Input("submit-button", "n_clicks")])
def update_variable(value, n_clicks):
    if n_clicks is not None:
        print("update")
        longitudes, latitudes, income, centroid, rect = aggregator(value)
        print(longitudes, latitudes, income, centroid, rect)
        numerical_values = [income_mapping[range_] for range_ in income]
        figure1 = plot_number_orders([float(i) for i in longitudes], [float(i) for i in latitudes])
        print("finished plot1")
        figure2 = plot_income([float(i) for i in longitudes], [float(i) for i in latitudes], numerical_values)
        print("finished plot2")
        figure3 = plot_centroid(centroid)
        print("finished centroid")
        figure4 = plot_rect(rect)
        print("LEngth:", len(longitudes))
        return f'Refreshed: {datetime.now().strftime("%H:%M:%S")}', figure1,figure2,figure3,figure4,

    return



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
