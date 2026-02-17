import google.generativeai as genai
from typing import List, Dict
from backend.config import settings

# Configure Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)

class LLMService:
    def __init__(self, model_name: str = settings.LLM_MODEL):
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
        # Store for session-specific context
        # session_id: [{"chunks": [str], "embeddings": [list]}]
        self.session_context_store: Dict[str, List[Dict]] = {}

    def add_session_document(self, session_id: str, chunks: List[str], embeddings: List[List[float]], metadata: List[Dict] = None):
        """
        Adds a document's chunks and embeddings to a specific session's temporary store.
        """
        if session_id not in self.session_context_store:
            self.session_context_store[session_id] = []
        
        self.session_context_store[session_id].append({
            "chunks": chunks,
            "embeddings": embeddings,
            "metadata": metadata or []
        })

    def get_session_context(self, session_id: str) -> List[Dict]:
        """
        Retrieves all temporary documents for a session.
        """
        return self.session_context_store.get(session_id, [])

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
You are a helpful assistant for Biesse. Use the provided context and conversation history to answer the question.

IMPORTANT INSTRUCTIONS:
1. The context may contain both "[CURRENT SESSION FILE CONTEXT]" and "[GLOBAL KNOWLEDGE BASE]".
2. If the user asks about an attached file, a profile, a resume, or "this file", PRIORITIZE the "[CURRENT SESSION FILE CONTEXT]".
3. If the user's question is about Biesse machine manuals and technical specs, use the "[GLOBAL KNOWLEDGE BASE]".
4. DO NOT hallucinate page numbers or references. ONLY cite page numbers if they are explicitly mentioned as "Page X" in the provided context for that specific document.
5. If you are answering from "[CURRENT SESSION FILE CONTEXT]" and it doesn't mention page numbers, DO NOT add any page citations.
6. If the context doesn't contain the answer, state that you don't have enough information from the provided documents.
7. DO NOT mix the contexts unless they are relevant to each other.

{history_text}

Context:
{context}

Question:
{query}

Answer:
"""

llm_service = LLMService()
