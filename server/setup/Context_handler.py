from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from setup.Context_agent import ContextAgent
import re
import pandas as pd
import nltk
from datetime import datetime


nltk.download('stopwords', quiet=True)
from nltk.corpus import stopwords
stop_words = set(stopwords.words('english'))

class Context_handler():
    def __init__(self):
        self.llm_agent = ContextAgent()

    def Preprocess_abstract(self,text):
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        tokens = [w for w in text.split() if w not in stop_words]
        return ' '.join(tokens)

    def Get_trending_topics(self, abstract_dict, publish_date_dict, n=10):
        if not abstract_dict:
            return [], {}, {}

        # Índices dos textos
        indices_csv = list(abstract_dict.keys())
        
        # Textos
        texts = [(abstract_dict[i] if abstract_dict[i] is not None else "") for i in indices_csv ]
        
        # Datas correspondentes aos textos
        dates = [publish_date_dict[i] for i in indices_csv]

        # Pré-processamento
        texts_clean = [self.Preprocess_abstract(t) for t in texts]

        # CountVectorizer
        vectorizer = CountVectorizer(ngram_range=(1, 2), max_features=5000)
        vector_data = vectorizer.fit_transform(texts_clean)
        vocab = vectorizer.get_feature_names_out()

        # Frequência total das palavras
        word_freq = np.asarray(vector_data.sum(axis=0)).ravel()
        top_indices = np.argsort(word_freq)[::-1][:n]
        top_words = vocab[top_indices]
        top_counts = word_freq[top_indices]

        # Criar dicionário para cada palavra com os índices dos textos onde aparece
        topic_indices = {}
        
        # Criar dicionário para agrupar por datas
        topic_by_date = {word: {} for word in top_words}

        for i, word_idx in enumerate(top_indices):
            # Posições dos textos onde a palavra aparece
            text_positions = vector_data[:, word_idx].nonzero()[0].tolist()
            
            # IDs dos textos
            text_indices_csv = [indices_csv[pos] for pos in text_positions]
            topic_indices[top_words[i]] = text_indices_csv

            # Frequência por data
            for pos in text_positions:
                date = dates[pos]
                topic_by_date[top_words[i]][date] = topic_by_date[top_words[i]].get(date, 0) + vector_data[pos, word_idx]

        # Combinar palavras e contagens totais
        top_words_freq = list(zip(top_words, top_counts))

        return top_words_freq, topic_indices, topic_by_date


    #passar um dict com o nome dos topicos como chave e uma lista de titulos como valor
    def Generate_summary_based_on_topics(self,topics_articles_dict):
        return self.llm_agent.Generate_topics_summary_individual(topics_articles_dict)

    def Generate_categories_based_on_topics(self,number_of_categories,topics_description_dict):
        return self.llm_agent.Generate_categories(number_of_categories,topics_description_dict)