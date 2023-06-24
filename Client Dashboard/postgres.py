from sshtunnel import SSHTunnelForwarder  # Run pip install sshtunnel
from sqlalchemy.orm import sessionmaker  # Run pip install sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from sqlalchemy import inspect

def connector():
    with SSHTunnelForwarder(
        ('35.246.227.120', 22),  # Remote server IP and SSH port
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

        print('Database session created')

        # test data retrieval
        test = session.execute(text("SELECT ST_AsText(geom), monthly_income, ST_Envelope(geom) FROM public.online_delivery_data"))
        print(test)
        lat = []
        long = []
        incomes = []
        for i in test:
            row = test.fetchone()
            print(row)
            print(row[0])
            x = row[0].split(" ")
            lat.append(x[0].replace("POINT(", ""))
            long.append(x[1].replace(")", ""))
            incomes.append(row[1])
        print(lat, long)
        session.close()
        return lat, long, incomes

connector()