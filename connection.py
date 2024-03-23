import psycopg2

hostname = 'localhost'
database_name = 'tf'
username = 'root'
pwd = ''  # Enter your password here.
port_id = 5432

conn = psycopg2.connect(
    host = hostname,
    dbname = database_name,
    user = username,
    password = pwd,
    port = port_id
)

cur = conn.cursor()

script = '''CREATE TABLE IF NOT EXISTS status (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
)'''

cur.execute(script)

conn.commit()

conn.close()