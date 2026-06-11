import os
import time
import requests
from typing import List
from dotenv import load_dotenv

load_dotenv()


class OpenRouterSummaryGenerator:
    """Generates daily summaries using OpenRouter API."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            try:
                import streamlit as st
                self.api_key = st.secrets["OPENROUTER_API_KEY"]
            except Exception:
                pass
                
        self.api_url = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1/chat/completions")
        self.model_name = os.getenv("SUMMARY_AGENT", os.getenv("OPENROUTER_MODEL_NAME", "google/gemma-2-9b-it:free"))
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found. Please add it to your .env file or Streamlit secrets.")

    def _build_context(self, articles: List[dict]) -> str:
        context_parts = []
        for i, article in enumerate(articles, 1):
            what_happened = article.get('what_happened', '') or ''
            why_it_happened = article.get('why_it_happened', '') or ''
            possible_impact = article.get('possible_impact', '') or ''
            desc = article.get('description', '') or ''

            part = f"""Article {i}:
Title: {article.get('title', 'Untitled')}
Source: {article.get('source', 'Unknown')}
Category: {article.get('category', 'Unknown')}
Published: {article.get('published_date', 'Unknown')}
Description: {desc}
What Happened: {what_happened}
Why It Happened: {why_it_happened}
Possible Impact: {possible_impact}
"""
            context_parts.append(part)

        return "\n".join(context_parts)

    def generate_daily_summary(self, articles: List[dict], language: str = "English") -> str:
        if not articles:
            return "No articles available to summarize."

        context = self._build_context(articles[:10])
        prompt = f"""You are a helpful AI assistant that summarizes Indian economic news in simple language.

Here are today's economic news articles:

{context}

TASK: Generate a summary titled "Today's Economy in 30 Seconds".
It MUST contain EXACTLY 5 bullet points covering the most important events that actually matter to ordinary people. Make sure to write out all 5 bullet points completely. Do not stop midway.

IMPORTANT: You MUST write your ENTIRE response in {language}.
"""

        max_retries = 3
        for attempt in range(max_retries):
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                }
                
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
                
                if response.status_code != 200:
                    raise Exception(f"API Error {response.status_code}: {response.text}")
                
                try:
                    data = response.json()
                except Exception:
                    raise Exception(f"Expected JSON but got: {response.text[:150]}...")
                # Attempt to extract text from a standard OpenAI-compatible format, with a fallback
                text = data.get("choices", [{}])[0].get("message", {}).get("content", "") or data.get("response", "")
                
                if not text or not text.strip():
                    return "The AI generated an empty response. Please wait a moment and click Retry."
                return text
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    return f"Unable to generate summary at this time. (Error: {str(e)})"