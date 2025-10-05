from bs4 import BeautifulSoup
import requests
from datetime import date, datetime
import re

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
        formats = ["%Y %b %d", "%Y %b"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None



    def Get_publication_date_from_soup(self, soup):
        # 1️⃣ Tenta meta tag primeiro
        meta_date = soup.find('meta', attrs={'name': 'citation_publication_date'})
        if meta_date and 'content' in meta_date.attrs:
            date_str = meta_date['content']
            final_date = self.parse_publication_date(date_str)
            if final_date is not None:
                return final_date


        # 2️⃣ Pega todo o texto da página ou de uma seção específica
        if soup.find('section', class_='pmc_layout_citation font-seocndary font-xs'):
            text = soup.find('section', class_='pmc_layout_citation font-seocndary font-xs').get_text(separator=' ', strip=True)
        else:
            text = soup.get_text(separator=' ', strip=True)


        # 3️⃣ Regex flexível para datas
        # Procura padrões como:
        # 2022 Jan 1, 2022 January 1, Jan 1, 2022, 1 Jan 2022, 1 January 2022
        date_pattern = re.compile(
            r'(\d{4})\s+([A-Za-z]{3,9})\s+(\d{1,2})|'   # 2022 Jan 1 ou 2022 January 1
            r'([A-Za-z]{3,9})\s+(\d{1,2}),?\s+(\d{4})|' # Jan 1, 2022 ou January 1, 2022
            r'(\d{1,2})\s+([A-Za-z]{3,9})\s+(\d{4})'    # 1 Jan 2022 ou 1 January 2022
        )

        match = date_pattern.search(text)
        if match:
            groups = [g for g in match.groups() if g]  # remove None
            date_str = " ".join(groups)
            # Tenta todos os formatos possíveis
            for fmt in ["%Y %b %d", "%Y %B %d", "%b %d %Y", "%B %d %Y", "%d %b %Y", "%d %B %Y"]:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue

        # 4️⃣ Se não encontrar nada
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

