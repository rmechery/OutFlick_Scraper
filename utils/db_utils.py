import sqlalchemy as sa
from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy import Engine, create_engine, URL
from sqlalchemy.orm import sessionmaker, Session


def get_local_engine():
    """Gets SQLAlchemy engine to connect to local database."""
    parent_dir = Path(__file__).resolve().parent.parent
    file_path = parent_dir / 'src' / 'local_settings' / 'local_settings.sqlite3'
    db_url = "sqlite:///" + str(file_path)
    engine: Engine = create_engine(db_url)
    return engine


SessionLocal: sessionmaker[Session] = sessionmaker(bind=get_local_engine())


def get_remote_engine():
    """Gets SQLAlchemy engine to connect to remote database."""
    env_file = Path(__file__).parent.parent / '.env'
    config = dotenv_values(env_file)

    url_object = URL.create(
        "postgresql+psycopg2",
        username=config['DB_USER'],
        password=config['DB_PASS'],
        host=config['DB_HOST'],
        database=config['DB'],
        port=config['DB_PORT'],
    )
    #url = f"postgresql+psycopg2://{config['DB_USER']}:{config['DB_PASS']}@{config['DB_HOST']}:{config['DB_PORT']}/{config['DB']}"
    #print(url)
    return create_engine(url_object, echo=False)


SessionRemote: sessionmaker[Session] = sessionmaker(bind=get_remote_engine())
