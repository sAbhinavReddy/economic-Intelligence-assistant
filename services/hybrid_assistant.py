from typing import List
from services.gemini_assistant import GeminiAssistant
from services.ollama_assistant import OllamaAssistant

class HybridAssistant:
    """Tries Gemini first, falls back to Ollama if limit is exceeded or error occurs."""
    
    def __init__(self):
        self.gemini = GeminiAssistant()
        self.ollama = OllamaAssistant(model="qwen2.5:0.5b")

    def generate_answer(self, question: str, retrieved_articles: List[dict], language: str = "English") -> str:
        ans = self.gemini.generate_answer(question, retrieved_articles, language)
        
        # Check if Gemini returned its error fallback strings
        if "encountered an error" in ans or "Unable to generate" in ans:
            print("Gemini Assistant hit a limit/error. Falling back to Ollama.")
            return self.ollama.generate_answer(question, retrieved_articles, language)
            
        return ans

    def generate_daily_summary(self, articles: List[dict], language: str = "English") -> str:
        ans = self.gemini.generate_daily_summary(articles, language)
        
        # Check if Gemini returned its error fallback strings
        if "encountered an error" in ans or "Unable to generate" in ans or "empty response" in ans:
            print("Gemini Summary hit a limit/error. Falling back to Ollama.")
            return self.ollama.generate_daily_summary(articles, language)
            
        return ans