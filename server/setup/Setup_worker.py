from concurrent.futures import ThreadPoolExecutor, as_completed
from setup.Webscrapper import Webscrapper
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

class Setup_worker():
    # ... __init__ ...

    def Get_all_data(self, df):
        webscrapper = Webscrapper()
        url_list = df['Link'].to_list()
        print(url_list)
        all_data = {
            'authors': {},
            'publish_date': {},
            'abstracts': {}
        }

        def fetch_all_data(i, url):
            try:
                data = webscrapper.Get_all_data_from_url(url)
                return i, data
            except Exception as e:
                print(f"Error ao processsing URL (index {i}): {url}\n{e}")
                return i, {'authors': None, 'publish_date': None, 'abstracts': None}

        with ThreadPoolExecutor(max_workers=40) as executor:
            futures = {executor.submit(fetch_all_data, i, url): i for i, url in enumerate(url_list)}

            for future in as_completed(futures):
                i, data = future.result()

                all_data['authors'][i] = data.get('authors', None)
                all_data['publish_date'][i] = data.get('publish_date', None)
                all_data['abstracts'][i] = data.get('abstract', None)

        

        df['authors'] = pd.Series(all_data['authors'])
        df['publish_date'] = pd.Series(all_data['publish_date'])
        df['abstracts'] = pd.Series(all_data['abstracts'])

        return all_data, df

    def Format_topics_articles_dict(self,related_articles,articles_name):
        new_dict = {}
        for key in  related_articles.keys():
            new_dict[key] = [articles_name[i] for i in related_articles[key]]
        return new_dict
