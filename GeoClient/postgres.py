import ast
from configparser import ConfigParser
from typing import Union

# Run pip install sqlalchemy
from sqlalchemy import CursorResult, Row, create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sshtunnel import SSHTunnelForwarder  # Run pip install sshtunnel


def aggregator(epsilon: int = 1):
    lat, long, incomes = [], [], []
    query_result = execute_query(
        f"SELECT private_data({epsilon})",
        # "SELECT ST_AsText(geom), monthly_income FROM public.online_delivery_data",
    )
    x = query_result[0].split("], [")
    for i in x:
        res = i.split(",")
        lat.append(res[0].replace("[", ""))
        long.append(res[1])
        incomes.append(res[2].replace("]", "").replace("'", ""))
    rect = execute_query(
        f"SELECT private_bounding_rect({epsilon})"
        # "SELECT ST_AsText(ST_Envelope(st_union(geom))) FROM public.online_delivery_data"
    )
    print(1, rect)

    centroid = execute_query(f"SELECT private_centroid({epsilon})")

    return (
        lat,
        long,
        incomes,
        get_centroid(centroid),
        get_rect(rect),
    )  # centroid_lat, centroid_long, bounding_rect


def get_centroid(point):
    return [float(i) for i in point[0].replace("[", "").replace("]", "").split(", ")]


def get_rect(rect):
    return [
        i.replace("[", "").replace("]", "").split(",") for i in rect[0].split("], [")
    ]


def clean_centroid_result(row: Row, key: str):
    clean_string = row._mapping[key].replace('"', "")
    # print(clean_string)
    tuple_value = ast.literal_eval(clean_string)
    # print(tuple_value)
    longitudes, latitudes = tuple_value[0], tuple_value[1]
    return longitudes, latitudes


def execute_query(
    query: str, unfetched_output: bool = False
) -> Union[CursorResult, Row]:
    config = ConfigParser()
    config.read("settings.ini")
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
        with engine.connect() as connection:
            # print(insp.get_table_names())
            env_activation = connection.execute(
                text("SELECT activate_python_venv('/home/y_voigt/.venv');")
            )
            # print(query)
            sql_query = connection.execute(text(query))
            connection.close()
            if unfetched_output:
                # print(type(sql_query))
                return sql_query
            else:
                query_result = sql_query.fetchone()
                return query_result
