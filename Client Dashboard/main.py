import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import numpy as np
from postgres import connector


# Create the Dash app
app = dash.Dash(__name__, update_title=None, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Analytics Dashboard"




#df = pd.read_csv('onlinedeliverydata.csv')
#latitudes = df["latitude"]
#longitudes = df["longitude"]
#print(latitudes)
longitudes, latitudes, income, centroid, rect= connector()
income_mapping = {
    '10001 to 25000': 2.5,
    '25001 to 50000': 5,
    'More than 50000': 10,
    'Below Rs.10000': 1,
    'No Income': 0
}
numerical_values = [income_mapping[range_] for range_ in income]
print(numerical_values)
#latitudes.append(x)
#longitudes.append(y)
# Generate sample geo location data


# Define the layout
app.layout = dbc.Container(
    [
        html.Br(),
        html.H1("GDPR conform Analytics Dashboard for Food Delivery", className="mb-4"),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id='density-heatmap',
                        figure=go.Figure(
                            data=go.Densitymapbox(
                                lon=longitudes,
                                lat=latitudes,
                                z=np.ones_like(latitudes),
                                radius=30,
                            ),
                            layout=go.Layout(
                                title='Areas with the highest number of Orders:',
                                mapbox=dict(
                                    style='open-street-map',
                                    center={'lat': centroid[0], 'lon': centroid[1]},
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
                        id='density-heatmap2',
                        figure=go.Figure(
                            data=go.Densitymapbox(
                                lon=longitudes,
                                lat=latitudes,
                                z=numerical_values,
                                radius=30,
                            ),
                            layout=go.Layout(
                                title='Areas with the highest Income:',
                                mapbox=dict(
                                    style='open-street-map',
                                    center={'lat': centroid[0], 'lon': centroid[1]},
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
                        title='Centroid:',
                            height=650,
                            mapbox={
                        'style': 'open-street-map',
                        'center': {'lat': centroid[0], 'lon': centroid[1]},
                        'zoom': 15,
                    },
                    )
                    )
                    ]
                ),width = 6,
            ),
            dbc.Col(
                html.Div(
                    children=[
                        dcc.Graph(
                            id="map-graph1",
                            figure=go.Figure(
                                data = go.Scattermapbox(
                                    lat=[i[1] for i in rect],
                                    lon=[i[0] for i in rect],
                                    fill="toself",
                                    marker={'size': 10, 'color': "orange"}),
                                layout=go.Layout(
                                    height=650,
                                    title='Bounding Rectangle:',
                                    mapbox={
                                        'style': 'open-street-map',
                                        'center': {'lat': centroid[0], 'lon': centroid[1]},  # Set the map's center
                                        'zoom': 9,
                                    },
                                )
                            )
                        )
                    ]
                )
            )
            ]
        )
    ],
    fluid=True,
)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)