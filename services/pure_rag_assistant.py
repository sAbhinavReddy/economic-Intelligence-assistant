import requests
import re
from typing import List

class PureRAGAssistant:
    """A simple bot that returns RAG-retrieved articles directly with a built-in glossary and Wikipedia fallback."""
    
    def __init__(self):
        # A built-in mini-encyclopedia to replace the AI's general knowledge
        self.glossary = {
            "bank": "A bank is a financial institution licensed to receive deposits and make loans. Banks play a crucial role in the economy by offering services like savings accounts, wealth management, and credit.",
            "inflation": "Inflation is the rate at which prices for goods and services rise, meaning your money buys less over time.",
            "rbi": "The Reserve Bank of India (RBI) is India's central bank. It regulates the banking system and manages the money supply.",
            "gdp": "Gross Domestic Product (GDP) is the total monetary value of all finished goods and services produced within a country's borders.",
            "repo rate": "The Repo Rate is the interest rate at which the RBI lends money to commercial banks. Changes here directly affect your loan EMIs.",
            "npa": "A Non-Performing Asset (NPA) is a bank loan where the borrower has stopped making interest or principal payments for 90 days.",
            "sensex": "The Sensex is the benchmark index of the Bombay Stock Exchange (BSE), representing 30 of the largest Indian stocks.",
            "nifty": "The NIFTY 50 is a benchmark Indian stock market index representing 50 of the largest companies on the National Stock Exchange (NSE).",
            "fiscal deficit": "A fiscal deficit occurs when a government's total expenditures exceed the revenue it generates (excluding borrowed money).",
            "fdi": "Foreign Direct Investment (FDI) is an investment made by a firm or individual in one country into business interests located in another country."
        }
        
    def _fetch_wikipedia_info(self, question: str) -> str:
        # Remove common words to isolate the core subjects
        stopwords = {
            'what', 'is', 'a', 'an', 'the', 'why', 'how', 'where', 'when', 'who', 
            'did', 'does', 'do', 'are', 'were', 'was', 'about', 'explain', 'tell', 
            'me', 'in', 'of', 'on', 'for', 'to', 'with', 'happen', 'happened', 
            'today', 'yesterday', 'recently', 'news', 'latest', 'developments', 
            'sector', 'india', 'indian', 'economy', 'economic', 'impact', 'affect'
        }
        words = [w for w in re.findall(r'\b\w+\b', question.lower()) if w not in stopwords and len(w) > 2]
        
        if not words:
            return ""
            
        # Try the full phrase first, then try the longest individual words
        search_terms = [" ".join(words)]
        if len(words) > 1:
            search_terms.extend(sorted(words, key=len, reverse=True))
            
        for search_term in search_terms:
            try:
                # Use Wikipedia Opensearch to find the exact article title
                search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={search_term}&limit=1&namespace=0&format=json"
                res = requests.get(search_url, timeout=3).json()
                if len(res) > 1 and res[1]:
                    best_match = res[1][0]
                    # Fetch the summary for that exact title
                    summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{best_match}"
                    sum_res = requests.get(summary_url, timeout=3).json()
                    if 'extract' in sum_res:
                        return f"- **{best_match.upper()} (Source: Wikipedia)**: {sum_res['extract']}"
            except Exception:
                continue
        return ""
    
    def generate_answer(self, question: str, retrieved_articles: List[dict], language: str = "English") -> str:
        t = {
            "English": {
                "no_articles": "I couldn't find any relevant articles in the database. Please try a different question or refresh the news database.",
                "concepts": "### 📚 General Info & Concepts\n",
                "info": "### 📚 General Info\n",
                "no_def": "I couldn't find a specific dictionary definition for your query, but here is the latest context from the news!\n\n---\n\n",
                "news": "### 📰 In the News\nHere are the most relevant news articles I found for your query:\n\n",
                "source": "**Source:**",
                "highlight": "**Key Highlight:**",
                "no_desc": "No description available.",
                "note": "---\n*Note: This response was generated directly from a local glossary and database search without generative AI.*"
            },
            "Hindi": {
                "no_articles": "मुझे डेटाबेस में कोई प्रासंगिक लेख नहीं मिला। कृपया कोई अन्य प्रश्न पूछें या समाचार डेटाबेस को ताज़ा करें।",
                "concepts": "### 📚 सामान्य जानकारी और अवधारणाएं\n",
                "info": "### 📚 सामान्य जानकारी\n",
                "no_def": "मुझे आपके प्रश्न के लिए कोई विशिष्ट शब्दकोश परिभाषा नहीं मिली, लेकिन यहाँ समाचारों का नवीनतम संदर्भ दिया गया है!\n\n---\n\n",
                "news": "### 📰 समाचार में\nयहाँ मुझे आपके प्रश्न के लिए सबसे प्रासंगिक समाचार लेख मिले हैं:\n\n",
                "source": "**स्रोत:**",
                "highlight": "**मुख्य अंश:**",
                "no_desc": "कोई विवरण उपलब्ध नहीं है।",
                "note": "---\n*नोट: यह प्रतिक्रिया बिना जनरेटिव AI के सीधे स्थानीय शब्दावली और डेटाबेस खोज से उत्पन्न की गई थी।*"
            },
            "Telugu": {
                "no_articles": "డేటాబేస్‌లో నాకు సంబంధిత కథనాలు ఏవీ దొరకలేదు. దయచేసి వేరే ప్రశ్న అడగండి లేదా వార్తల డేటాబేస్‌ను రిఫ్రెష్ చేయండి.",
                "concepts": "### 📚 సాధారణ సమాచారం & భావనలు\n",
                "info": "### 📚 సాధారణ సమాచారం\n",
                "no_def": "మీ ప్రశ్నకు నాకు నిర్దిష్ట నిఘంటువు నిర్వచనం దొరకలేదు, కానీ ఇక్కడ వార్తల నుండి తాజా సందర్భం ఉంది!\n\n---\n\n",
                "news": "### 📰 వార్తలలో\nమీ ప్రశ్న కోసం నాకు దొరికిన అత్యంత సంబంధిత వార్తా కథనాలు ఇక్కడ ఉన్నాయి:\n\n",
                "source": "**మూలం:**",
                "highlight": "**ముఖ్య అంశం:**",
                "no_desc": "వివరణ ఏదీ అందుబాటులో లేదు.",
                "note": "---\n*గమనిక: ఈ ప్రతిస్పందన ఉత్పాదక AI లేకుండా నేరుగా స్థానిక పదకోశం మరియు డేటాబేస్ శోధన నుండి రూపొందించబడింది.*"
            }
        }
        
        lang_dict = t.get(language, t["English"])

        if not retrieved_articles:
            return lang_dict["no_articles"]

        response = ""
        
        # 1. Provide Theory/Definitions
        found_terms = []
        q_lower = question.lower()
        for term, definition in self.glossary.items():
            if term in q_lower:
                found_terms.append(f"- **{term.upper()}**: {definition}")
                
        # If no local terms found, try Wikipedia dynamically
        if not found_terms:
            wiki_info = self._fetch_wikipedia_info(question)
            if wiki_info:
                found_terms.append(wiki_info)
                
        if found_terms:
            response += lang_dict["concepts"]
            response += "\n".join(found_terms) + "\n\n---\n\n"
        else:
            response += lang_dict["info"]
            response += lang_dict["no_def"]

        # 2. Provide the News Context
        response += lang_dict["news"]
        
        for i, article in enumerate(retrieved_articles, 1):
            title = article.get('title', 'Untitled')
            source = article.get('source', 'Unknown')
            summary = article.get('what_happened') or article.get('description') or lang_dict["no_desc"]
            url = article.get('url', '#')
            
            if language != 'English':
                from services.utils import translate_text
                title = translate_text(title, language)
                summary = translate_text(summary, language)
            
            response += f"#### {i}. [{title}]({url})\n"
            response += f"{lang_dict['source']} {source}\n"
            response += f"{lang_dict['highlight']} {summary}\n\n"
            
        response += lang_dict["note"]
        
        return response