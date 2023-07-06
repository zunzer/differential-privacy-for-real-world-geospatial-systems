-- Load python language in postgres db (only successful if python version and PATH is correct)
CREATE EXTENSION plpython3u;


-- Function for activating existing pip venv
CREATE OR REPLACE FUNCTION activate_python_venv(venv text)
  RETURNS void AS
$BODY$
    import os

    activate_this = os.path.join(venv, 'bin', 'activate_this.py')

    exec(open(activate_this).read(), dict(__file__=activate_this))
$BODY$
LANGUAGE plpython3u;


-- function to activate Phython
select activate_python_venv('/home/y_voigt/.venv');


-- check if path if correct ("/home/y_voigt/.venv/lib/python3.11/site-packages")
DO LANGUAGE plpython3u $$
    import sys
    plpy.notice('pl/python3 Path: {}'.format(sys.path[0]))                                                                                                                                                           $$;                                                                                                                                                                                                              NOTICE:  pl/python3 Path: /path/to/project/venv/lib/python3.10/site-packages
DO


-- function to add random uniform noise to geo data in plpgsql
create or replace function geo_dp(i geometry, epsilon float) RETURNS geometry AS $$
        BEGIN
                RETURN ST_MakePoint(ST_X(i)+(RANDOM()*((-epsilon)- epsilon) + epsilon), ST_Y(i)+(RANDOM()*((-epsilon)- epsilon) + epsilon));
        END;
$$ LANGUAGE plpgsql;


-- create Python function after python is loaded
CREATE or replace FUNCTION pymax (a integer, b integer)
  RETURNS integer
AS $$
  if a > b:
    return a
  return b
$$ LANGUAGE plpython3u;


-- Demonstration for midterm
select * from online_delivery_data

SELECT geom as location, age , gender, marital_status , monthly_income, centroid
FROM public."Delivery", (SELECT st_centroid(st_union(geom)) AS centroid FROM public."Delivery") as table4, (SELECT st_centroid(st_union(geo_dp(geom,0.01))) AS dp_centroid FROM public."Delivery")as table3

SELECT  geom as location, geo_dp(geom,0.01) as geo_dp_location, age , gender, marital_status , monthly_income, dp_centroid, centroid
FROM public."Delivery", (SELECT st_centroid(st_union(geom)) AS centroid FROM public."Delivery") as table4, (SELECT st_centroid(st_union(geo_dp(geom,0.01))) AS dp_centroid FROM public."Delivery")as table3

SELECT geom, point
FROM public."Delivery", (SELECT ST_ClusterWithin(geom) AS point FROM public."Delivery") as table4, (SELECT st_centroid(st_union(geo_dp(geom,0.01))) AS dp_point FROM public."Delivery")as table3


INSERT INTO online_delivery_data VALUES (388, 20, 'Female', 'Married', 'Student', 'No Income', 'Post Graduate', 3, 560001, 'Food delivery apps', 'Web browser', 'Breakfast', 'Lunch', 'Non Veg foods (Lunch / Dinner)', 'Bakery items (snacks)', 'Neutral',	'Neutral',	'Neutral',	'Neutral',	'Neutral', 'Neutral', 'Neutral', 'Neutral',	'Neutral', 'Neutral', 'Neutral', 'Neutral', 'Neutral', 'Neutral', 'Agree', 'Agree',	'Agree', 'Agree', 'Agree', 'Agree',	'Yes', 'Weekend (Sat & Sun)', '30 minutes', 'Agree', 'Neutral', 'Neutral', 'Neutral', 'Neutral', 'Yes', 'Moderately Important', 'Moderately Important', 'Moderately Important', 'Moderately Important', 'Moderately Important', 'Moderately Important', 'Moderately Important', 'Moderately Important', 'Yes', 'TEST ENTRY', ST_GeometryFromText('POINT (65.9901232886963 55.5953903123242)', 4326));--") #ST_GeometryFromText('POINT (" +str(long) + " " + str(lat) +")', 4326));")


-- add & delete new item
INSERT INTO online_delivery_data VALUES (388, 20, 'Female', 'Married', 'Student', 'No Income', 'Post Graduate', 3, 560001, 'Food delivery apps', 'Web browser', 'Breakfast', 'Lunch', 'Non Veg foods (Lunch / Dinner)', 'Bakery items (snacks)', 'Neutral',	'Neutral',	'Neutral',	'Neutral',	'Neutral', 'Neutral', 'Neutral', 'Neutral',	'Neutral', 'Neutral', 'Neutral', 'Neutral', 'Neutral', 'Neutral', 'Agree', 'Agree',	'Agree', 'Agree', 'Agree', 'Agree',	'Yes', 'Weekend (Sat & Sun)', '30 minutes', 'Agree', 'Neutral', 'Neutral', 'Neutral', 'Neutral', 'Yes', 'Moderately Important', 'Moderately Important', 'Moderately Important', 'Moderately Important', 'Moderately Important', 'Moderately Important', 'Moderately Important', 'Moderately Important', 'Yes', 'TEST ENTRY', ST_GeometryFromText('POINT (75.9901232886963 55.5953903123242)', 4326));

DELETE FROM public.online_delivery_data
WHERE "index"=388



CREATE or REPLACE FUNCTION real_centroid(n int, out longitudes text, out latitudes text)
AS $$
  from plpygis import Geometry, Point
  longitudes, latitudes = [], []
  for i in range(n):
	  geom = plpy.execute("select st_centroid(st_union(geom)) from public.online_delivery_data")
	  point = Geometry(geom[0]['st_centroid'])
	  if point.type != "Point":
		  return None
	  gj = point.geojson
	  lon = gj["coordinates"][0]
	  lat = gj["coordinates"][1]
	  longitudes.append(lon)
	  latitudes.append(lat)
  return longitudes, latitudes
$$ LANGUAGE plpython3u;



-- create centroid dp function
select private_centroid(10.0, 1)

CREATE or REPLACE FUNCTION private_centroid(epsilon float, n int, out longitudes text, out latitudes text)
as $$
  from plpygis import Geometry, Point
  from diffprivlib.mechanisms import Laplace
  mechanism = Laplace(epsilon=epsilon, sensitivity=1.0)
  longitudes, latitudes = [], []
  for i in range(n):
	  geom = plpy.execute("select st_centroid(st_union(geom)) from public.online_delivery_data")
	  point = Geometry(geom[0]['st_centroid'])
	  if point.type != "Point":
		  return None
	  gj = point.geojson
	  dp_lon = mechanism.randomise(gj["coordinates"][0])
	  dp_lat = mechanism.randomise(gj["coordinates"][1])
	  longitudes.append(dp_lon)
	  latitudes.append(dp_lat)
  return longitudes, latitudes
$$ LANGUAGE plpython3u;


drop function private_centroid(epsilon float)

-- create bounding rectangle dp function
select private_data(0.1)


CREATE or REPLACE FUNCTION private_data(epsilon float)
RETURNS text
AS $$
 from plpygis import Geometry
 from plpygis import Point
 from GeoPrivacy.mechanism import random_laplace_noise
 srows = plpy.execute("select geom, monthly_income from public.online_delivery_data")
 plpy.info(srows)
 res = []
 for i in srows:
  point = Geometry(i['geom'])
  if point.type != "Point":
   return None
  gj = point.geojson
  lon = gj["coordinates"][0]
  lat = gj["coordinates"][1]
  noise = random_laplace_noise(epsilon)
  new_lon = lon+ noise[0]
  new_lat = lat+ noise[1]
  res.append([new_lon, new_lat, i['monthly_income']])
 return res
$$ LANGUAGE plpython3u;


 -- create heatmap dp function
select * from private_bounding_rect(20)

SELECT private_bounding_rect(10)

CREATE or REPLACE FUNCTION private_bounding_rect(epsilon float)
  RETURNS text
AS $$
 from plpygis import Geometry
 from plpygis import Point
 from GeoPrivacy.mechanism import random_laplace_noise
 geom = plpy.execute("select st_astext(ST_Envelope(st_union(geom))) from public.online_delivery_data")
 plpy.info(geom)
 def get_rect(point):
    plpy.info(point)
    x = point.split(",")
    plpy.info(x)
    corner_list = []
    for i in x:
        corner_list.append(i.split(" "))
    corner_list[0][0] = corner_list[0][0].replace("POLYGON((", "")
    corner_list[4][1] = corner_list[4][1].replace("))", "")
    return corner_list
 corner = get_rect(geom[0]['st_astext'])
 plpy.info(corner)
 geo_mapping = {}
 for sublist in corner:
  noise = random_laplace_noise(epsilon)
  geo_mapping[sublist[0]] = float(sublist[0]) + noise[0]
  geo_mapping[sublist[1]] = float(sublist[1]) + noise[1]
 res =[]
 for sublist in corner:
  res.append([geo_mapping[sublist[0]], geo_mapping[sublist[1]]])
 plpy.info(res)
 return res
$$ LANGUAGE plpython3u;

