from datetime import datetime

import dash
import dash_bootstrap_components as dbc
import folium
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from creatorapp import creator_callbacks, creator_layout
from dash import dcc, html
from dash.dependencies import Input, Output, State
from evaluatorapp import evaluator_layout, update_evaluator
from folium.plugins import MarkerCluster
from planareval import planar_layout, update_planar
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
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)
app.title = "Analytics Dashboard"


def plot_number_orders(longitudes, latitudes):
    figure = go.Figure(
        data=go.Densitymapbox(
            lon=longitudes,
            lat=latitudes,
            # z=np.ones_like(latitudes),
            radius=5,
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
    )

    return figure


def plot_number_orders_new(longitudes, latitudes):
    coordinates = [
        {"name": "order", "lon": lon, "lat": lat}
        for lon, lat in zip(longitudes, latitudes)
    ]

    # Create a Pandas DataFrame to hold the coordinates
    df = pd.DataFrame(coordinates)
    print("Create Folium Map")
    # Create a map using Folium
    m = folium.Map(
        location=[12.97, 77.59],
        tiles="cartodbpositron",
        zoom_start=12,
        control_scale=True,
    )

    # Add marker clusters to the map
    marker_cluster = MarkerCluster().add_to(m)

    # Add markers to the marker cluster
    for _, row in df.iterrows():
        folium.Marker(location=[row["lat"], row["lon"]], popup=row["name"]).add_to(
            marker_cluster
        )

    return m._repr_html_()


def plot_income(longitudes, latitudes, numerical_values):
    figure = go.Figure(
        data=go.Densitymapbox(
            lon=longitudes,
            lat=latitudes,
            z=numerical_values,
            radius=30,
        ),
        layout=go.Layout(
            # title="Areas with the highest Income:",
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
    # print("plot", centroid)
    figure = px.scatter_mapbox(
        lat=[centroid[0]],
        lon=[centroid[1]],
        zoom=10,
        size=[10],
    ).update_layout(
        # title="Centroid:",
        height=600,
        mapbox={
            "style": "open-street-map",
            "center": {
                "lat": centroid[0],
                "lon": centroid[1],
            },
            "zoom": 15,
        },
    )
    return figure


def plot_rect(rect):
    figure = go.Figure(
        data=go.Scattermapbox(
            lat=[float(item[0]) for item in rect[0]],
            lon=[float(item[1]) for item in rect[0]],
            fill="toself",
            marker={"size": 10, "color": "orange"},
        ),
        layout=go.Layout(
            height=650,
            # title="Bounding Rectangle:",
            mapbox={
                "style": "open-street-map",
                "center": {
                    "lat": 12.977,
                    "lon": 77.5773,
                },  # Set the map's center
                "zoom": 9,
            },
        ),
    )
    return figure


homelayout = dbc.Container(
    [
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    "",
                    width=3,
                ),
                dbc.Col(
                    [
                        dcc.Slider(
                            0.01,
                            1.5,
                            0.01,
                            marks={
                                i: "{}".format(round((10**i) - 1), 2)
                                for i in [0.1, 0.3, 0.5, 0.7, 1, 1.2, 1.4]
                            },
                            value=1.5,
                            id="epsilon",
                        ),
                        html.Div(id="output_value_main"),
                    ],
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
                                            "background-color": "#0e1012",
                                            "border": "none",
                                            "color": "white",
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
                    html.P("Noised Order Locations:"),
                    width=6,  # Set the width of the first column to 6
                ),
                dbc.Col(
                    html.P("Noised Incomes:"),
                    width=6,  # Set the width of the second column to 6
                ),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Br(),
                        html.Br(),
                        html.Iframe(
                            id="data_map",
                            srcDoc="",
                            style={"margin-top": "1cm", "margin-bottom": "1cm"},
                            width="90%",
                            height="600",
                        ),
                    ],
                    width=6,  # Set the width of the first column to 6
                ),
                dbc.Col(
                    dcc.Graph(id="income_map"),
                    # dcc.Graph(
                    #   id="density-heatmap2",
                    # ),
                    width=6,  # Set the width of the second column to 6
                ),
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    html.P("Noised Centroid:"),
                    width=6,  # Set the width of the first column to 6
                ),
                dbc.Col(
                    html.P("Noised Bounding Rectangle:"),
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
                    ),
                    width=6,
                ),
            ]
        ),
    ],
    fluid=True,
)


app.layout = html.Div(
    [
        html.Div(
            html.H1(
                "GDPR conform Analytics Dashboard for Food Delivery",
                style={"color": "white", "margin": "0"},
            ),
            style={
                "background-color": "#0e1012",
                "padding": "16px 32px",
                "position": "sticky",
            },
        ),
        dbc.Tabs(
            [
                dbc.Tab(homelayout, label="Overview", style={"color": "#6c757d"}),
                dbc.Tab(
                    evaluator_layout(), label="3D Analysis", style={"color": "#6c757d"}
                ),
                dbc.Tab(
                    planar_layout(), label="Planar Analysis", style={"color": "#6c757d"}
                ),
                dbc.Tab(
                    creator_layout(),
                    label="User Management",
                    style={"color": "#6c757d"},
                ),
            ],
            style={"color": "#6c757d"},
        ),
    ]
)

update_evaluator(app)
update_planar(app)
creator_callbacks(app)


@app.callback(Output("output_value_main", "children"), Input("epsilon", "value"))
def display_value(epsilon):
    return f"Epsilon: {round(float((10 ** epsilon) - 1), 2)}"


@app.callback(
    [
        Output("output", "children"),
        Output("data_map", "srcDoc"),
        Output("income_map", "figure"),
        Output("map-graph", "figure"),
        Output("map-graph1", "figure"),
    ],
    [State("epsilon", "value")],
    [Input("submit-button", "n_clicks")],
)
def update_variable(epsilon, n_clicks):
    if n_clicks is not None:
        epsilon = float((10**epsilon) - 1)
        print("update")
        print("Started:", datetime.now())
        longitudes, latitudes, income, centroid, rect = aggregator(epsilon)
        print("Ended:", datetime.now())
        # print(longitudes, latitudes, income, centroid, rect)
        numerical_values = [income_mapping[range_] for range_ in income]
        figure1 = plot_number_orders_new(
            [float(i) for i in longitudes], [float(i) for i in latitudes]
        )
        figure2 = plot_income(
            [float(i) for i in longitudes],
            [float(i) for i in latitudes],
            numerical_values,
        )
        print("finished plot1+2")
        # print("update", centroid)
        figure3 = plot_centroid(centroid)
        print("finished centroid")
        # print("rect", rect)
        figure4 = plot_rect(rect)  # TODO: It has to stay a rectangle
        # print("LEngth:", len(longitudes))
        return (
            f'Refreshed: {datetime.now().strftime("%H:%M:%S")} with ε = {round(epsilon, 2)} ',
            figure1,
            figure2,
            figure3,
            figure4,
        )

    return

    # Callback to update the page content based on the URL


if __name__ == "__main__":
    app.run_server(debug=True)
