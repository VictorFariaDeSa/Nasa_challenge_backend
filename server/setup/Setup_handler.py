import pandas as pd
from postgress_integration.tables import (
    authors_table,
    articles_table,
    article_author_table,
    topics_table,
    topic_article_table,
    categories_table,
    topic_category_table,
    mentions_table,
)
from setup.Setup_worker import Setup_worker
from setup.Context_handler import Context_handler


class Setup_handler:
    def __init__(self, database, csv_file):
        self.database = database
        self.csv_file = csv_file
        self.publications_df = pd.read_csv(csv_file)
        self.worker = Setup_worker()
        self.ctx_handler = Context_handler()
        self.web_dict = {}
        self.db_len = None
        self.topics_description = None
        self.categories_dict = None
        self.topic_summaries = None

    def Start_handler_values(self, n_topics=15, n=None):
        self.db_len = n if n is not None else self.publications_df.shape[0]
        start = 0
        df_section = self.publications_df[start : start + self.db_len]
        (
            self.web_dict,
            self.publications_df,
        ) = self.worker.Get_all_data(df_section)
        self.Configure_trending_topics(n_topics)

    def Configure_trending_topics(self, n_topics):
        abstracts_dict = self.web_dict["abstracts"]
        publish_dict = self.web_dict["publish_date"]

        self.topic_freq, self.related_articles, self.topics_dates = (
            self.ctx_handler.Get_trending_topics(abstracts_dict, publish_dict, n_topics)
        )

    async def Fill_database(self):
        await self.Fill_authors_table()
        await self.Fill_articles_table()
        await self.Fill_article_author_table()
        await self.Fill_topics_table()
        await self.Fill_topic_article_table()
        await self.Fill_categories_table(6, self.topics_description)
        await self.Fill_topic_category_table(self.categories_dict)
        await self.Fill_mentions_table()

        print("Database filled successfully!")

    async def Clear_databases(self):
        await self.database.connect()
        await authors_table.clear_table()
        await articles_table.clear_table()
        await article_author_table.clear_table()
        await topics_table.clear_table()
        await topic_article_table.clear_table()
        await categories_table.clear_table()
        await topic_category_table.clear_table()
        await mentions_table.clear_table()
        await self.database.disconnect()

    async def Fill_mentions_table(self):
        await self.database.connect()
        for key in self.topics_dates:
            topic_id = await topics_table.Get_id_by_name(key)
            for date, count in self.topics_dates[key].items():
                mention_row = mentions_table.Create_mention(
                    topic_id=topic_id, mention_date=date, mention_counter=count
                )
                await mentions_table.Insert_mention(mention_row)
        await self.database.disconnect()

    async def Fill_topic_category_table(self, categories_dict):
        await self.database.connect()
        for category in categories_dict.values():
            category_id = await categories_table.Get_id_by_name(
                category["category_name"]
            )
            for topic in category["topics"]:
                topic_id = await topics_table.Get_id_by_name(topic)
                topic_category_row = topic_category_table.Create_topic_category_row(
                    topic_id=topic_id, category_id=category_id
                )
                await topic_category_table.Insert_topic_article(topic_category_row)
        await self.database.disconnect()

    async def Fill_categories_table(self, number_of_categories, topics_descripton):
        categories = self.ctx_handler.Generate_categories_based_on_topics(
            number_of_categories, topics_descripton
        )
        self.categories_dict = categories
        await self.database.connect()

        for category in categories.values():
            category_name = category["category_name"]
            category_description = category["category_description"]
            category_row = categories_table.Create_category(
                name=category_name, summary=category_description
            )
            await categories_table.Insert_category(category_row)

        await self.database.disconnect()

    async def Fill_topic_article_table(self):
        await self.database.connect()
        for topic in self.related_articles:
            topic_id = await topics_table.Get_id_by_name(topic)
            for article_index in self.related_articles[topic]:
                article_id = await articles_table.Get_id_by_link(
                    self.publications_df.Link[article_index]
                )
                topic_article_row = topic_article_table.Create_topic_article_row(
                    topic_id=topic_id, article_id=article_id
                )
                await topic_article_table.Insert_topic_article(topic_article_row)
        await self.database.disconnect()

    async def Fill_authors_table(self):
        await self.database.connect()
        for i in range(self.db_len):
            authors = self.web_dict["authors"][i]
            for author in authors:
                author_row = authors_table.Create_author(author)
                await authors_table.Insert_author(author_row)
        await self.database.disconnect()

    async def Fill_articles_table(self):
        await self.database.connect()
        for i in range(self.db_len):
            article_name = self.publications_df.Title[i]
            article_link = self.publications_df.Link[i]
            article_publish_date = self.web_dict["publish_date"][i]
            article_abstract = self.web_dict["abstracts"][i]
            article_row = articles_table.Create_article(
                name=article_name,
                summary=article_abstract,
                link=article_link,
                publish_date=article_publish_date,
            )
            await articles_table.Insert_article(article_row)
        await self.database.disconnect()

    async def Fill_article_author_table(self):
        await self.database.connect()

        for i in range(self.db_len):
            article_link = self.publications_df.Link[i]
            authors = self.web_dict["authors"][i]

            article_id = await articles_table.Get_id_by_link(article_link)
            for author_name in authors:
                author_id = await authors_table.Get_id_by_name(author_name)
                try:
                    article_author_row = article_author_table.Create_article_author_row(
                        article_id=article_id, author_id=author_id
                    )
                except:
                    print("erro ao adicionar a tabela article_author")
                await article_author_table.Insert_article_author(article_author_row)

        await self.database.disconnect()

    async def Fill_topics_table(self):
        topics_articles_dict = self.worker.Format_topics_articles_dict(
            self.related_articles, self.publications_df.Title.to_list()
        )
        self.topic_summaries = self.ctx_handler.Generate_summary_based_on_topics(
            topics_articles_dict
        )
        self.topics_description = self.topic_summaries
        await self.database.connect()

        for topic in self.topic_summaries.keys():
            topic_row = topics_table.Create_topic(
                name=topic, summary=self.topic_summaries[topic]
            )
            await topics_table.Insert_topic(topic_row)

        await self.database.disconnect()
