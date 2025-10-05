from databases import Database
import sqlalchemy as sa
import os

DATABASE_USER = os.environ.get("DATABASE_USER")
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
DATABASE_HOST = os.environ.get("DATABASE_HOST")
DATABASE_PORT = os.environ.get("DATABASE_PORT")
DATABASE_NAME = os.environ.get("DATABASE_NAME")


def create_postgres_engine(user, password, host, port, db_name, async_mode=True):
    driver = "asyncpg" if async_mode else "psycopg2"
    database_url = f"postgresql+{driver}://{user}:{password}@{host}:{port}/{db_name}"

    database = Database(database_url) if async_mode else None
    engine = sa.create_engine(database_url, echo=True, future=True)
    metadata = sa.MetaData()

    return engine, metadata, database


engine, metadata, database = create_postgres_engine(
    DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT, DATABASE_NAME
)
