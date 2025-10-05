from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from Context_agent import ContextAgent
import re

import nltk
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

    def Get_trending_topics(self,abstract_dict, n=10):
        if not abstract_dict:
            return [], {}

        indices_csv = list(abstract_dict.keys())
        texts = [(abstract_dict[i] if abstract_dict[i] is not None else "") for i in indices_csv ]

        texts_clean = [self.Preprocess_abstract(t) for t in texts]

        vectorizer = CountVectorizer(ngram_range=(1, 2), max_features=5000)
        vector_data = vectorizer.fit_transform(texts_clean)
        vocab = vectorizer.get_feature_names_out()

        word_freq = np.asarray(vector_data.sum(axis=0)).ravel()
        top_indices = np.argsort(word_freq)[::-1][:n]
        top_words = vocab[top_indices]
        top_counts = word_freq[top_indices]

        topic_indices = {}
        for i, word_idx in enumerate(top_indices):
            text_positions = vector_data[:, word_idx].nonzero()[0].tolist()
            text_indices_csv = [indices_csv[pos] for pos in text_positions]
            topic_indices[top_words[i]] = text_indices_csv

        top_words_freq = list(zip(top_words, top_counts))
        return top_words_freq, topic_indices
    
    #passar um dict com o nome dos topicos como chave e uma lista de titulos como valor
    def Generate_summary_based_on_topics(self,topics_articles_dict):
        
        # description_dict = {}
        # for topic,articles_list in topics_articles_dict.items():
        #     summary = self.llm_agent.Generate_topic_summary(topic,articles_list)
        #     description_dict[topic] = summary
        return self.llm_agent.Generate_topics_summary(topics_articles_dict)
