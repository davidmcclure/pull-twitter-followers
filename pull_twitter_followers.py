

import os
import tweepy

from datetime import datetime as dt
from tqdm import tqdm
from redis import Redis
from rq import Queue

from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base


# TODO: Rotate keys, etc.
TWITTER_TOKEN = os.environ.get('TWITTER_TOKEN')
TWITTER_SECRET = os.environ.get('TWITTER_SECRET')


queue = Queue(connection=Redis())


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
    job_timestamp = Column(Integer, nullable=False)
    follower_id = Column(Integer, nullable=False)

    @classmethod
    def insert_ids(cls, screen_name, ids, start):
        """Bulk-insert ids.
        """
        rows = [
            dict(
                screen_name=screen_name,
                job_timestamp=start,
                follower_id=id,
            )
            for id in ids
        ]

        session.bulk_insert_mappings(cls, rows)


def pull_followers(screen_name):
    """Pull all follwers for an account.
    """
    start = utc_timestamp()

    auth = tweepy.AppAuthHandler(TWITTER_TOKEN, TWITTER_SECRET)

    api = tweepy.API(
        auth,
        wait_on_rate_limit=True,
        wait_on_rate_limit_notify=True,
        retry_count=10,
        retry_delay=10,
    )

    cursor = tweepy.Cursor(api.followers_ids, screen_name=screen_name)

    for ids in tqdm(cursor.pages()):
        Follower.insert_ids(screen_name, ids, start)

    session.commit()
