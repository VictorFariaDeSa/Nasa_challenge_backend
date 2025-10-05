from bs4 import BeautifulSoup
import requests
from datetime import date, datetime


class Webscrapper():
    def __init__(self):
        pass




    def Get_all_data_from_url(self,url):
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        publication_date = self.Get_publication_date_from_soup(soup)
        authors = self.Get_authors_from_soup(soup)
        abstract = self.Get_abstracts_from_soup(soup)
        return {"abstract":abstract,
                "authors":authors,
                "publish_date":publication_date}



    def parse_publication_date(self,date_str):
        formats = ["%Y %b %d", "%Y %b", "%Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None


    def Get_publication_date_from_soup(self, soup):
        meta_date = soup.find('meta', attrs={'name': 'citation_publication_date'})
        if meta_date and 'content' in meta_date.attrs:
            date_str = meta_date['content']
            return self.parse_publication_date(date_str)
        else:
            return None

    def Get_authors_from_soup(self,soup):
        meta_authors = soup.find_all('meta', attrs={'name': 'citation_author'})
        authors = [meta['content'] for meta in meta_authors]
        return authors
    
    
    def Get_abstracts_from_soup(self,soup):
        abstract_section = soup.find('section', class_='abstract')

        if abstract_section:
            abstract_p = abstract_section.find('p', recursive=False)
            if abstract_p:
                abstract_text = abstract_p.text.strip()
                return abstract_text
            
        abstract_section = soup.find('section', class_='pmc_sec_title')

        if abstract_section:
            abstract_p = abstract_section.find('p', recursive=False)
            if abstract_p:
                abstract_text = abstract_p.text.strip()
                return abstract_text

