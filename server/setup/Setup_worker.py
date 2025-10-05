from concurrent.futures import ThreadPoolExecutor, as_completed
from Webscrapper import Webscrapper

from concurrent.futures import ThreadPoolExecutor, as_completed
# Mantenha a importação da classe Webscrapper, mas ela deve ser alterada acima!
# from Webscrapper import Webscrapper 

class Setup_worker():
    # ... __init__ ...

    def Get_all_data(self, url_list):
        webscrapper = Webscrapper() 
        
        all_data = {'authors': {}, 'publish_date': {}, 'abstracts': {}}

        def fetch_all_data(i, url):
            data = webscrapper.Get_all_data_from_url(url)
            return i, data

        with ThreadPoolExecutor(max_workers=40) as executor:
            futures = {executor.submit(fetch_all_data, i, url): i for i, url in enumerate(url_list)}
            
            # Processa os resultados
            for future in as_completed(futures):
                i, data = future.result()
                
                # Distribui os dados coletados em seus respectivos dicionários
                all_data['authors'][i] = data['authors']
                all_data['publish_date'][i] = data['publish_date']
                all_data['abstracts'][i] = data['abstract']

        return all_data

    def Format_topics_articles_dict(self,related_articles,articles_name):
        new_dict = {}
        for key in  related_articles.keys():
            new_dict[key] = [articles_name[i] for i in related_articles[key]]
        return new_dict
