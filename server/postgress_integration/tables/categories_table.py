from sqlalchemy import Table, Column, Integer, String, Text, MetaData, select
from pydantic import BaseModel
from postgress_integration.TrendingOrbit_table import TrendingOrbit_table

metadata = MetaData()


class CategoryRow(BaseModel):
    name: str
    summary: str | None = None


categories = Table(
    "categories",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
    Column("summary", Text),
)


class TO_categories_table(TrendingOrbit_table):
    def __init__(self):
        super().__init__(table=categories, row=CategoryRow, metadata=metadata)

    def Create_category(self, name: str, summary: str):
        return self.row(name=name, summary=summary)

    async def Insert_category(self, new_row: CategoryRow):
        query = self.table.insert().values(name=new_row.name, summary=new_row.summary)
        last_record_id = await self.database.execute(query)
        return {"id": last_record_id}

    async def Get_id_by_name(self, name):
        query = select(self.table.c.id).where(self.table.c.name == name)
        result = await self.database.fetch_one(query)
        if result:
            return result["id"]
        return None


categories_table = TO_categories_table()
