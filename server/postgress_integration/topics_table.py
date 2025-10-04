from sqlalchemy import Table, Column, Integer, String, Text, MetaData
from postgress_integration.db_interface import database
from pydantic import BaseModel

metadata = MetaData()

class TopicRow(BaseModel):
    name: str
    summary: str | None = None

topics = Table(
    "topics",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
    Column("summary", Text)
)

async def Insert_topic(topic: TopicRow):
    query = topics.insert().values(name=topic.name, summary=topic.summary)
    last_record_id = await database.execute(query)
    return {"id": last_record_id}

async def get_all():
    query = topics.select()
    results = await database.fetch_all(query)
    return [dict(result) for result in results]
