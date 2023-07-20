import ast
from configparser import ConfigParser
from typing import Union

from sqlalchemy import CursorResult, Row, create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sshtunnel import SSHTunnelForwarder

# if True, no ssh-tunnel will be established
IS_IN_PROD = False


def aggregator(epsilon: float = 2.0, n: int = 1) -> object:
    """
    Main function for requesting data from all three DP-functions defined in the database return a list of coordinates
    for heatmap and clustering, as well as a dict for the private centroids and bounding rectangles respectively

    :param epsilon:
    :param n:
    :return:
    """
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
    """
    Serialize output from private bounding rectangle database function for later use
    :param row:
    :param key:
    :return:
    """
    clean_string = row._mapping[key].replace('"', "")
    dict_value = ast.literal_eval(clean_string)
    return dict_value


def clean_centroid_result(row: Row, key: str):
    """
    Serialize output from private centroid database function for later use
    :param row:
    :param key:
    :return:
    """
    clean_string = row._mapping[key].replace('"', "").replace(">", "").replace("<", "")
    tuple_value = ast.literal_eval(clean_string)
    if len(tuple_value) <= 1:
        coordinates = tuple_value[0]
        latitudes, longitudes = coordinates[0], coordinates[1]
        return latitudes, longitudes
    else:
        return tuple_value


def clean_private_data(row: Row, key: str):
    """
    Serialize output from private data function for later use
    :param row:
    :param key:
    :return:
    """
    clean_string = row._mapping[key].replace('"', "")
    dict_value = ast.literal_eval(clean_string)
    return dict_value


def execute_query(
        query: str, unfetched_output: bool = False
) -> Union[CursorResult, Row]:
    """
    Main function for establishing a database connection as well as handling and executing queries on the database when
    used from a machine different than the database machine, an ssh-tunnel can be used to establish a secure connection
    with the remote database server reads important credentials from settings.ini-file, for the ssh and database
    connection activates the virtual environment needed for the database function imports enables the return of either
    fetched output for SELECT-queries or unfetched output for a more verbose handling of SELECT-queries or SQL-commands
    that return nothing

    :param query:
    :param unfetched_output:
    :return:
    """
    config = ConfigParser()
    config.read("../settings.ini")
    db_settings = config["postgres"]
    ssh_settings = config["ssh"]

    if IS_IN_PROD:
        # connect to PostgreSQL
        engine = create_engine(
            f"postgresql://{db_settings['user']}:{db_settings['password']}@{db_settings['host_ip']}:5432/{db_settings['db_name']}",
        )
        _ = inspect(engine)
        with engine.connect() as connection:
            _ = connection.execute(
                text("SELECT activate_python_venv('/home/y_voigt/.venv');")
            )
            sql_query = connection.execute(text(query))
            connection.close()
            if unfetched_output:
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
            _ = inspect(engine)
            with engine.connect() as connection:
                _ = connection.execute(
                    text("SELECT activate_python_venv('/home/y_voigt/.venv');")
                )
                sql_query = connection.execute(text(query))
                if unfetched_output:
                    connection.commit()
                    connection.close()
                    return sql_query
                else:
                    query_result = sql_query.fetchone()
                    connection.close()
                    return query_result
