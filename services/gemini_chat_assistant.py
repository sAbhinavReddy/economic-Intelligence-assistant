import os
import time
import re
from typing import List
from dotenv import load_dotenv

try:
    import google.generativeai as gai
except Exception:
    gai = None

load_dotenv()


class GeminiChatAssistant:
    """RAG-based assistant powered by Gemini (Google) LLM for chat functionality."""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            try:
                import streamlit as st
                self.api_key = st.secrets["GEMINI_API_KEY"]
            except Exception:
                pass

        if not gai:
            raise ValueError("google-generativeai library not installed. Please run: pip install google-generativeai")

        gai.configure(api_key=self.api_key)
        
        model_name = os.getenv("CHAT_AGENT", "gemini-2.5-flash")
        
        # Strip the 'google/' prefix if the .env was configured for OpenRouter format
        if model_name.startswith("google/"):
            model_name = model_name.replace("google/", "", 1)
            
        self.model = gai.GenerativeModel(model_name)

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
            return "I couldn't find any relevant articles in the database. Please try a different question or refresh the news database."

        context = self._build_context(retrieved_articles)

        prompt = f"""You are a knowledgeable Indian economic news assistant. Your role is to explain economic concepts and answer questions accurately. You explain Indian economic and business news in simple, easy-to-understand language — as if explaining to someone with no economics background.

SYSTEM INSTRUCTIONS:
1. First, start with a clear, basic definition of any key economic terms or concepts in the question so a beginner or student can understand.
2. Then, provide a broader, easy-to-understand answer using your general knowledge. Explain WHY this matters to ordinary people (consumers, workers, students, businesses).
3. Next, include a SEPARATE SECTION titled "📰 In the News:". In this section, explain how the question or concepts relate to the provided news articles.
4. For the "In the News" section, rely ONLY on the provided articles. Cite which article(s) the information came from by mentioning the source name or title. If the articles don't relate to the question, state that briefly in this section.
5. Use simple, plain language throughout — avoid financial jargon and acronyms without explanation.

QUESTION:
{question}

RELEVANT NEWS ARTICLES:
{context}

Now, provide a clear, accurate answer following the structure above. Be concise but thorough.
IMPORTANT: You MUST write your ENTIRE response in {language}. Do not use English unless defining a specific technical term."""

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=gai.types.GenerationConfig(
                        temperature=0.3,
                        max_output_tokens=1200,
                    )
                )

                model_content = response.text

                # deterministic references
                refs = []
                for i, art in enumerate(retrieved_articles, 1):
                    title = art.get('title', 'Untitled')
                    source = art.get('source', 'Unknown')
                    matched = art.get('matched_keywords', [])
                    mk = ', '.join(matched) if matched else '(no direct keyword match)'
                    refs.append(f"{i}. {title} — {source} — matched keywords: {mk}")

                references_text = "\n\n---\n**References:**\n" + "\n".join(refs)
                return model_content + references_text

            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg and attempt < max_retries - 1:
                    match = re.search(r'retry in (\d+(?:\.\d+)?)s', error_msg)
                    sleep_time = float(match.group(1)) + 1 if match else 60
                    time.sleep(sleep_time)
                else:
                    return f"I encountered an error while generating the answer: {error_msg}. Please try again."