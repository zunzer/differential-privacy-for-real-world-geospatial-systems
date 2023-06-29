from collections import Counter
from random import uniform

import numpy as np
import plotly.graph_objects as go
import scipy.ndimage as ndimage
from postgres import execute_query, get_centroid


def request_dp_centroid(n: int):
    # test3 = session.execute(text("SELECT ST_AsText(st_centroid(st_union(geom))) FROM public.online_delivery_data"))
    longitudes = []
    latitudes = []

    for i in range(n):
        cent = execute_query(
            "SELECT ST_AsText(st_centroid(st_union(geo_dp_centroid(geom,0.01)))) FROM public.online_delivery_data"
        )
        # print(cent)
        longitudes.append(cent[0])
        latitudes.append(cent[1])
    session.close()

    return longitudes, latitudes


def request_centroid(n: int):
    for i in range(n):
        cent = execute_query(
            "SELECT ST_AsText(st_centroid(st_union(geom))) FROM public.online_delivery_data"
        )
        # print(cent)
        longitudes.append(cent[0])
        latitudes.append(cent[1])
    session.close()

    return longitudes, latitudes


def plot_3d_centroids(n: int):
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
    fig.show()


def fetch_dp_centroids(n: int):
    longitudes, latitudes = request_dp_centroid(n)
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
    fig.show()


def plot_3d_distribution():
    n = 100

    plot_3d_centroids(n)

    x, y, z = fetch_dp_centroids(n)

    plot_3d_dp_centroids(x, y, z, 1)
    plot_3d_dp_centroids(x, y, z, 2)
    plot_3d_dp_centroids(x, y, z, 3)


plot_3d_distribution()
