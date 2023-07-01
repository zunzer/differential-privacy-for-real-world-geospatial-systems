from configparser import ConfigParser
from typing import Union

from sqlalchemy import (
    CursorResult,
    Row,  # Run pip install sqlalchemy
    create_engine,
    inspect,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sshtunnel import SSHTunnelForwarder  # Run pip install sshtunnel


def aggregator(epsilon:int = 1):
    lat = []
    long = []
    incomes = []
    query_result = execute_query(
        f'SELECT  private_data({epsilon})',
        #"SELECT ST_AsText(geom), monthly_income FROM public.online_delivery_data",
    )
    x = query_result[0].split("], [")
    for i in x:
        res = i.split(",")
        lat.append(res[0].replace("[", ""))
        long.append(res[1])
        incomes.append(res[2].replace("]", "").replace("'", ""))
    rect = execute_query(
            f'SELECT private_bounding_rect({epsilon})'

            #"SELECT ST_AsText(ST_Envelope(st_union(geom))) FROM public.online_delivery_data"
        )

    centroid = execute_query(
            f'SELECT private_centroid({epsilon})'
        )

    return (
        lat,
        long,
        incomes,
        centroid[0].replace("[","").replace("]","").split(", "),
        [i.replace("[","").replace("]","").split(",") for i in rect[0].split("], [")]
    )  # centroid_lat, centroid_long, bounding_rect


def get_centroid(point):
    x = point[0].split(" ")
    return [float(x[1].replace(")", "")), float(x[0].replace("POINT(", ""))]


def get_rect(point):
    x = point[0].split(",")
    corner_list = []
    for i in x:
        corner_list.append(i.split(" "))
    print(corner_list)

    corner_list[0][0] = corner_list[0][0].replace("POLYGON((", "")
    corner_list[3][1] = corner_list[3][1].replace(")))", "")
    return corner_list


def execute_query(
    query: str, unfetched_output: bool = False
) -> Union[CursorResult, Row]:
    config = ConfigParser()
    config.read("../settings.ini")
    db_settings = config["postgres"]
    ssh_settings = config["ssh"]

    with SSHTunnelForwarder(
        (
            ssh_settings["host_ip"],
            int(ssh_settings["port"]),
        ),  # Remote server IP and SSH port
        ssh_username=ssh_settings["username"],
        ssh_pkey=ssh_settings["pkey_path"],
        ssh_private_key_password=ssh_settings["pkey_password"],
        remote_bind_address=(db_settings["host_ip"], int(db_settings["port"])),
    ) as server:  # PostgreSQL server IP and sever port on remote machine
        server.start()  # start ssh sever
        print("Server connected via SSH")

        # connect to PostgreSQL
        local_port = str(server.local_bind_port)
        engine = create_engine(
            f"postgresql://{db_settings['user']}:{db_settings['password']}@{db_settings['host_ip']}:{local_port}/{db_settings['db_name']}",
        )
        insp = inspect(engine)
        # print(insp.get_table_names())
        Session = sessionmaker(bind=engine)
        session = Session()
        env_activation = session.execute(
            text("select activate_python_venv('/home/y_voigt/.venv');")
        )
        sql_query = session.execute(text(query))
        session.close()
        if unfetched_output:
            # print(type(sql_query))
            return sql_query
        else:
            query_result = sql_query.fetchone()
            # print(type(query_result))
            return query_result
