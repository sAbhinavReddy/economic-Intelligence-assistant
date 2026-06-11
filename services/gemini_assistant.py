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


class GeminiAssistant:
    """RAG-based assistant powered by Gemini (Google) LLM with dynamic contextual answers."""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")

        if not gai:
            raise ValueError("google-generativeai library not installed. Please run: pip install google-generativeai")

        gai.configure(api_key=self.api_key)
        self.model_name = "gemini-2.5-flash"
        self.model = gai.GenerativeModel(self.model_name)

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

    def get_assistant_welcome(self) -> str:
        return """
        🇮🇳 **Ask About India's Economy**
        
        Ask questions about recent Indian economic and business news. 
        The assistant will search through articles and explain what's happening.
        """

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

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=gai.types.GenerationConfig(
                        temperature=0.4,
                        max_output_tokens=400,
                    )
                )
                text = response.text
                if not text or not text.strip():
                    return "The AI generated an empty response. Please wait a moment and click Retry."
                return text
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg and attempt < max_retries - 1:
                    match = re.search(r'retry in (\d+(?:\.\d+)?)s', error_msg)
                    sleep_time = float(match.group(1)) + 1 if match else 60
                    time.sleep(sleep_time)
                else:
                    return f"Unable to generate summary at this time. (Error: {error_msg})"
