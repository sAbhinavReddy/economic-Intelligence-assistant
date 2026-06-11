import json
import os
import re
import time
from pathlib import Path


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