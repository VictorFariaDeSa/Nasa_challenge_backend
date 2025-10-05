from sqlalchemy import Table, Column, Integer, MetaData, ForeignKey
from pydantic import BaseModel
from postgress_integration.TrendingOrbit_table import TrendingOrbit_table
metadata = MetaData()
from sqlalchemy.dialects.postgresql import insert

class TopicArticleRow(BaseModel):
    article_id: int 
    topic_id: int

topic_article = Table(
    "topic_article",
    metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("topic_id", Integer, ForeignKey("topics.id"), primary_key=True),
)

class TO_topic_article_table(TrendingOrbit_table):
    def __init__(self):
        super().__init__(table=topic_article,row=TopicArticleRow,metadata=metadata)

    def Create_topic_article_row(self,topic_id: int, article_id: int):
        return self.row(article_id=article_id,topic_id=topic_id)

    async def Insert_topic_article(self,new_row: TopicArticleRow):
        query = insert(self.table).values(
            article_id=new_row.article_id, 
            topic_id=new_row.topic_id
            ).on_conflict_do_nothing(index_elements=['article_id', 'topic_id'])
        last_record_id = await self.database.execute(query)
        return {"id": last_record_id}



topic_article_table = TO_topic_article_table()