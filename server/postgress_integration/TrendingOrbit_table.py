from sqlalchemy import Table, Column, Integer, String, Text, MetaData
from postgress_integration.db_interface import database


class TrendingOrbit_table():
    def __init__(self,row,table,metadata):
        self.row = row
        self.table = table
        self.metadata = metadata
        self.database = database

    async def get_all(self):
        query = self.table.select()
        results = await self.database.fetch_all(query)
        return [dict(result) for result in results]

        
