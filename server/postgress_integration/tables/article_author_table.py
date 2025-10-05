from sqlalchemy import Table, Column, Integer, MetaData, ForeignKey
from pydantic import BaseModel
from postgress_integration.TrendingOrbit_table import TrendingOrbit_table
metadata = MetaData()
from sqlalchemy.dialects.postgresql import insert


class ArticleAuthorRow(BaseModel):
    article_id: int 
    author_id: int

article_author = Table(
    "article_author",
    metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("author_id", Integer, ForeignKey("authors.id"), primary_key=True),
)

class TO_article_author_table(TrendingOrbit_table):
    def __init__(self):
        super().__init__(table=article_author,row=ArticleAuthorRow,metadata=metadata)

    def Create_article_author_row(self,article_id: int, author_id: int):
        return self.row(article_id=article_id,author_id=author_id)

    async def Insert_article_author(self, new_row):
        query = insert(self.table).values(
            article_id=new_row.article_id,
            author_id=new_row.author_id
        ).on_conflict_do_nothing(index_elements=['article_id', 'author_id'])
        
        last_record_id = await self.database.execute(query)
        return {"id": last_record_id}



article_author_table = TO_article_author_table()