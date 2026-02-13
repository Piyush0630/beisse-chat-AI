import google.generativeai as genai
from typing import List, Dict
from backend.config import settings

# Configure Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)

class LLMService:
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        self.model_name = model_name
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": 0.3,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
        )

    def generate_answer(self, query: str, context: str, history: List[Dict[str, str]] = None) -> str:
        """
        Generates an answer based on the provided query, context, and conversation history.
        """
        prompt = self._build_prompt(query, context, history)
        response = self.model.generate_content(prompt)
        return response.text

    def generate_answer_stream(self, query: str, context: str, history: List[Dict[str, str]] = None):
        """
        Generates a streaming answer based on the provided query, context, and conversation history.
        """
        prompt = self._build_prompt(query, context, history)
        response = self.model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text

    def _build_prompt(self, query: str, context: str, history: List[Dict[str, str]] = None) -> str:
        history_text = ""
        if history:
            history_text = "\nConversation History:\n"
            for msg in history:
                role = "User" if msg["role"] == "user" else "Assistant"
                history_text += f"{role}: {msg['content']}\n"

        return f"""
You are a helpful assistant for Biesse. Use the following context and conversation history to answer the user's question.
If the context doesn't contain the answer, say you don't know based on the provided documents.
Always include citations to the context if possible.

{history_text}

Context:
{context}

Question:
{query}

Answer:
"""

llm_service = LLMService()
