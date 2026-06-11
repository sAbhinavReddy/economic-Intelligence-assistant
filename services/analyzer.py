import os
import json
import re
import requests
import time
from pathlib import Path

from dotenv import load_dotenv

try:
    import google.generativeai as gai
except Exception:
    gai = None

load_dotenv()


# -----------------------------
# CATEGORY DETECTION
# -----------------------------

CATEGORIES = {
    "Economy": [
        "gdp",
        "growth",
        "inflation",
        "cpi",
        "macroeconomic",
        "economic growth",
        "recession",
        "fiscal",
        "budget"
    ],
    "Banking & Finance": [
        "bank",
        "rbi",
        "loan",
        "credit",
        "npa",
        "interest rate",
        "repo rate",
        "monetary policy",
        "reserve bank",
        "banking sector"
    ],
    "Jobs & Employment": [
        "job",
        "employment",
        "unemployment",
        "hiring",
        "wages",
        "labor",
        "workforce",
        "salary"
    ],
    "Government Policies": [
        "policy",
        "government",
        "minister",
        "regulation",
        "law",
        "parliament",
        "bill",
        "announcement",
        "scheme"
    ],
    "Business & Companies": [
        "company",
        "corporate",
        "profit",
        "revenue",
        "earnings",
        "business",
        "industry",
        "enterprise"
    ],
    "Technology & Startups": [
        "tech",
        "technology",
        "startup",
        "software",
        "digital",
        "ai",
        "innovation",
        "it sector"
    ],
    "Global Events": [
        "global",
        "international",
        "trade",
        "import",
        "export",
        "tariff",
        "geopolitics",
        "world"
    ],
    "Markets": [
        "stock",
        "share",
        "market",
        "sensex",
        "nifty",
        "index",
        "bse",
        "nse",
        "share price"
    ]
}


def rule_based_analysis(article):
    text = (
        article.get("title", "") +
        " " +
        article.get("description", "")
    ).lower()

    category = "Other"

    for cat, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in text:
                category = cat
                break

    return {
        "title": article.get("title", ""),
        "source": article.get("source", ""),
        "published_date": article.get("published_at", ""),
        "category": category,
        "what_happened": "Based on " + article.get("title", ""),
        "why_it_happened": "Keyword-based detection indicates this event is categorized as " + category,
        "possible_impact": "This economic development may have implications for the Indian economy.",
        "sentiment": "Neutral"
    }



# -----------------------------
# GEMINI CLIENT
# -----------------------------

class GeminiAnalyzer:

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")

        if not gai:
            raise ValueError("google-generativeai library not installed. Please run: pip install google-generativeai")

        gai.configure(api_key=self.api_key)
        # Use a specific, fast model for the batch JSON analysis task
        self.model = gai.GenerativeModel("gemini-2.0-flash")

    def extract_json(self, text):

        try:
            return json.loads(text)

        except Exception:

            match = re.search(
                r"\{.*\}",
                text,
                re.DOTALL
            )

            if match:
                try:
                    return json.loads(
                        match.group()
                    )
                except Exception:
                    pass

        return {}

    def analyze_batch(self, articles):
        if not articles:
            return []
            
        prompt = "Analyze the following Indian economic news articles concisely. Respond with a JSON array containing exactly one analysis object per article, in the exact same order.\n\n"
        
        for i, art in enumerate(articles):
            prompt += f"--- ARTICLE {i+1} ---\n"
            prompt += f"Title: {art.get('title', '')}\n"
            prompt += f"Description: {art.get('description', '')}\n"
            prompt += f"Source: {art.get('source', '')}\n\n"
            
        prompt += """Respond with a JSON array of objects in this EXACT format (no extra text):
[
    {
        "what_happened": "One sentence explaining what happened in simple terms",
        "why_it_happened": "One or two sentences explaining why this happened",
        "possible_impact": "One or two sentences about how this might affect ordinary people or businesses",
        "sentiment": "Positive, Negative, or Neutral",
        "category": "One of: Economy, Banking & Finance, Jobs & Employment, Government Policies, Business & Companies, Technology & Startups, Global Events, Markets, Other"
    }
]"""

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=gai.types.GenerationConfig(
                        temperature=0.2,
                        max_output_tokens=4000,
                        response_mime_type="application/json"
                    )
                )
                content = response.text
                data = self.extract_json(content)
                
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return [data] # Fallback if model returns a single dict instead of array
                return []

            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg and attempt < max_retries - 1:
                    match = re.search(r'retry in (\d+(?:\.\d+)?)s', error_msg)
                    sleep_time = float(match.group(1)) + 1 if match else 60
                    print(f"Gemini API rate limit hit. Retrying in {sleep_time} seconds...")
                    time.sleep(sleep_time)
                else:
                    print(f"Gemini API batch error: {e}")
                    return []


# -----------------------------
# MAIN ANALYZER
# -----------------------------

class NewsAnalyzer:

    def __init__(self):

        self.raw_file = Path(
            "data/raw_news.json"
        )

        self.output_file = Path(
            "data/analyzed_news.json"
        )

        self.ai = GeminiAnalyzer()

    def load_articles(self):

        if not self.raw_file.exists():
            return []

        with open(
            self.raw_file,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    def save_articles(self, data):

        with open(
            self.output_file,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

    def analyze_articles(self, articles):
        """Analyze a list of raw articles directly (used by app.py)."""
        if not articles:
            print("No articles provided.")
            return
            
        # Load existing analyzed articles to avoid re-analyzing
        existing_analyzed = []
        if self.output_file.exists():
            try:
                with open(self.output_file, "r", encoding="utf-8") as f:
                    existing_analyzed = json.load(f)
            except Exception:
                pass

        existing_urls = {a.get("url") for a in existing_analyzed if a.get("url")}
        existing_titles = {a.get("title") for a in existing_analyzed if a.get("title")}

        new_articles = []
        for a in articles:
            if (a.get("url") and a.get("url") in existing_urls) or \
               (a.get("title") and a.get("title") in existing_titles):
                continue
            new_articles.append(a)

        if not new_articles:
            print("No new articles to analyze.")
            return
            
        # We can safely process more articles now via batching
        new_articles = new_articles[:30]

        analyzed = existing_analyzed
        total = len(new_articles)
        batch_size = 10

        for i in range(0, total, batch_size):
            batch = new_articles[i:i+batch_size]
            print(f"Analyzing batch {i//batch_size + 1}/{(total + batch_size - 1)//batch_size} ({len(batch)} articles)...")
            
            results = self.ai.analyze_batch(batch)
            
            for j, article in enumerate(batch):
                analysis = {}
                if results and j < len(results) and isinstance(results[j], dict):
                    analysis = results[j]
                    
                if not analysis.get("what_happened"):
                    analysis = rule_based_analysis(article)
                    
                processed_article = {
                    "title": article.get("title", ""),
                    "source": article.get("source", ""),
                    "published_date": article.get("published_at", ""),
                    "url": article.get("url", ""),
                    "category": analysis.get("category", "Other"),
                    "what_happened": analysis.get("what_happened", ""),
                    "why_it_happened": analysis.get("why_it_happened", ""),
                    "possible_impact": analysis.get("possible_impact", ""),
                    "sentiment": analysis.get("sentiment", "Neutral"),
                    "description": article.get("description", "")
                }
                analyzed.insert(0, processed_article)
                
            time.sleep(15)  # Longer pause between batches to respect Gemini rate limits

        self.save_articles(analyzed)
        print(f"\nAnalysis completed. Saved {total} new articles to {self.output_file}")

    def run(self):

        articles = self.load_articles()

        if not articles:
            print("No articles found.")
            return
            
        # Load existing analyzed articles to avoid re-analyzing
        existing_analyzed = []
        if self.output_file.exists():
            try:
                with open(self.output_file, "r", encoding="utf-8") as f:
                    existing_analyzed = json.load(f)
            except Exception:
                pass

        existing_urls = {a.get("url") for a in existing_analyzed if a.get("url")}
        existing_titles = {a.get("title") for a in existing_analyzed if a.get("title")}

        new_articles = []
        for a in articles:
            if (a.get("url") and a.get("url") in existing_urls) or \
               (a.get("title") and a.get("title") in existing_titles):
                continue
            new_articles.append(a)

        if not new_articles:
            print("No new articles to analyze.")
            return
            
        # We can safely process more articles now via batching
        new_articles = new_articles[:30]

        analyzed = existing_analyzed
        total = len(new_articles)
        batch_size = 10

        for i in range(0, total, batch_size):
            batch = new_articles[i:i+batch_size]
            print(f"Analyzing batch {i//batch_size + 1}/{(total + batch_size - 1)//batch_size} ({len(batch)} articles)...")
            
            results = self.ai.analyze_batch(batch)
            
            for j, article in enumerate(batch):
                analysis = {}
                if results and j < len(results) and isinstance(results[j], dict):
                    analysis = results[j]
                    
                if not analysis.get("what_happened"):
                    analysis = rule_based_analysis(article)
                    
                processed_article = {
                    "title": article.get("title", ""),
                    "source": article.get("source", ""),
                    "published_date": article.get("published_at", ""),
                    "url": article.get("url", ""),
                    "category": analysis.get("category", "Other"),
                    "what_happened": analysis.get("what_happened", ""),
                    "why_it_happened": analysis.get("why_it_happened", ""),
                    "possible_impact": analysis.get("possible_impact", ""),
                    "sentiment": analysis.get("sentiment", "Neutral"),
                    "description": article.get("description", "")
                }
                analyzed.insert(0, processed_article)
                
            time.sleep(15)  # Longer pause between batches to respect Gemini rate limits

        self.save_articles(analyzed)

        print("\nAnalysis completed.")
        print(f"Saved {total} new articles to {self.output_file}")


# -----------------------------
# EXECUTE
# -----------------------------

if __name__ == "__main__":

    analyzer = NewsAnalyzer()

    analyzer.run()
