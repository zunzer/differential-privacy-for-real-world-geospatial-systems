import dash
import dash_bootstrap_components as dbc
import numpy as np
import plotly.graph_objects as go
import scipy.ndimage as ndimage
from dash import dcc, html
from dash.dependencies import Input, Output, State
from postgres import execute_query


def creator_layout():
    layout = dbc.Container(
        [
            html.Br(),
            html.Div(
                [
                    html.Label("Latitude: "),
                    dcc.Input(
                        id="latitude-input",
                        type="number",
                        value=None,
                        style={"width": "100%"},
                    ),
                ]
            ),
            html.Br(),
            html.Div(
                [
                    html.Label("Longitude: "),
                    dcc.Input(
                        id="longitude-input",
                        type="number",
                        value=None,
                        style={"width": "100%"},
                    ),
                ]
            ),
            html.Br(),
            html.Div(
                [
                    html.Label("Income: "),
                    dcc.Dropdown(
                        id="income",
                        options=[
                            {"label": "10001 to 25000", "value": "10001 to 25000"},
                            {"label": "25001 to 50000", "value": "25001 to 50000"},
                            {"label": "More than 50000", "value": "More than 50000"},
                            {"label": "Below Rs.10000", "value": "Below Rs.10000"},
                            {"label": "No Income", "value": "No Income"},
                        ],
                        value="",
                    ),
                ]
            ),
            html.Br(),
            html.Div(
                [
                    dcc.Loading(
                        id="loading2",
                        type="circle",
                        children=[
                            html.Button(
                                "Add Datapoint",
                                id="submit-query",
                                n_clicks=0,
                                style={
                                    "align": "center",
                                    "width": "100%",
                                    "height": "1cm",
                                    "display": "inline-block",
                                    "background-color": "#0e1012",
                                    "border": "none",
                                    "color": "white",
                                },
                            ),
                            html.Div(id="output-submit"),
                        ],
                    )
                ]
            ),
            html.Br(),
            html.Br(),
            html.Div(
                [
                    dcc.Loading(
                        id="loading21",
                        type="circle",
                        children=[
                            html.Button(
                                "Delete all added Datapoints",
                                id="delete-query",
                                n_clicks=0,
                                style={
                                    "align": "center",
                                    "width": "100%",
                                    "height": "1cm",
                                    "display": "inline-block",
                                    "background-color": "#0e1012",
                                    "border": "none",
                                    "color": "white",
                                },
                            ),
                            html.Div(id="output-delete"),
                        ],
                    )
                ]
            ),
        ],
        style={"width": "100%"},
    )
    return layout


# Callback to update the values of the figure


def creator_callbacks(app):
    @app.callback(
        Output("output-submit", "children"),
        [
            State("longitude-input", "value"),
            State("latitude-input", "value"),
            State("income", "value"),
        ],
        Input("submit-query", "n_clicks"),
    )
    def display_value(long, lat, income, nclicks):
        max_index = execute_query(
            "SELECT MAX(index) FROM public.online_delivery_data;"
        )._mapping["max"]
        if (
            nclicks > 0
            and type(long) == float
            and type(lat) == float
            and abs(lat) < 90.0
            and abs(long) < 180.0
        ):
            print("Execute insert")
            # add a new database entry based on the selected coordinates and income values
            _ = execute_query(
                f"INSERT INTO public.online_delivery_data VALUES ({int(max_index) + 1}, 20, 'Female', 'Married', 'Student','{str(income)}', 'Post Graduate', 3, 560001, 'Food delivery apps', 'Web browser', 'Breakfast', 'Lunch', 'Non Veg foods (Lunch / Dinner)', 'Bakery items (snacks)', 'Neutral', 'Neutral',	'Neutral',	'Neutral',	'Neutral', 'Neutral', 'Neutral', 'Neutral',	'Neutral', 'Neutral', 'Neutral', 'Neutral', 'Neutral', 'Neutral', 'Agree', 'Agree',	'Agree', 'Agree', 'Agree', 'Agree',	'Yes', 'Weekend (Sat & Sun)', '30 minutes', 'Agree', 'Neutral', 'Neutral', 'Neutral', 'Neutral', 'Yes', 'Moderately Important', 'Moderately Important', 'Moderately Important', 'Moderately Important', 'Moderately Important', 'Moderately Important', 'Moderately Important', 'Moderately Important', 'Yes', 'TEST ENTRY', ST_GeometryFromText('POINT ({long} {lat})', 4326));",
                unfetched_output=True,
            )
            print("Executed insert")
            return f"Value: {long},{lat},{income}, {nclicks}"
        elif nclicks > 0:
            return "Invalid coordinates. Coordinates have to be entered as a float. (e.g. 32.215)"
        else:
            print("Insert failed")
            return

    @app.callback(
        Output("output-delete", "children"), Input("delete-query", "n_clicks")
    )
    # delete all new user added vlues from the database
    def display_value(nclicks):
        if nclicks > 0:
            print("Execute delete")
            _ = execute_query(
                "DELETE FROM public.online_delivery_data WHERE index >= 388;",  # original dataset only consists of 387 entries
                unfetched_output=True,
            )
            print("Finished delete")
            return "All values deleted"
        else:
            print("Deletion failed")
            return
