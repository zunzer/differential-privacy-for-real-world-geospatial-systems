import dash
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
import scipy.ndimage as ndimage
from dash import dcc, html
from dash.dependencies import Input, Output, State
from postgres import clean_centroid_result, execute_query


# requests a private centroid and returns a dict of centroids
def request_dp_centroid(epsilon, n: int):
    res = execute_query(f"SELECT private_centroid({epsilon}, {n});")
    return clean_centroid_result(res, "private_centroid")


# requests a real centroid and returns a dict of centroids
def request_centroid(n: int):
    res = execute_query(f"SELECT real_centroid({n});")
    return clean_centroid_result(res, "real_centroid")


# fetch private centroids and prepare them for plotting within the 3D evaluation
def fetch_dp_centroids(epsilon, n):
    coordinate_list = request_dp_centroid(epsilon, n)
    latitudes, longitudes = zip(*coordinate_list)
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


# prepare the private centroids and plot them within the 3D evaluationn
# applies gaussian smoothing of the aggregated data for visual purposes
def plot_3d_dp_centroids(x, y, z, sf):
    smoothed_z = ndimage.gaussian_filter(z, sigma=sf)
    fig = go.Figure(data=[go.Surface(x=x, y=y, z=smoothed_z)])
    fig.update_traces(
        contours_z=dict(
            show=True, usecolormap=True, highlightcolor="limegreen", project_z=True
        )
    )
    fig.update_layout(
        title=f"Differential Private Centroid with Smoothing Factor: {sf}",
        scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z"),
    )
    return fig


# plot the received real centroids within the 3D evaluation
def plot_3d_centroids(n):
    coordinate_list = request_centroid(n)
    latitudes, longitudes = coordinate_list[0], coordinate_list[1]
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
    fig.update_traces(
        contours_z=dict(
            show=True, usecolormap=True, highlightcolor="limegreen", project_z=True
        )
    )
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
                                value=1.2,
                                id="num",
                            ),
                            html.Label("Epsilon: "),
                            dcc.Slider(
                                0.01,
                                1.5,
                                0.01,
                                marks={
                                    i: "{}".format(round((10**i) - 1), 2)
                                    for i in [0.1, 0.3, 0.5, 0.7, 1, 1.2, 1.4]
                                },
                                value=1.5,
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
                                    id="loading3",
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
                                                "backgroundColor": "#0e1012",
                                                "border": "none",
                                                "color": "white",
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
    @app.callback(
        Output("output2", "children"),
        [Input("num", "value"), Input("epsilon2", "value")],
    )
    def display_value(number, epsilon):
        return f"Number of Requests: {int(10**number)}, Epsilon: {round(float(10**epsilon-1),2)}"

    @app.callback(
        Output("output_evaluation", "children"),
        Output("graph", "figure"),
        Output("graph1", "figure"),
        Output("graph2", "figure"),
        Output("graph3", "figure"),
        [State("num", "value"), State("epsilon2", "value")],
        [Input("evaluate-button", "n_clicks")],
    )
    # update the plotted centroid distributions by regenrating the plots with new input values for epsilon and n
    def update_figure(value, epsilon, n_clicks):
        value = int(10**value)
        epsilon = float((10**epsilon) - 1)
        print("Start fetching")
        fig1 = plot_3d_centroids(value)
        print("Plo1 ready")
        x, y, z = fetch_dp_centroids(epsilon, value)
        fig2 = plot_3d_dp_centroids(x, y, z, 1)
        fig3 = plot_3d_dp_centroids(x, y, z, 2)
        fig4 = plot_3d_dp_centroids(x, y, z, 3)
        print("Received plots")
        return (
            f"Display 3D Distribution for n={value} and e={round(epsilon,2)}",
            fig1,
            fig2,
            fig3,
            fig4,
        )
