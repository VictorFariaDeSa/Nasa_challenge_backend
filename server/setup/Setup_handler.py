import pandas as pd
from postgress_integration.tables import authors_table, articles_table, article_author_table, topics_table
from Setup_worker import Setup_worker
from Context_handler import Context_handler

class Setup_handler():
    def __init__(self,database,csv_file):
        self.database = database
        self.csv_file = csv_file
        self.publications_df = pd.read_csv(csv_file)
        self.worker = Setup_worker()
        self.ctx_handler = Context_handler()
        self.web_dict = {}
        self.db_len = None


    def Start_handler_values(self,n=None):
        url_list = self.publications_df.Link.to_list() if n is None else self.publications_df.Link.to_list()[:n]
        self.db_len = len(url_list)
        self.web_dict = self.worker.Get_all_data(url_list)
        
    async def Fill_database(self):
        await self.Fill_authors_table()
        await self.Fill_articles_table()
        await self.Fill_article_author_table()
        await self.Fill_topics_table()


    async def Fill_authors_table(self):
        await self.database.connect()
        for i in range(self.publications_df.shape[0]):
            authors = self.web_dict["authors"][i]
            for author in authors:
                author_row = authors_table.Create_author(author)
                await authors_table.Insert_author(author_row)
        await self.database.disconnect()





    async def Fill_articles_table(self):
        await self.database.connect()
        for i in range(self.publications_df.shape[0]):
            article_name = self.publications_df.Title[i]
            article_link = self.publications_df.Link[i]
            article_publish_date = self.web_dict["publish_date"][i]
            article_abstract = self.web_dict["abstracts"][i]
            article_row = articles_table.Create_article(
                name=article_name,
                summary=article_abstract,
                link=article_link,
                publish_date=article_publish_date
            )
            await articles_table.Insert_article(article_row)
        await self.database.disconnect()






    async def Fill_article_author_table(self):
        await self.database.connect()
    
        for i in range(self.db_len):
            article_link = self.publications_df.Link[i]
            authors = self.web_dict["authors"][i]
            
            article_id = await articles_table.Get_id_by_link(article_link)
            # print("---")
            # print(i)
            # print(article_link)
            # print(authors)
            # print(await articles_table.Get_name_by_id(article_id))
            for author_name in authors:
                author_id = await authors_table.Get_id_by_name(author_name)
                # print(f"authorID: {author_id} | articleID: {article_id}")
                try:
                    article_author_row = article_author_table.Create_article_author_row(
                        article_id=article_id,
                        author_id=author_id
                    )
                except:
                    print("erro ao adicionar a tabela article_author")
                await article_author_table.Insert_article_author(article_author_row)

        await self.database.disconnect()

    async def Fill_topics_table(self):
        url_list = self.publications_df.Link.to_list()
        abstracts_dict = self.web_dict["abstracts"]
        topic_freq, related_articles = self.ctx_handler.Get_trending_topics(abstracts_dict,15)
        topics_articles_dict = self.worker.Format_topics_articles_dict(related_articles,self.publications_df.Title.to_list())
        summaries = self.ctx_handler.Generate_summary_based_on_topics(topics_articles_dict)
        await self.database.connect()

        for topic in summaries.keys():
            topic_row = topics_table.Create_topic(
                name=topic,
                summary=summaries[topic]
            )
            await topics_table.Insert_topic(topic_row)

        await self.database.disconnect()


    