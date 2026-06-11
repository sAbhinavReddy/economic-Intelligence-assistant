import os
import requests
import feedparser
from pathlib import Path
from dotenv import load_dotenv
from services.utils import normalize_article, deduplicate_articles, save_json

load_dotenv()


class NewsCollector:
    def __init__(self):
        self.news_api_key = os.getenv('NEWS_API_KEY', '')
        if not self.news_api_key:
            try:
                import streamlit as st
                self.news_api_key = st.secrets["NEWS_API_KEY"]
            except Exception:
                pass
        self.raw_file = Path('data/raw_news.json')

    def fetch_newsapi(self):
        if not self.news_api_key:
            return []

        url = 'https://newsapi.org/v2/top-headlines'
        params = {
            'country': 'in',
            'category': 'business',
            'pageSize': 100,
            'apiKey': self.news_api_key
        }

        try:
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            return [
                normalize_article({
                    'title': item.get('title'),
                    'description': item.get('description'),
                    'source': 'NewsAPI',
                    'url': item.get('url'),
                    'published_at': item.get('publishedAt')
                })
                for item in data.get('articles', [])
            ]
        except Exception as error:
            print('NewsAPI fetch error:', error)
            return []

    def fetch_google_news(self):
        feed_url = 'https://news.google.com/rss/search?q=india+economy&hl=en-IN&gl=IN&ceid=IN:en'
        try:
            response = requests.get(feed_url, timeout=15)
            feed = feedparser.parse(response.content)
            return [
                normalize_article({
                    'title': entry.get('title'),
                    'description': entry.get('summary', ''),
                    'source': 'Google News',
                    'url': entry.get('link'),
                    'published_at': entry.get('published', '')
                })
                for entry in feed.entries
            ]
        except Exception as error:
            print('Google News fetch error:', error)
            return []

    def fetch_economic_times(self):
        """Fetch news from Economic Times RSS feed."""
        feed_urls = [
            'https://economictimes.indiatimes.com/rssfeeds/13355576.cms',
            'https://economictimes.indiatimes.com/rssfeeds/1715242.cms'
        ]
        all_articles = []
        for feed_url in feed_urls:
            try:
                response = requests.get(feed_url, timeout=15)
                feed = feedparser.parse(response.content)
                for entry in feed.entries:
                    article = normalize_article({
                        'title': entry.get('title'),
                        'description': entry.get('summary', ''),
                        'source': 'Economic Times',
                        'url': entry.get('link'),
                        'published_at': entry.get('published', '')
                    })
                    all_articles.append(article)
            except Exception as error:
                print(f'Economic Times fetch error for {feed_url}:', error)
                continue
        return all_articles

    def collect_all(self):
        all_articles = []
        all_articles.extend(self.fetch_newsapi())
        all_articles.extend(self.fetch_google_news())
        all_articles.extend(self.fetch_economic_times())

        all_articles = [article for article in all_articles if article.get('title') and article.get('url')]
        unique_articles = deduplicate_articles(all_articles)
        save_json(str(self.raw_file), unique_articles)
        return unique_articles


if __name__ == '__main__':
    collector = NewsCollector()
    collector.collect_all()