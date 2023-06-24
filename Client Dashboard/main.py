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
longitudes, latitudes, income = connector()
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
        html.H1("GDPR conform Analytics Dashboard for Food Delivery", className="mb-4"),
        dbc.Row(
            dbc.Col(
                dcc.Graph(
                    id='density-heatmap',
                    figure=go.Figure(
                        data=go.Densitymapbox(
                            lon=longitudes,
                            lat=latitudes,
                            z= np.ones_like(latitudes),
                            radius=30,
                        ),
                        layout=go.Layout(
                            title='Areas with the highest number of Orders:',
                            mapbox=dict(
                                style='carto-positron',
                                center=dict(lat=12.9, lon=78),
                                zoom=10,
                            ),
                            height=600,
                        ),
                    ),
                ),
            ),
            className="mt-4",
        ),
        dbc.Row(
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
                                style='carto-positron',
                                center=dict(lat=12.9, lon=78),
                                zoom=10,
                            ),
                            height=600,
                        ),
                    ),
                ),
            ),
            className="mt-4",
        ),

    ],
    fluid=True,
)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)