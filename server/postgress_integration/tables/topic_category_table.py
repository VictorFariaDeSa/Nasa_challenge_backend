from sqlalchemy import Table, Column, Integer, MetaData, ForeignKey
from pydantic import BaseModel
from postgress_integration.TrendingOrbit_table import TrendingOrbit_table
metadata = MetaData()


class TopicCategoryRow(BaseModel):
    category_id: int 
    topic_id: int

topic_category = Table(
    "topic_category",
    metadata,
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
    Column("topic_id", Integer, ForeignKey("topics.id"), primary_key=True),
)

class TO_topic_category_table(TrendingOrbit_table):
    def __init__(self):
        super().__init__(table=topic_category,row=TopicCategoryRow,metadata=metadata)

    def Create_topic_category_row(self,topic_id: int, category_id: int):
        return self.row(category_id=category_id,topic_id=topic_id)

    async def Insert_topic_article(self,new_row: TopicCategoryRow):
        query = self.table.insert().values(
            category_id=new_row.category_id, 
            topic_id=new_row.topic_id
            )
        last_record_id = await self.database.execute(query)
        return {"id": last_record_id}



topic_category_table = TO_topic_category_table()