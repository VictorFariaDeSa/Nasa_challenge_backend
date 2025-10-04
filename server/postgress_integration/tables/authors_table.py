from sqlalchemy import Table, Column, Integer, String, Text, MetaData
from pydantic import BaseModel
from postgress_integration.TrendingOrbit_table import TrendingOrbit_table
metadata = MetaData()

class AuthorRow(BaseModel):
    name: str
    summary: str | None = None

authors = Table(
    "authors",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
)

class TO_authors_table(TrendingOrbit_table):
    def __init__(self):
        super().__init__(table=authors,row=AuthorRow,metadata=metadata)

    def Create_author(self,name: str):
        return self.row(name=name)

    async def Insert_author(self,new_row: AuthorRow):
        query = self.table.insert().values(name=new_row.name)
        last_record_id = await self.database.execute(query)
        return {"id": last_record_id}



authors_table = TO_authors_table()