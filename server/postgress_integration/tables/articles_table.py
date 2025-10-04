from sqlalchemy import Table, Column, Integer, String, Text, MetaData, Date
from pydantic import BaseModel
from postgress_integration.TrendingOrbit_table import TrendingOrbit_table
from datetime import date
metadata = MetaData()


class ArticleRow(BaseModel):
    name: str
    summary: str | None = None
    link: str
    publish_date: date

articles = Table(
    "articles",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
    Column("summary", Text),
    Column("link", String(100)),
    Column("publish_date", Date),

)

class TO_articles_table(TrendingOrbit_table):
    def __init__(self):
        super().__init__(table=articles,row=ArticleRow,metadata=metadata)

    def Create_article(self,name: str, summary:str, link: str, publish_date: date):
        return self.row(name=name,summary=summary,link=link,publish_date=publish_date)

    async def Insert_article(self,new_row: ArticleRow):
        query = self.table.insert().values(name=new_row.name, summary=new_row.summary)
        last_record_id = await self.database.execute(query)
        return {"id": last_record_id}



articles_table = TO_articles_table()