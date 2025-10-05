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




    def Generate_categories(self, number_of_categories, topics_dict: dict):
        task_description = (
            "Analyze the dictionary of topic names and their summaries, and create categories to group these topics. "
            "One topic can belong to more than one category if necessary, and one category usually has multiple topics. "
            "You should also write a short, clear description for each category you create. "
            "The user will specify how many categories they want. "
            "Your output must be valid JSON following this structure:\n\n"
            "{\n"
            "  '1': {\n"
            "     'category_name': '...',\n"
            "     'category_description': '...',\n"
            "     'topics': ['topic1', 'topic2', ...]\n"
            "  },\n"
            "  '2': {...}\n"
            "}\n\n"
            "Remember: you are only creating categories — the topic names and summaries must not be modified."
        )

        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.context_prompt),
            SystemMessage(content=task_description),
            ("human", "Generate {number_of_categories} categories considering this: {data_input}")
        ])

        chain = prompt | self.llm
        raw_output = chain.invoke({"data_input": topics_dict,
                                    "number_of_categories":number_of_categories})

        if hasattr(raw_output, "content"):
            raw_output = raw_output.content

        raw_output = raw_output.strip()
        if raw_output.startswith("```json"):
            raw_output = raw_output[len("```json"):].strip()
        if raw_output.endswith("```"):
            raw_output = raw_output[:-3].strip()

        try:
            json_text = raw_output.replace("'", '"')
            categories = json.loads(json_text)
        except json.JSONDecodeError as e:
            categories = {}

        return categories

