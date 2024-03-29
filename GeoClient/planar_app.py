import dash_bootstrap_components as dbc
import folium
import haversine as hs
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output, State
from postgres import aggregator


def plot(n: int, epsilon: float):
    """
    Plot a two d map with circles containing the coordinates of all received noised geolocations
    :param n: number of requests
    :param epsilon: epsilon value
    :return: figure for 2d planar analysis
    """
    longitudes, latitudes, income, centroid, rect = aggregator(99.0)
    real_long = [float(i) for i in longitudes]
    real_lat = [float(i) for i in latitudes]
    radius = [0] * len(real_lat)
    for i in range(n):
        longitudes, latitudes, income, centroid, rect = aggregator(epsilon)
        long = [float(i) for i in longitudes]
        lat = [float(i) for i in latitudes]
        for k in range(len(real_lat)):
            new_max = hs.haversine((real_lat[k], real_long[k]), (lat[k], long[k]))
            if radius[k] < new_max:
                radius[k] = new_max

    coordinates = [
        {"name": "order", "lon": lon, "lat": lat, "rad": rad}
        for lon, lat, rad in zip(real_long, real_lat, radius)
    ]

    df = pd.DataFrame(coordinates)
    print("Create Folium Map")
    m2 = folium.Map(
        location=[12.97, 77.59],
        tiles="cartodbpositron",
        zoom_start=12,
        control_scale=True,
    )
    # marker_cluster2 = MarkerCluster().add_to(m2)

    for _, marker_data in df.iterrows():
        marker_location = [marker_data["lat"], marker_data["lon"]]
        radius = marker_data["rad"]
        folium.Circle(
            location=marker_location,
            radius=radius,
            color="blue",
            fill=True,
            fill_color="blue",
        ).add_to(m2)

    return m2._repr_html_()


def planar_layout():
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
                                id="num4",
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
                                id="epsilon4",
                            ),
                            html.Div(id="output4"),
                        ],
                        width=8,
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                dcc.Loading(
                                    id="loading4",
                                    type="circle",
                                    children=[
                                        html.Button(
                                            "Reload",
                                            id="evaluate-button4",
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
                                        html.Div(id="output_evaluation4"),
                                    ],
                                )
                            ]
                        ),
                        width=2,
                    ),
                ]
            ),
            html.Br(),
            html.Iframe(
                id="data_map4",
                srcDoc="",
                style={"marginTop": "1cm", "marginBottom": "1cm"},
                width="90%",
                height="600",
            ),
        ],
        style={"width": "100%"},
    )
    return layout


# define function for callbacks of planar evaluation page
def planar_callbacks(app):
    # callback to display selected values
    @app.callback(
        Output("output4", "children"),
        [Input("num4", "value"), Input("epsilon4", "value")],
    )
    def display_value(number, epsilon):
        return f"Number of Requests: {int(10 ** number)}, Epsilon: {round(float(10 ** epsilon - 1), 2)}"

    # callback to plot the 2d analysis figure
    @app.callback(
        Output("output_evaluation4", "children"),
        Output("data_map4", "srcDoc"),
        [State("num4", "value"), State("epsilon4", "value")],
        [Input("evaluate-button4", "n_clicks")],
    )
    def update_figure(value, epsilon, n_clicks):
        value = int(10**value)
        epsilon = float((10**epsilon) - 1)
        print("Start fetching")

        fig = plot(value, epsilon)

        return (
            f"Display 3D Distribution for n={value} and e={round(epsilon, 2)}",
            fig,
        )
