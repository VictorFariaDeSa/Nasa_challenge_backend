from sqlalchemy import Table, Column, Integer, String, Text, MetaData, select
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

    async def Get_id_by_name(self,name):
        query = select(self.table.c.id).where(self.table.c.name == name)
        result = await self.database.fetch_one(query)
        if result:
            return result["id"]
        return None

    async def Get_name_by_id(self,id):
        query = select(self.table.c.name).where(self.table.c.id == id)
        result = await self.database.fetch_one(query)
        if result:
            return result["name"]
        return None

authors_table = TO_authors_table()