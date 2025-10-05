from pydantic import RootModel
import os
from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_core.messages import SystemMessage
from langchain.output_parsers import PydanticOutputParser


api_key = os.getenv("GEMINI_API_KEY")


class TopicNames(RootModel[Dict[str, str]]):
    pass

class TopicAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",api_key=api_key)
        self.context_prompt = (
            "You are a market intelligence expert and trend analyst in science and technology. "
        )


    def Generate_names(self, topic_string: str) -> str:
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.context_prompt),
            ("Your task is to analyze the output of an LDA model and assign meaningful, short, and descriptive names "
            "to each topic based on its keywords. "
            "Return your output STRICTLY as a valid JSON object mapping the topic ID to its name.\n"
            "Example:\n"
            "{{\n"
            "  'topic 1': 'topic name',\n"
            "  'topic 2': 'topic name'\n"
            "}}\n"),
            ("human", "Generate topic names considering this output: {topic_string}")
        ])


        topic_chain = prompt | self.llm | PydanticOutputParser(pydantic_object=TopicNames)
        result = topic_chain.invoke({"topic_string": topic_string})
        return result.root
    
    def Generate_summary(self, topic_string: str) -> str:
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.context_prompt),
            ("Your task is to analyze a topic name for a give category and the titles from the articles that belong to this category"
            " and write a small descriptive summary to understant site visitors to understand what that topic is about "
            ),
            ("human", "Generate text considering this this informations: {topic_string}")
        ])


        topic_chain = prompt | self.llm | StrOutputParser()
        result = topic_chain.invoke({"topic_string": topic_string})
        return result


    def Generate_topics_summary(self, topic_string: str) -> str:
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.context_prompt),
            ("Your task is to analyze a topic name for a give category and the titles from the articles that belong to this category"
            " and write a small descriptive summary to understant site visitors to understand what that topic is about "
            ),
            ("human", "Generate text considering this this informations: {topic_string}")
        ])


        topic_chain = prompt | self.llm | StrOutputParser()
        result = topic_chain.invoke({"topic_string": topic_string})
        return result