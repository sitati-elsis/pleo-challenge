from sqlalchemy import create_engine
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker
from logger import logger

db = SQLAlchemy()


class Events(db.Model):
    __tablename__ = 'events'

    event_id = db.Column(UUID, unique=True, primary_key=True)
    payload = db.Column(db.JSON)
    meta_data = db.Column("metadata", db.JSON)
    event_at = db.Column(db.DATETIME)
    type = db.Column(db.String(300))


def get_db_connection():
    PG_USER = os.getenv("PG_USER", "dwh")
    PG_PASSWORD = os.getenv("PG_PASSWORD", "dwh")
    PG_HOST = os.getenv("PG_HOST", "dwh")
    PG_DB = os.getenv("PG_DB", "dwh")
    return create_engine(f'postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}/{PG_DB}')


def create_events_table():
    engine = get_db_connection()
    engine.execute("""
    CREATE TABLE IF NOT EXISTS events
    (
        event_id uuid NOT NULL,
        payload jsonb NOT NULL,
        type text NOT NULL,
        metadata jsonb NOT NULL,
        event_at timestamptz NOT NULL DEFAULT now(),
        UNIQUE (event_id)
    );
    """)


def bulk_insert(records):
    """
    Perform a bulk insert of the data
    """
    try:
        session = sessionmaker(bind=get_db_connection())()
        session.bulk_insert_mappings(
            Events, records
        )
        session.commit()
    except Exception as e:
        logger.error(e)
        session.rollback()
        logger.error('Rolled back the session because of the above Exception')
    return