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
CREATE FUNCTION pymax (a integer, b integer)
  RETURNS integer
AS $$
  if a > b:
    return a
  return b
$$ LANGUAGE plpython3u;


select  geom FROM public."Delivery"  

select count(geom) FROM public."Delivery"  

select * FROM public."Delivery"  


select st_centroid(st_union(geom)) FROM public."Delivery"; 


SELECT geom as location, age , gender, marital_status , monthly_income, centroid
FROM public."Delivery", (SELECT st_centroid(st_union(geom)) AS centroid FROM public."Delivery") as table4, (SELECT st_centroid(st_union(geo_dp(geom,0.01))) AS dp_centroid FROM public."Delivery")as table3

SELECT  geom as location, geo_dp(geom,0.01) as geo_dp_location, age , gender, marital_status , monthly_income, dp_centroid, centroid
FROM public."Delivery", (SELECT st_centroid(st_union(geom)) AS centroid FROM public."Delivery") as table4, (SELECT st_centroid(st_union(geo_dp(geom,0.01))) AS dp_centroid FROM public."Delivery")as table3



SELECT geom, point
FROM public."Delivery", (SELECT ST_ClusterWithin(geom) AS point FROM public."Delivery") as table4, (SELECT st_centroid(st_union(geo_dp(geom,0.01))) AS dp_point FROM public."Delivery")as table3
