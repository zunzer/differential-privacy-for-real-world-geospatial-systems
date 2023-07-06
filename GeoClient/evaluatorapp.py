import dash
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
import scipy.ndimage as ndimage
from dash import dcc, html
from dash.dependencies import Input, Output, State
from postgres import clean_centroid_result, execute_query


def request_dp_centroid(epsilon, n: int):
    # test3 = session.execute(text("SELECT ST_AsText(st_centroid(st_union(geom))) FROM public.online_delivery_data"))
    res = execute_query(f"SELECT private_centroid({epsilon}, {n});")
    return clean_centroid_result(res, "private_centroid")


def request_centroid(n: int):
    res = execute_query(f"SELECT real_centroid({n});")
    return clean_centroid_result(res, "real_centroid")


def fetch_dp_centroids(epsilon, n):
    longitudes, latitudes = request_dp_centroid(epsilon, n)
    lon_min = min(longitudes) - 5
    lon_max = max(longitudes) + 5
    lat_min = min(latitudes) - 5
    lat_max = max(latitudes) + 5

    x = list(range(int(lon_min), int(lon_max), 1))
    y = list(range(int(lat_min), int(lat_max), 1))
    z = np.zeros((len(y), len(x)))

    for i in range(len(latitudes)):
        z[int(latitudes[i] - lat_min), int(longitudes[i] - lon_min)] += 1

    return x, y, z


def plot_3d_dp_centroids(x, y, z, sf):
    smoothed_z = ndimage.gaussian_filter(z, sigma=sf)
    fig = go.Figure(data=[go.Surface(x=x, y=y, z=smoothed_z)])
    fig.update_layout(
        title=f"Differential Private Centroid with Smoothing Factor: {sf}",
        scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z"),
    )
    return fig


def plot_3d_centroids(n):
    longitudes, latitudes = request_centroid(n)
    lon_min = min(longitudes) - 5
    lon_max = max(longitudes) + 5
    lat_min = min(latitudes) - 5
    lat_max = max(latitudes) + 5
    x = list(range(int(lon_min), int(lon_max), 1))
    y = list(range(int(lat_min), int(lat_max), 1))
    z = np.zeros((len(y), len(x)))
    for i in range(len(latitudes)):
        z[int(latitudes[i] - lat_min), int(longitudes[i] - lon_min)] += 1

    fig = go.Figure(data=[go.Surface(x=x, y=y, z=z)])
    fig.update_layout(
        title="Received Centroids without Differential Privacy",
        scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z"),
    )
    return fig


def evaluator_layout():
    layout = dbc.Container(
        [
            html.Br(),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Number of requests: "),
                            dcc.Slider(
                                1,
                                4,
                                0.01,
                                marks={i: "{}".format(10**i) for i in range(5)},
                                value=0,
                                id="num",
                            ),
                            html.Label("Epsilon: "),
                            dcc.Slider(
                                0.001,
                                2.5,
                                0.01,
                                marks={i: "{}".format((10 ** i)-1) for i in range(5)},
                                value=0,
                                id="epsilon2",
                            ),
                            html.Div(id="output2"),
                        ],
                        width=8,
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
                                            id="evaluate-button",
                                            n_clicks=0,
                                            style={
                                                "align": "center",
                                                "width": "50%",
                                                "height": "1cm",
                                                "display": "inline-block",
                                                "backgroundColor": "#119dff",
                                                "border": "none",
                                                "color": "black",
                                            },
                                        ),
                                        html.Div(id="output_evaluation"),
                                    ],
                                )
                            ]
                        ),
                        width=2,
                    ),
                ]
            ),
            html.Br(),
            dcc.Graph(id="graph", style={"width": "1000px", "height": "1000px"}),
            dcc.Graph(id="graph1", style={"width": "1000px", "height": "1000px"}),
            dcc.Graph(id="graph2", style={"width": "1000px", "height": "1000px"}),
            dcc.Graph(id="graph3", style={"width": "1000px", "height": "1000px"}),
        ],
        style={"width": "100%"},
    )
    return layout


# Callback to update the values of the figure


def update_evaluator(app):
    @app.callback(Output("output2", "children"), Input("num", "value"), Input("epsilon2", "value"))
    def display_value(value):
        return f"Number of Requests: {int(10**value)}, Epsilon: {int(10**value-1)}"

    @app.callback(
        Output("output_evaluation", "children"),
        Output("graph", "figure"),
        Output("graph1", "figure"),
        Output("graph2", "figure"),
        Output("graph3", "figure"),
        [State("num", "value"), State("epsilon2", "value")],
        [Input("evaluate-button", "n_clicks")],
    )
    def update_figure(value, epsilon, n_clicks):
        value = int(10**value)
        epsilon = int((10**epsilon)-1)
        print("Start fetching")
        fig1 = plot_3d_centroids(value)
        print("Plo1 ready")
        x, y, z = fetch_dp_centroids(epsilon, value)
        fig2 = plot_3d_dp_centroids(x, y, z, 1)
        fig3 = plot_3d_dp_centroids(x, y, z, 2)
        fig4 = plot_3d_dp_centroids(x, y, z, 3)
        print("Received plots")
        return (
            f"Display 3D Distribution for n={value} and e={epsilon}",
            fig1,
            fig2,
            fig3,
            fig4,
        )
