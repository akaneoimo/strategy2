from datetime import datetime
from typing import List, Optional
import sqlalchemy
from pydantic import BaseModel


class Topic(BaseModel):
    id: int
    region: str
    field: str
    issue: str
    topic: str
    main_keywords: str
    submain_keywords: str
    secondary_keywords: str
    keywords: Optional[list]
    keysentences: Optional[list]


class Strategy(BaseModel):
    id: int
    name: str
    define: str


class News(BaseModel):
    topic_id: int
    publish_time: datetime
    title: str
    url: str
    site: str
    source: str
    content: str
    strategy_id: list
    predict_strategy_id: list
    

class Status(BaseModel):
    name: str
    value: int
    request_submit_time: datetime
    update_time: datetime


metadata = sqlalchemy.MetaData()
topics = sqlalchemy.Table(
    'topic',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('region', sqlalchemy.String(128)),
    sqlalchemy.Column('field', sqlalchemy.String(128)),
    sqlalchemy.Column('issue', sqlalchemy.String(128)),
    sqlalchemy.Column('topic', sqlalchemy.String(128)),
    sqlalchemy.Column('main_keywords', sqlalchemy.Text),
    sqlalchemy.Column('submain_keywords', sqlalchemy.Text),
    sqlalchemy.Column('secondary_keywords', sqlalchemy.Text),
    sqlalchemy.Column('keywords', sqlalchemy.JSON),
    sqlalchemy.Column('keysentences', sqlalchemy.JSON),
)

strategies = sqlalchemy.Table(
    'strategy',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('name', sqlalchemy.String(128)),
    sqlalchemy.Column('define', sqlalchemy.Text),
)

news = sqlalchemy.Table(
    'news',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('topic_id', sqlalchemy.Integer),
    sqlalchemy.Column('publish_time', sqlalchemy.DATETIME),
    sqlalchemy.Column('title', sqlalchemy.String(255)),
    sqlalchemy.Column('url', sqlalchemy.String(255)),
    sqlalchemy.Column('site', sqlalchemy.String(255)),
    sqlalchemy.Column('source', sqlalchemy.String(255)),
    sqlalchemy.Column('content', sqlalchemy.Text),
    sqlalchemy.Column('strategy_id', sqlalchemy.JSON),
    sqlalchemy.Column('predict_strategy_id', sqlalchemy.JSON),
)

status = sqlalchemy.Table(
    'status',
    metadata,
    sqlalchemy.Column('name', sqlalchemy.String(255)),
    sqlalchemy.Column('value', sqlalchemy.Integer),
    sqlalchemy.Column('request_submit_time', sqlalchemy.DATETIME),
    sqlalchemy.Column('update_time', sqlalchemy.DATETIME),
)