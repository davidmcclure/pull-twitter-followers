

import os

from datetime import datetime as dt

from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base


def connect_db(db_path):
    """Get database connection.

    Args:
        db_name (str)

    Returns: engine, session
    """
    url = URL(drivername='sqlite', database=db_path)
    engine = create_engine(url)

    factory = sessionmaker(bind=engine)
    session = scoped_session(factory)

    return engine, session


DB_PATH = os.path.join(os.path.dirname(__file__), 'followers.db')
engine, session = connect_db(DB_PATH)


class BaseModel:

    @classmethod
    def reset(cls):
        """Drop and recreate table.
        """
        cls.metadata.drop_all(engine, tables=[cls.__table__])
        cls.metadata.create_all(engine, tables=[cls.__table__])


BaseModel = declarative_base(cls=BaseModel)
BaseModel.query = session.query_property()


def utc_timestamp():
    return round(dt.utcnow().timestamp())


class Follower(BaseModel):

    __tablename__ = 'follower'
    id = Column(Integer, primary_key=True)
    screen_name = Column(String, nullable=False)
    follower_id = Column(String, nullable=False)
    timestamp = Column(Integer, nullable=False)
