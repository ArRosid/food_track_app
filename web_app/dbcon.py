from flask import g
import os
import psycopg2
from psycopg2.extras import DictCursor

# def connect_db():
#     sql = sqlite3.connect('./food_trakcer.db')
#     sql.row_factory = sqlite3.Row
#     return sql

# def get_db():
#     if not hasattr(g, 'sqlite_db'):
#         g.sqlite_db = connect_db()
#     return g.sqlite_db

def connect_db():
    conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=DictCursor)
    conn.autocommit = True
    sql = conn.cursor()
    return conn, sql

def get_db():
    db = connect_db()

    if not hasattr(g, 'postgres_db_conn'):
        g.postgres_db_conn = db[0]
    if not hasattr(g, 'postgres_db_cur'):
        g.postgres_db_cur = db[1]

    return g.postgres_db_cur