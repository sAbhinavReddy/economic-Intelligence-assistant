import requests
from typing import List

class OllamaAssistant:
    """RAG-based assistant powered by local Ollama LLM."""
    
    def __init__(self, model="qwen2.5:0.5b"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

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

    def generate_answer(self, question: str, retrieved_articles: List[dict], language: str = "English") -> str:
        if not retrieved_articles:
            return "I couldn't find any relevant articles in the database."

        context = self._build_context(retrieved_articles)

        prompt = f"""You are a knowledgeable Indian economic news assistant.
        
Explain Indian economic and business news in simple, easy-to-understand language.
1. Define key terms.
2. Provide a broad answer.
3. Include a "📰 In the News:" section relying ONLY on the provided articles.

QUESTION:
{question}

RELEVANT NEWS ARTICLES:
{context}

IMPORTANT: Write your ENTIRE response in {language}.
"""

        try:
            response = requests.post(self.url, json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            })
            
            model_content = response.json().get("response", "")

            # Append deterministic references at the end
            refs = []
            for i, art in enumerate(retrieved_articles, 1):
                title = art.get('title', 'Untitled')
                source = art.get('source', 'Unknown')
                refs.append(f"{i}. {title} — {source}")

            references_text = "\n\n---\n**References:**\n" + "\n".join(refs)
            return model_content + references_text
            
        except Exception as e:
            return f"I encountered an error with the local AI: {e}"

    def generate_daily_summary(self, articles: List[dict], language: str = "English") -> str:
        if not articles:
            return "No articles available to summarize."

        context = self._build_context(articles[:10])
        prompt = f"""You are a helpful AI assistant that summarizes Indian economic news in simple language.

Here are today's economic news articles:

{context}

Generate "Today's Economy in 30 Seconds" — exactly 5 bullet points covering the most important events that actually matter to ordinary people.

IMPORTANT: You MUST write your ENTIRE response in {language}.
"""

        try:
            response = requests.post(self.url, json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            })
            text = response.json().get("response", "")
            if not text or not text.strip():
                return "The AI generated an empty response. Please wait a moment and click Retry."
            return text
        except Exception as e:
            return f"Unable to generate summary at this time. (Error: {str(e)})"