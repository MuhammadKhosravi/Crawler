import re
import requests
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup


class Scraper:

    def __init__(self, current_year, current_month):
        self.current_year = current_year
        self.current_month = current_month

    def get_URL_content(self, URL):
        """
        This function takes a URL as an input and returns the content of the URL. 
        It uses the requests library to make a GET request to the URL and returns the content of the response. 
        If an exception is encountered, it retries the request.

        Parameters
        ----------
        URL : str
            The URL to get the content of.
        
        Returns
        -------
        content : str
            The content of the URL.

        """
        while True:
            try:
                content = requests.get(URL)
                return content.text
            except:
                continue

    def generate_page_URL(self, page_index, category, year, month):
        """
        This function generates the URL for a specific page of a category's archive, given the page index, category, year and month.
        The function uses a dictionary to map categories to their corresponding numeric codes, which are used to construct the URL.

        Parameters
        ----------
        page_index : int
            The index of the page.
        category : str
            The category of the page.
        year : int
            The year of the page.
        month : int
            The month of the page.
        
        Returns
        -------
        URLs : list
            A list of URLs for all pages of the archive of the given category, year and month.

        """

        tp = {'Politics': 6, 'World': 11, 'Economy': 10, 'Society': 5, 'City': 7,
              'Sport': 9, 'Science': 20, 'Culture': 26, 'IT': 718, 'LifeSkills': 21}[category]
        return f'https://www.hamshahrionline.ir/archive?pi={page_index}&tp={tp}&ty=1&ms=0&mn={month}&yr={year}'

    def get_page_URLs_by_time(self, category, year, month):
        """
        This function takes a category, year, and month as input and returns a list of URLs for all pages of the archive of that category, year and month.
        It uses the generate_page_URL() function to generate URLs for pages and checks if the pages exist by searching for pagination in the HTML content of each page.

        Parameters
        ----------
        category : str
            The category of the page.
        year : int
            The year of the page.
        month : int
            The month of the page.
        
        Returns
        -------
        URLs : list
            A list of URLs for all pages of the archive of the given category, year and month.

        """
        URLs = []
        page_index = 1
        while True:
            URL = self.generate_page_URL(page_index, category, year, month)
            content = self.get_URL_content(URL)
            soup = BeautifulSoup(content, 'html.parser')
            pagination = soup.find_all("ul", {"class": "pagination justify-content-center"})
            if len(pagination) == 0:
                break
            URLs.append(URL)
            page_index += 1
        return URLs

    def get_page_URLs_since(self, category, year, month):
        """
        This function takes a category, year, and month as input and returns a list of URLs for all pages of the archive of that category since that year and month.
        It uses the get_page_URLs_by_time() function to get URLs for all pages of the archive for each month and year.

        Parameters
        ----------
        category : str
            The category of the page.
        year : int
            The year of the page.
        month : int
            The month of the page.
        
        Returns
        -------
        URLs : list
            A list of URLs for all pages of the archive of the given category, year and month.
        
        """
        URLs = []
        with tqdm() as pbar:
            while True:
                pbar.set_description(f'[{category}] [Extracting page URLs] [Date: {year}/{month}]')
                URLs_by_time = self.get_page_URLs_by_time(category, year, month)
                URLs += URLs_by_time
                if self.current_year > year:
                    if month < 12:
                        month += 1
                    else:
                        year += 1
                        month = 1
                elif self.current_year == year:
                    if self.current_month > month:
                        month += 1
                    else:
                        break
                else:
                    break
        return URLs

    def get_news_URLs_since(self, category, year, month):
        """
        This function takes a category, year, and month as input and returns a list of URLs for all news articles of that category since that year and month.)
        It uses the get_page_URLs_since() function to get URLs for all pages of the archive and uses BeautifulSoup to scrape the URLs of news articles from each page.

        Parameters
        ----------
        category : str
            The category of the page.
        year : int
            The year of the page.
        month : int
            The month of the page.
        
        Returns
        -------
        URLs : list
            A list of URLs for all news articles of the given category, year and month.
        
        """
        news_URLs = []
        page_URLs = self.get_page_URLs_since(category, year, month)
        with tqdm(page_URLs) as pbar:
            for page_URL in pbar:
                pbar.set_description(f'[{category}] [Extracting news URLs] [{len(news_URLs)} news until now]')
                content = self.get_URL_content(page_URL)
                soup = BeautifulSoup(content, 'html.parser')
                for news_headline in soup.find_all('li', {'class': 'news'}):
                    url = news_headline.find('a', href=True)
                    if url:
                        link = url['href']
                        news_URLs.append(link)
        return news_URLs

    def parse_news(self, URL, category):
        """
        This function takes a URL and category as input and returns a dictionary containing the date, title, intro, and body of the news article.
        It uses the BeautifulSoup library to parse the HTML content of the page and extract the relevant information.

        Parameters
        ----------
        URL : str
            The URL of the page.
        category : str
            The category of the news.

        Returns
        -------
        news : dict
            A dictionary containing the date, title, intro, and body of the news article.
        
        """
        BASE_URL = 'https://www.hamshahrionline.ir'
        try:
            content = self.get_URL_content(BASE_URL + URL)
            soup = BeautifulSoup(content, 'html.parser')
            title = soup.find("a", {"itemprop": "headline"}).get_text()
            date = soup.find('div', {'class': 'item-date'}).find('span').get_text()
            intro = soup.find('p', {'class': "introtext"}).get_text()
            body = soup.find('div', {'itemprop': 'articleBody'}).get_text()
            return {
                'date': date,
                'title': title,
                'intro': intro,
                'body': body,
                'category': category,
            }
        except:
            return None

    def scrape(self, from_year, from_month):
        categories = ['Politics', 'World', 'Economy', 'Society', 'City',
                      'Sport', 'Science', 'Culture', 'IT', 'LifeSkills']
        news = []
        for category in categories:
            URLs = self.get_news_URLs_since(category, from_year, from_month)
            with tqdm(URLs) as pbar:
                pbar.set_description(f'[{category}] [Scraping news]')
                for URL in pbar:
                    news_in_category = self.parse_news(URL, category)
                    news += news_in_category
        news = list(filter(None, news))
        pd.DataFrame(news).to_csv(f'dataset.csv', encoding='utf-8')


if __name__ == '__main__':
    scrapper = Scraper(1401, 11)
    scrapper.scrape(1401, 10)
