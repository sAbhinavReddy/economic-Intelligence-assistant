import json
import os
import re
import time
from pathlib import Path
import streamlit as st
import requests
from concurrent.futures import ThreadPoolExecutor


def ensure_directory(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def save_json(path, data):
    ensure_directory(os.path.dirname(path))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def safe_load_json(path):
    if not os.path.exists(path):
        return []

    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def clean_html(text):
    if not isinstance(text, str):
        return ''
    clean = re.sub(r'<[^>]+>', '', text)
    return clean.strip()


def normalize_article(article):
    title = article.get('title') or article.get('headline') or 'Untitled'
    description = article.get('description') or article.get('summary') or ''
    source = article.get('source') or article.get('provider') or 'Unknown'
    url = article.get('url') or article.get('link') or ''
    published_at = article.get('published_at') or article.get('published') or article.get('pubDate') or ''

    return {
        'title': clean_html(title),
        'description': clean_html(description),
        'source': source,
        'url': url,
        'published_at': published_at
    }


def deduplicate_articles(articles):
    seen_urls = set()
    seen_titles = set()
    unique_articles = []
    for article in articles:
        url = article.get('url', '').strip()
        title = article.get('title', '').strip()
        identity = url or title
        if not identity or identity in seen_urls or identity in seen_titles:
            continue
        seen_urls.add(identity)
        seen_titles.add(identity)
        unique_articles.append(article)
    return unique_articles


def get_last_updated():
    """Get the last updated timestamp from metadata file."""
    meta_file = Path('data/metadata.json')
    if meta_file.exists():
        try:
            with open(meta_file, 'r') as f:
                meta = json.load(f)
                return meta.get('last_updated', 'Never')
        except Exception:
            return 'Never'
    return 'Never'


def save_last_updated():
    """Save the current timestamp as last updated."""
    meta_file = Path('data/metadata.json')
    ensure_directory('data')
    try:
        with open(meta_file, 'w') as f:
            json.dump({'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')}, f)
    except Exception:
        pass


def get_trending_topics(articles, top_n=5):
    """Extract trending topics from analyzed news articles."""
    from collections import Counter
    words = []
    stop_words = {'the', 'a', 'an', 'in', 'of', 'to', 'for', 'and', 'is', 'on', 'at', 'by', 'with', 'from', 'as', 'are', 'was', 'were', 'has', 'have', 'been', 'its', 'their', 'our', 'this', 'that', 'will', 'can'}
    
    for article in articles:
        title = article.get('title', '')
        category = article.get('category', '')
        for text in [title, category]:
            tokens = re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\b', text)
            for token in tokens:
                lower = token.lower()
                if lower not in stop_words and len(token) > 2:
                    words.append(token)
    
    counter = Counter(words)
    return [word for word, count in counter.most_common(top_n)]


def get_sample_articles():
    """Provide fallback sample articles while initial fetch is running."""
    return [
        {
            'title': 'India\'s GDP Growth Projected at 7% for the Current Fiscal Year',
            'description': 'A comprehensive report on India\'s economic outlook indicates robust growth metrics.',
            'source': 'Sample News',
            'url': '#',
            'published_date': time.strftime('%Y-%m-%d'),
            'category': 'Economy',
            'what_happened': 'Economic experts project a strong 7% GDP growth for India this fiscal year.',
            'why_it_happened': 'This is driven by strong domestic demand and government capital expenditure.',
            'possible_impact': 'Positive growth will likely boost job creation and attract more foreign direct investment.',
            'sentiment': 'Positive'
        },
        {
            'title': 'RBI Keeps Repo Rate Unchanged at 6.5%',
            'description': 'In its latest monetary policy committee meeting, the RBI maintained the status quo.',
            'source': 'Sample Finance',
            'url': '#',
            'published_date': time.strftime('%Y-%m-%d'),
            'category': 'Banking & Finance',
            'what_happened': 'The Reserve Bank of India has decided to keep the benchmark repo rate unchanged.',
            'why_it_happened': 'The decision aims to balance inflation control with supporting ongoing economic growth.',
            'possible_impact': 'EMI for home and auto loans will remain stable, providing relief to borrowers.',
            'sentiment': 'Neutral'
        },
        {
            'title': 'Tech Startups See Resurgence in Funding',
            'description': 'After a brief funding winter, the startup ecosystem is bouncing back.',
            'source': 'Sample Tech',
            'url': '#',
            'published_date': time.strftime('%Y-%m-%d'),
            'category': 'Technology & Startups',
            'what_happened': 'Indian technology startups have witnessed a 20% increase in venture capital funding.',
            'why_it_happened': 'Investors are showing renewed confidence in AI-driven platforms.',
            'possible_impact': 'This will spur innovation, lead to new tech jobs, and help startups scale globally.',
            'sentiment': 'Positive'
        }
    ]


# --- TRANSLATION UTILITIES ---

@st.cache_data(show_spinner=False, max_entries=2000, ttl=3600)
def translate_text(text: str, target_lang: str) -> str:
    """Translates text dynamically using Google Translate's free GTX endpoint."""
    if not text or not isinstance(text, str) or target_lang == 'English':
        return text
        
    lang_map = {'Hindi': 'hi', 'Telugu': 'te'}
    tl = lang_map.get(target_lang)
    if not tl:
        return text
        
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "en",
        "tl": tl,
        "dt": "t",
        "q": text
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            translated = "".join([segment[0] for segment in data[0] if segment[0]])
            return translated
    except Exception:
        pass
        
    return text

def translate_article(article: dict, target_lang: str) -> dict:
    """Translates an entire article dictionary into the target language."""
    if target_lang == 'English':
        return article
    translated = article.copy()
    fields = ['title', 'description', 'what_happened', 'why_it_happened', 'possible_impact', 'category', 'sentiment']
    for field in fields:
        if translated.get(field):
            translated[field] = translate_text(translated[field], target_lang)
    return translated

def translate_articles_list(articles: list, target_lang: str) -> list:
    """Translates a list of articles concurrently for maximum speed."""
    if target_lang == 'English' or not articles:
        return articles
        
    try:
        from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
        ctx = get_script_run_ctx()
    except ImportError:
        ctx = None
        
    def process_article(a):
        if ctx:
            try:
                import threading
                add_script_run_ctx(threading.current_thread(), ctx)
            except Exception:
                pass
        return translate_article(a, target_lang)
        
    with ThreadPoolExecutor(max_workers=10) as executor:
        return list(executor.map(process_article, articles))