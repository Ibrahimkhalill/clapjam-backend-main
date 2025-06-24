from django_setup import *
from cjcreds import creds
import psycopg2
from psycopg2 import sql
import sys


DB_NAME = creds.POSTGRES_DB_NAME
DB_USER = creds.POSTGRES_DB_USER
DB_PASSWORD = creds.POSTGRES_DB_PASSWORD
DB_HOST = creds.POSTGRES_DB_HOST
DB_PORT = creds.POSTGRES_DB_PORT


if input('Are you sure kafi bhai? (yes/no): ').lower() == 'yes':
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True

        with conn.cursor() as cur:
            cur.execute(sql.SQL("""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = %s AND pid <> pg_backend_pid();
            """), [DB_NAME])

            cur.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(
                sql.Identifier(DB_NAME)
            ))
            print(f"Dropped database '{DB_NAME}' (if it existed).")

            cur.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(DB_NAME)
            ))
            print(f"Created fresh database '{DB_NAME}'.")

        if conn:
            conn.close()

    except psycopg2.Error as e:
        print(f"Error: {e}")
        sys.exit(1)
