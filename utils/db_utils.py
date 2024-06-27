import sqlalchemy as sa
from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy.orm import sessionmaker


def get_local_engine():
    parent_dir = Path(__file__).resolve().parent.parent
    file_path = parent_dir / 'src' / 'local_settings' / 'local_settings.sqlite3'
    return sa.create_engine("sqlite:///" + str(file_path))


SessionLocal = sessionmaker(bind=get_local_engine())


def get_remote_engine():
    env_file = Path(__file__).parent.parent / '.env'
    config = dotenv_values(env_file)
    url = f"postgresql+psycopg2://{config['DB_USER']}:{config['DB_PASS']}@{config['DB_HOST']}:{config['DB_PORT']}/{config['DB']}"
    #print(url)
    return sa.create_engine(url, echo=False)


SessionRemote = sessionmaker(bind=get_remote_engine())
