-- function for DP bounding rectangle(s)

CREATE or REPLACE FUNCTION private_bounding_rect(epsilon float, n int)
	RETURNS text
AS $$
 import geopandas as gpd
 from plpygis import Geometry, Point
 from GeoPrivacy.mechanism import random_laplace_noise
 from shapely import Point as SPoint
 bounding_rects = []
 for i in range(n):
	 srows = plpy.execute("SELECT geom, monthly_income FROM public.online_delivery_data;")
	 coordinates = []
	 plpy.info(srows)
	 for i in srows:
	  point = Geometry(i['geom'])
	  if point.type != "Point":
	   pass
	  gj = point.geojson
	  noise = random_laplace_noise(epsilon)
	  lon = gj["coordinates"][0] + noise[0]
	  lat = gj["coordinates"][1] + noise[1]
	  coordinates.append(SPoint(lat, lon))
	 gdf = gpd.GeoDataFrame(geometry=coordinates)
	 bounding_rects.append(gdf.geometry.unary_union.envelope)
 bounding_rects_list = {idx: [coord for coord in polygon.exterior.coords[:]] for idx, polygon in enumerate(bounding_rects)}
 return bounding_rects_list
$$ LANGUAGE plpython3u;

-- function for DP bounding centroids(s)

CREATE or REPLACE FUNCTION private_centroid(epsilon float, n int)
	RETURNS text
AS $$
 import geopandas as gpd
 from plpygis import Geometry, Point
 from GeoPrivacy.mechanism import random_laplace_noise
 from shapely import Point as SPoint
 epsilon_fac = float(epsilon - (epsilon * 0.4))
 centroids = []
 for i in range(n):
	 srows = plpy.execute("SELECT geom, monthly_income FROM public.online_delivery_data;")
	 coordinates = []
	 plpy.info(srows)
	 for i in srows:
	  point = Geometry(i['geom'])
	  if point.type != "Point":
	   pass
	  gj = point.geojson
	  noise = random_laplace_noise(epsilon_fac)
	  lon = gj["coordinates"][0] + noise[0]
	  lat = gj["coordinates"][1] + noise[1]
	  coordinates.append(SPoint(lat, lon))
	 gdf = gpd.GeoDataFrame(geometry=coordinates)
	 centroids.append(gdf.geometry.unary_union.centroid)
 centroid_list = [(point.x, point.y) for point in centroids]
 return centroid_list
$$ LANGUAGE plpython3u;

-- function for DP data for heatmap and clustering

CREATE or REPLACE FUNCTION private_data(epsilon float, n int)
RETURNS text
AS $$
 from plpygis import Geometry, Point
 from GeoPrivacy.mechanism import random_laplace_noise
 for i in range(n):
	 srows = plpy.execute("SELECT geom, monthly_income FROM public.online_delivery_data;")
	 plpy.info(srows)
	 res = []
	 for i in srows:
	  point = Geometry(i['geom'])
	  if point.type != "Point":
	   return None
	  gj = point.geojson
	  noise = random_laplace_noise(epsilon)
	  lon = gj["coordinates"][0] + noise[0]
	  lat = gj["coordinates"][1] + noise[1]
	  res.append([lon, lat, i['monthly_income']])
 return res
$$ LANGUAGE plpython3u;