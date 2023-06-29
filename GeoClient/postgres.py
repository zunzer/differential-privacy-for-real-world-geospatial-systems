from configparser import ConfigParser
from typing import Union

from sqlalchemy import Row  # Run pip install sqlalchemy
from sqlalchemy import CursorResult, create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sshtunnel import SSHTunnelForwarder  # Run pip install sshtunnel


<<<<<<< Updated upstream
def aggregator():
    lat = []
    long = []
    incomes = []
    query_result = execute_query(
        "SELECT ST_AsText(geom), monthly_income FROM public.online_delivery_data",
        unfetched_output=True,
    )
    for _ in query_result:
        row = query_result.fetchone()
        if row is None:
            break
        # print(row)
        # print(row[0])
        x = row[0].split(" ")
        lat.append(x[0].replace("POINT(", ""))
        long.append(x[1].replace(")", ""))
        incomes.append(row[1])
    # print(lat, long)
    rect = get_rect(
        execute_query(
            "SELECT ST_AsText(ST_Envelope(st_union(geom))) FROM public.online_delivery_data"
        )
    )
    # print("Rect", rect)
    centroid = get_centroid(
        execute_query(
            "SELECT ST_AsText(st_centroid(st_union(geom))) FROM public.online_delivery_data"
        )
    )
    # print("Centroid", centroid)
    return (
        lat,
        long,
        incomes,
        centroid,
        rect,
    )  # centroid_lat, centroid_long, bounding_rect
=======
        server.start()  # start ssh sever
        print('Server connected via SSH')

        # connect to PostgreSQL
        local_port = str(server.local_bind_port)
        engine = create_engine('postgresql://postgres:password@127.0.0.1:' + local_port + '/peng')
        insp = inspect(engine)
        print(insp.get_table_names())
        Session = sessionmaker(bind=engine)
        session = Session()
        test = session.execute(text("select activate_python_venv('/home/y_voigt/.venv');"))

        test = session.execute(text("SELECT ST_AsText(geom), monthly_income FROM public.online_delivery_data"))
        print(test)
        lat = []
        long = []
        incomes = []
        for _ in test:
            row = test.fetchone()
            if row is None:
                break
            print(row)
            print(row[0])
            x = row[0].split(" ")
            lat.append(x[0].replace("POINT(", ""))
            long.append(x[1].replace(")", ""))
            incomes.append(row[1])
        print(lat, long)
        test2 = session.execute(text("SELECT ST_AsText(ST_Envelope(st_union(geom))) FROM public.online_delivery_data"))
        rect = get_rect(test2.fetchone())
        print("Rect", rect)
        test3 = session.execute(text("SELECT ST_AsText(st_centroid(st_union(geom))) FROM public.online_delivery_data"))
        centroid = get_centroid(test3.fetchone())
        print("Centroid", centroid)
        session.close()

        return lat, long, incomes, centroid, rect #centroid_lat, centroid_long, bounding_rect
>>>>>>> Stashed changes


def get_rect(point):
    x = point[0].split(",")
    corner_list = []
    for i in x:
        corner_list.append(i.split(" "))
    print(corner_list)

    corner_list[0][0] = corner_list[0][0].replace("POLYGON((", "")
    corner_list[3][1] = corner_list[3][1].replace(")))", "")
    return corner_list


def get_centroid(point):
    x = point[0].split(" ")
    return [float(x[1].replace(")", "")), float(x[0].replace("POINT(", ""))]


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
        # print(insp.get_table_names())
        Session = sessionmaker(bind=engine)
        session = Session()
        print("Database session created")
        env_activation = session.execute(
            text("select activate_python_venv('/home/y_voigt/.venv');")
        )
        sql_query = session.execute(text(query))
        session.close()
        print("Session closed")
        if unfetched_output:
            # print(type(sql_query))
            return sql_query
        else:
            query_result = sql_query.fetchone()
            # print(type(query_result))
            return query_result
