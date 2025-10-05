from pydantic import RootModel
import os
from typing import Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_core.messages import SystemMessage
from langchain.output_parsers import JsonOutputKeyToolsParser
import json

api_key = os.getenv("GEMINI_API_KEY")


class ContextAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",api_key=api_key)
        self.context_prompt = (
            "You are a market intelligence expert and trend analyst in science and technology. "
        )



    def Generate_topics_summary(self, topics_articles_dict):
        task_description = (
            "Analyze the dictionary of topic names and the article titles for each topic, "
            "and write a small descriptive summary for each topic. "
            "Return a single JSON object with topic names as keys and summaries as values. "
            "Do not create new topics; include all passed topics."
        )

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.context_prompt),
            SystemMessage(content=task_description),
            ("human", "Generate topic description considering this: {data_input}")
        ])

        chain = prompt | self.llm

        # Executa a chain
        raw_output = chain.invoke({"data_input": topics_articles_dict})

        # Se for AIMessage, pega o conteúdo
        if hasattr(raw_output, "content"):
            raw_output = raw_output.content

        # Remove ```json e ``` caso existam
        raw_output = raw_output.strip()
        if raw_output.startswith("```json"):
            raw_output = raw_output[len("```json"):].strip()
        if raw_output.endswith("```"):
            raw_output = raw_output[:-3].strip()

        # Converte para dict
        try:
            summaries_dict = json.loads(raw_output)
        except Exception as e:
            print("Erro ao converter JSON:", e)
            print("Saída bruta do LLM:", raw_output)
            summaries_dict = {}

        return summaries_dict



    def Generate_topic_summary(self,topic_name,articles_list):
        task_description = ("""
        Your task is to analyze a topic name for a give subject and the titles from the articles that presents this topic
        and write a small descriptive summary to site visitors to understand what that topic is about
        """)
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.context_prompt),
            task_description,
            ("human", "Generate topic description considering this: {data_input}")
        ])
        chain = prompt | self.llm | StrOutputParser()
        data_input = (f"""
        Topic: {topic_name}
        Articles list: {articles_list}
        """)
        result = chain.invoke({"data_input": data_input})
        return result
