-- noinspection SqlDialectInspectionForFile
-- noinspection SqlNoDataSourceInspectionForFile

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


-- function to activate Python env
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


-- Functions for midterm presentation
select * FROM public."Delivery"

SELECT geom as location, age , gender, marital_status , monthly_income, centroid
FROM public."Delivery", (SELECT st_centroid(st_union(geom)) AS centroid FROM public."Delivery") as table4, (SELECT st_centroid(st_union(geo_dp(geom,0.01))) AS dp_centroid FROM public."Delivery")as table3

SELECT  geom as location, geo_dp(geom,0.01) as geo_dp_location, age , gender, marital_status , monthly_income, dp_centroid, centroid
FROM public."Delivery", (SELECT st_centroid(st_union(geom)) AS centroid FROM public."Delivery") as table4, (SELECT st_centroid(st_union(geo_dp(geom,0.01))) AS dp_centroid FROM public."Delivery")as table3

SELECT geom, point
FROM public."Delivery", (SELECT ST_ClusterWithin(geom) AS point FROM public."Delivery") as table4, (SELECT st_centroid(st_union(geo_dp(geom,0.01))) AS dp_point FROM public."Delivery")as table3



-- Tests for differential private functions
select geo_dp(geom,0.01) from online_delivery_data

select geo_dp_centroid(geom, 20), geom from online_delivery_data

SELECT (st_centroid(st_union(geo_dp_centroid(geom,0.01)))) FROM public.online_delivery_data

-- create centroid differential private function
CREATE or REPLACE FUNCTION geo_dp_centroid(geom geometry, epsilon float)
  RETURNS geometry
AS $$
 from plpygis import Geometry
 from plpygis import Point
 point = Geometry(geom)
 plpy.info(point)
 if point.type != "Point":
      return None
 gj = point.geojson
 lon = gj["coordinates"][0]
 lat = gj["coordinates"][1]
 plpy.info("Starting test run")
 from GeoPrivacy.mechanism import random_laplace_noise
 noise = random_laplace_noise(epsilon)
 plpy.info(noise[0], noise[1], lon, lat)
 new_lon = lon + noise[0]
 new_lat = lat + noise[1]
 plpy.info(new_lon, new_lat)
 return Geometry(Point((new_lon, new_lat)))
$$ LANGUAGE plpython3u;



-- create bounding rectangle dp function
CREATE or REPLACE FUNCTION geo_dp_rect(geom geometry, epsilon float)
  RETURNS TEXT
AS $$
 from plpygis import Geometry
 plpy.info("Starting test run")
 from GeoPrivacy.mechanism import random_laplace_noise
 noise = random_laplace_noise(epsilon)
 new_location = geom + noise
 return new_location
 $$ LANGUAGE plpython3u;
 CREATE extension plpython3u

 -- create heatmap dp function
CREATE or REPLACE FUNCTION geo_dp_heat(geom geometry, epsilon float)
  RETURNS TEXT
AS $$
 from plpygis import Geometry
 plpy.info("Starting test run")
 from GeoPrivacy.mechanism import random_laplace_noise
 noise = random_laplace_noise(epsilon)
 new_location = geom + noise
 return new_location
 $$ LANGUAGE plpython3u;
 CREATE extension plpython3u

drop function geo_dp_centroid(geometry,double precision);
drop function geo_dp_rect(geometry,double precision)
drop function geo_dp_heat(geometry,double precision)
