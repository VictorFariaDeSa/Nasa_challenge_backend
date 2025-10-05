from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select, join, func, cast, Integer
from typing import List, Optional
import datetime
import numpy as np
from scipy import stats
import math

# Importações do seu projeto
from setup.Setup_handler import Setup_handler
from postgress_integration.db_interface import database
from postgress_integration.tables.articles_table import articles_table, ArticleRow
from postgress_integration.tables.authors_table import authors_table, AuthorRow
from postgress_integration.tables.categories_table import categories_table, CategoryRow
from postgress_integration.tables.mentions_table import mentions_table, MentionRow
from postgress_integration.tables.topics_table import topics_table, TopicRow
from postgress_integration.tables.topic_category_table import topic_category_table
from postgress_integration.tables.topic_article_table import topic_article_table
from postgress_integration.tables.article_author_table import article_author_table

# --- Pydantic Models for custom responses ---


class YearlyMention(BaseModel):
    year: int
    total_mentions: int


class CategorySlim(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class ArticleSlim(BaseModel):
    id: int
    name: str
    link: Optional[str] = None
    publish_date: Optional[datetime.date] = None

    class Config:
        orm_mode = True


class ArticleSlimWithAuthors(ArticleSlim):
    authors: List[AuthorRow]


class TopicSlim(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


### MUDANÇA 1 ###
# Novo modelo para os tópicos relacionados, que agora inclui mais detalhes
class RelatedTopicWithDetails(TopicSlim):
    totalMentions: int
    trend: float
    mentions: List[YearlyMention]


class TopicWithCategoriesAndYearlyMentions(TopicRow):
    id: int
    totalMentions: int
    trend: float
    categories: List[CategorySlim]
    mentions: List[YearlyMention]


### MUDANÇA 2 ###
# Modelo principal atualizado para usar o novo modelo de tópicos relacionados
class FullTopicDetails(TopicRow):
    id: int
    totalMentions: int
    trend: float
    categories: List[CategorySlim]
    articles: List[ArticleSlimWithAuthors]
    mentions: List[YearlyMention]
    related_topics: List[RelatedTopicWithDetails]  # Atualizado aqui


# --- FastAPI App Setup ---

app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/healthcheck")
async def healthcheck():
    return {"response": "alive7"}


def calculate_trend(yearly_mentions: List[dict]) -> float:
    """
    Calcula a tendência percentual anual de menções usando regressão linear
    na metade mais recente do período de dados.
    """
    sorted_mentions = sorted(yearly_mentions, key=lambda x: x["year"])

    if len(sorted_mentions) < 2:
        return 0.0

    num_years_total = len(sorted_mentions)
    period_to_analyze = max(2, math.ceil(num_years_total / 2))
    analysis_data = sorted_mentions[-period_to_analyze:]

    if len(analysis_data) < 2:
        return 0.0

    years = np.array([d["year"] for d in analysis_data])
    mentions_counts = np.array([d["total_mentions"] for d in analysis_data])

    if np.sum(mentions_counts) == 0:
        return 0.0

    try:
        slope, _, _, _, _ = stats.linregress(years, mentions_counts)
    except ValueError:
        return 0.0

    average_mentions = np.mean(mentions_counts)
    if average_mentions == 0:
        return 100.0 if slope > 0 else 0.0

    annual_growth_rate = (slope / average_mentions) * 100.0
    return round(annual_growth_rate, 2)


# --- API ENDPOINTS ---


@app.get("/categories", response_model=List[CategoryRow])
async def get_all_categories():
    """Retorna todas as categorias."""
    query = select(categories_table.table)
    return await database.fetch_all(query)


@app.get("/topics", response_model=List[TopicWithCategoriesAndYearlyMentions])
async def get_topics_with_details():
    """
    Retorna todos os tópicos que possuem pelo menos uma menção,
    ordenados pelo total de menções.
    """
    query_topics = (
        select(
            topics_table.table,
            func.sum(mentions_table.table.c.mention_counter).label("totalMentions"),
        )
        .join(
            mentions_table.table,
            topics_table.table.c.id == mentions_table.table.c.topic_id,
        )
        .group_by(topics_table.table.c.id)
        .order_by(func.sum(mentions_table.table.c.mention_counter).desc())
    )
    all_topics_with_totals = await database.fetch_all(query_topics)

    results = []
    for topic in all_topics_with_totals:
        topic_id = topic["id"]

        category_join = join(
            categories_table.table,
            topic_category_table.table,
            categories_table.table.c.id == topic_category_table.table.c.category_id,
        )
        query_categories = (
            select(categories_table.table.c.id, categories_table.table.c.name)
            .select_from(category_join)
            .where(topic_category_table.table.c.topic_id == topic_id)
        )
        categories = await database.fetch_all(query_categories)

        year_column = cast(
            func.extract("year", mentions_table.table.c.mention_date), Integer
        ).label("year")
        query_mentions_aggregated = (
            select(
                year_column,
                func.sum(mentions_table.table.c.mention_counter).label(
                    "total_mentions"
                ),
            )
            .where(mentions_table.table.c.topic_id == topic_id)
            .group_by(year_column)
            .order_by(year_column.asc())
        )
        aggregated_mentions = await database.fetch_all(query_mentions_aggregated)
        trend = calculate_trend(aggregated_mentions)

        results.append(
            {
                "id": topic["id"],
                "name": topic["name"],
                "summary": topic["summary"],
                "totalMentions": topic["totalMentions"],
                "trend": trend,
                "categories": categories,
                "mentions": aggregated_mentions,
            }
        )
    return results


@app.get("/topic/{topic_id}", response_model=FullTopicDetails)
async def get_full_topic_details(topic_id: int):
    """
    Retorna os detalhes completos de um tópico, incluindo menções e tendência
    para cada tópico relacionado.
    """
    query_topic = select(topics_table.table).where(topics_table.table.c.id == topic_id)
    topic = await database.fetch_one(query_topic)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Busca categorias do tópico principal
    category_join = join(
        categories_table.table,
        topic_category_table.table,
        categories_table.table.c.id == topic_category_table.table.c.category_id,
    )
    query_categories = (
        select(categories_table.table.c.id, categories_table.table.c.name)
        .select_from(category_join)
        .where(topic_category_table.table.c.topic_id == topic_id)
    )
    categories = await database.fetch_all(query_categories)

    # Busca e agrega menções do tópico principal
    year_column = cast(
        func.extract("year", mentions_table.table.c.mention_date), Integer
    ).label("year")
    query_mentions_aggregated = (
        select(
            year_column,
            func.sum(mentions_table.table.c.mention_counter).label("total_mentions"),
        )
        .where(mentions_table.table.c.topic_id == topic_id)
        .group_by(year_column)
        .order_by(year_column.asc())
    )
    aggregated_mentions = await database.fetch_all(query_mentions_aggregated)
    total_mentions_for_topic = sum(
        mention["total_mentions"] for mention in aggregated_mentions
    )
    trend = calculate_trend(aggregated_mentions)

    # Busca a lista base de tópicos relacionados
    subquery_category = (
        select(topic_category_table.table.c.category_id)
        .where(topic_category_table.table.c.topic_id == topic_id)
        .scalar_subquery()
    )
    query_related = (
        select(topics_table.table)
        .join(
            topic_category_table.table,
            topics_table.table.c.id == topic_category_table.table.c.topic_id,
        )
        .where(topic_category_table.table.c.category_id.in_(subquery_category))
        .where(topics_table.table.c.id != topic_id)
        .distinct()
    )
    related_topics_base = await database.fetch_all(query_related)

    ### MUDANÇA 3 ###
    # Itera sobre os tópicos relacionados para enriquecer os dados
    related_topics_with_details = []
    for rel_topic in related_topics_base:
        rel_topic_id = rel_topic["id"]

        # Busca menções para cada tópico relacionado
        query_rel_mentions = (
            select(
                year_column,
                func.sum(mentions_table.table.c.mention_counter).label(
                    "total_mentions"
                ),
            )
            .where(mentions_table.table.c.topic_id == rel_topic_id)
            .group_by(year_column)
            .order_by(year_column.asc())
        )
        rel_aggregated_mentions = await database.fetch_all(query_rel_mentions)

        # Calcula o total e a tendência para cada tópico relacionado
        total_mentions_for_rel_topic = sum(
            m["total_mentions"] for m in rel_aggregated_mentions
        )
        rel_trend = calculate_trend(rel_aggregated_mentions)

        # Adiciona o objeto enriquecido à lista
        related_topics_with_details.append(
            {
                "id": rel_topic_id,
                "name": rel_topic["name"],
                "totalMentions": total_mentions_for_rel_topic,
                "trend": rel_trend,
                "mentions": rel_aggregated_mentions,
            }
        )

    # Busca artigos com seus autores
    articles_with_authors = []
    article_join = join(
        articles_table.table,
        topic_article_table.table,
        articles_table.table.c.id == topic_article_table.table.c.article_id,
    )
    query_articles = (
        select(articles_table.table)
        .select_from(article_join)
        .where(topic_article_table.table.c.topic_id == topic_id)
        .order_by(articles_table.table.c.publish_date.desc().nulls_last())
        .limit(5)
    )
    articles = await database.fetch_all(query_articles)

    for article in articles:
        author_join = join(
            authors_table.table,
            article_author_table.table,
            authors_table.table.c.id == article_author_table.table.c.author_id,
        )
        query_authors = (
            select(authors_table.table)
            .select_from(author_join)
            .where(article_author_table.table.c.article_id == article["id"])
        )
        authors = await database.fetch_all(query_authors)
        articles_with_authors.append({**article, "authors": authors})

    return {
        **topic,
        "totalMentions": total_mentions_for_topic,
        "trend": trend,
        "categories": categories,
        "articles": articles_with_authors,
        "mentions": aggregated_mentions,
        "related_topics": related_topics_with_details,  # Retorna a lista enriquecida
    }
