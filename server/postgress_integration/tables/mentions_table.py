from sqlalchemy import Table, Column, Integer, String, Text, MetaData, DATE
from pydantic import BaseModel
from postgress_integration.TrendingOrbit_table import TrendingOrbit_table
from datetime import date
metadata = MetaData()

class MentionRow(BaseModel):
    topic_id: int
    mention_date: date
    mention_counter: int | None = None

mentions = Table(
    "mentions",
    metadata,
    Column("topic_id", Integer, primary_key=True),
    Column("mention_date", DATE, nullable=False),
    Column("mention_counter", Integer)
)



class TO_mentions_table(TrendingOrbit_table):
    def __init__(self):
        super().__init__(table=mentions,row=MentionRow,metadata=metadata)

    def Create_mention(self,topic_id:int, mention_date: date, mention_counter:int):
        return self.row(
            topic_id = topic_id,
            mention_date = mention_date,
            mention_counter = mention_counter
            )

    async def Insert_mention(self,new_row: MentionRow):
        query = self.table.insert().values(
            topic_id=new_row.topic_id,
            mention_date=new_row.mention_date, 
            mention_counter=new_row.mention_counter
            )
        last_record_id = await self.database.execute(query)
        return {"id": last_record_id}



mentions_table = TO_mentions_table()