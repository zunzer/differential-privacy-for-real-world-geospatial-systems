import ast
from configparser import ConfigParser
from typing import Union

# Run pip install sqlalchemy
from sqlalchemy import CursorResult, Row, create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sshtunnel import SSHTunnelForwarder  # Run pip install sshtunnel

# if True, no ssh-tunnel will be established
IS_IN_PROD = False


def aggregator(epsilon: float = 2.0, n: int = 1):
    query_result = execute_query(
        f"SELECT private_data({epsilon}, {n})",
    )
    private_data_result = clean_private_data(query_result, "private_data")
    lat, long, incomes = (
        [x[0] for x in private_data_result],
        [x[1] for x in private_data_result],
        [x[2] for x in private_data_result],
    )

    rect = execute_query(f"SELECT private_bounding_rect({epsilon}, {n})")
    clean_rect = clean_bounding_rect_result(rect, "private_bounding_rect")

    centroid = execute_query(f"SELECT private_centroid({epsilon}, {n})")
    clean_centroid = clean_centroid_result(centroid, "private_centroid")

    return (
        lat,
        long,
        incomes,
        clean_centroid,
        clean_rect,
    )


def clean_bounding_rect_result(row: Row, key: str):
    clean_string = row._mapping[key].replace('"', "")
    dict_value = ast.literal_eval(clean_string)
    return dict_value


def clean_centroid_result(row: Row, key: str):
    clean_string = row._mapping[key].replace('"', "").replace(">", "").replace("<", "")
    tuple_value = ast.literal_eval(clean_string)
    if len(tuple_value) <= 1:
        coordinates = tuple_value[0]
        latitudes, longitudes = coordinates[0], coordinates[1]
        return latitudes, longitudes
    else:
        return tuple_value


def clean_private_data(row: Row, key: str):
    clean_string = row._mapping[key].replace('"', "")
    dict_value = ast.literal_eval(clean_string)
    return dict_value


def execute_query(
    query: str, unfetched_output: bool = False
) -> Union[CursorResult, Row]:
    config = ConfigParser()
    config.read("settings.ini")
    db_settings = config["postgres"]
    ssh_settings = config["ssh"]

    if IS_IN_PROD:
        # connect to PostgreSQL
        engine = create_engine(
            f"postgresql://{db_settings['user']}:{db_settings['password']}@{db_settings['host_ip']}:5432/{db_settings['db_name']}",
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
    else:
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
                if unfetched_output:
                    # print(type(sql_query))
                    connection.commit()
                    connection.close()
                    return sql_query
                else:
                    query_result = sql_query.fetchone()
                    connection.close()
                    return query_result
