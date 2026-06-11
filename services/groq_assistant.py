"""
DEPRECATED: This module has been replaced by services/gemini_assistant.py

The project has migrated from Groq API to Google Gemini API.
Use GeminiAssistant from services.gemini_assistant instead.

Example:
    from services.gemini_assistant import GeminiAssistant
    assistant = GeminiAssistant()
    answer = assistant.generate_answer(question, articles)
"""

raise ImportError(
    "GroqAssistant has been deprecated. "
    "Please use GeminiAssistant from services.gemini_assistant instead. "
    "Update your imports to: from services.gemini_assistant import GeminiAssistant"
)
