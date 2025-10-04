from sqlalchemy import Table, Column, Integer, String, Text, MetaData
from pydantic import BaseModel
from postgress_integration.TrendingOrbit_table import TrendingOrbit_table
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

class TO_topics_table(TrendingOrbit_table):
    def __init__(self):
        super().__init__(table=topics,row=TopicRow,metadata=metadata)

    def Create_topic(self,name: str, summary:str):
        return self.row(name=name,summary=summary)

    async def Insert_topic(self,new_row: TopicRow):
        query = self.table.insert().values(name=new_row.name, summary=new_row.summary)
        last_record_id = await self.database.execute(query)
        return {"id": last_record_id}



topics_table = TO_topics_table()