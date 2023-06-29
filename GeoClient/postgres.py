from sshtunnel import SSHTunnelForwarder  # Run pip install sshtunnel
from sqlalchemy.orm import sessionmaker  # Run pip install sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from sqlalchemy import inspect

def connector():
    with SSHTunnelForwarder(
            ('35.234.102.238', 22),  # Remote server IP and SSH port
            ssh_username="serap",
            ssh_password="password",
            ssh_pkey="peng",
            ssh_private_key_password="peng",
            remote_bind_address=(
                    'localhost', 5432)) as server:  # PostgreSQL server IP and sever port on remote machine

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
        return lat, long, incomes, centroid, rect #centroid_lat, centroid_long, bounding_rect


def get_rect(point):
    x = point[0].split(",")
    corner_list = []
    for i in x:
        corner_list.append(i.split(" "))
    print(corner_list)

    corner_list[0][0] = corner_list[0][0].replace("POLYGON((", "")
    corner_list[3][1] = corner_list[3][1].replace(")))", "")
    return(corner_list)


def get_centroid(point):
    x = point[0].split(" ")
    return [float(x[1].replace(")", "")), float(x[0].replace("POINT(", ""))]
