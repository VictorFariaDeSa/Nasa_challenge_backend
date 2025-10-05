
import pandas as pd
from gensim import corpora, models
from gensim.parsing.preprocessing import STOPWORDS
from TopicAgent import TopicAgent
from gensim.parsing.preprocessing import STOPWORDS
from concurrent.futures import ThreadPoolExecutor, as_completed

class LDA_handler():
    def __init__(self,df):
        self.df = df
        self.classify_agent = TopicAgent()

    def Generate_article_text_list(self):
        return self.df['Title'].tolist()

    def Generate_tokenized_list(self,text_list):
        return [
            [word for word in text.lower().split() if word not in STOPWORDS]
            for text in text_list
        ]

    def Transform_data_numeric(self,tokens_list):
        dictionary = corpora.Dictionary(tokens_list)
        corpus = [dictionary.doc2bow(text) for text in tokens_list]
        return dictionary, corpus
    
    def Generate_lda_model(self,topics_number,corpus,dictionary,passes):
        lda_model = models.LdaModel(corpus, num_topics=topics_number, id2word=dictionary, passes=passes, random_state=42)  
        return lda_model

    def Get_lda_topics_keywords(self, lda_model):
        result = ""
        for i in range(lda_model.num_topics):
            topic_text = f"topic {i}: {lda_model.print_topic(i)}\n"
            result += topic_text
        return result

    def Append_model_to_df(self,lda_model,corpus):
        title_topics = []
        for doc_bow in corpus:
            title_topics.append(lda_model.get_document_topics(doc_bow))

        self.df['topics'] = title_topics

    def Create_model_names(self,topics_keywords):
        return self.classify_agent.Generate_names(topics_keywords)

    def Get_all_titles_from_topic(self, topic_num, threshold=0.4):

        def topic_greater_than_threshold(topicos):
            if topic_num >= len(topicos):
                return False
            _, valor = topicos[topic_num]
            return valor > threshold

        return self.df[self.df['topics'].apply(topic_greater_than_threshold)]['Title'].tolist()
    

    def summarize_topic(self,i,model_names,max_titles_per_topic):
        topic_name = model_names[f"topic {i}"]
        articles_list = self.Get_all_titles_from_topic(i, 0.95)
        summary_prompt = f"""
        Topic name: {topic_name}
        Article list: {articles_list}
        """
        summary_text = self.classify_agent.Generate_summary(summary_prompt)
        return i, {"name": topic_name, "description": summary_text}
    


    def Create_topics_dict(self, number_of_topics, max_titles_per_topic=100):
        topics_dict = {}
        text_list = self.Generate_article_text_list()
        tokenized_list = self.Generate_tokenized_list(text_list)
        dictionary, corpus = self.Transform_data_numeric(tokenized_list)
        lda_model = self.Generate_lda_model(number_of_topics, corpus, dictionary, 20)
        topics_keywords = self.Get_lda_topics_keywords(lda_model)
        self.Append_model_to_df(lda_model, corpus)
        
        model_names = self.Create_model_names(topics_keywords)
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.summarize_topic, i,model_names,max_titles_per_topic) for i in range(number_of_topics)]
            for future in as_completed(futures):
                i, topic_dict = future.result()
                topics_dict[i] = topic_dict
        
        return topics_dict

