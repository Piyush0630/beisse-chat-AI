import google.generativeai as genai
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

    def generate_answer(self, query: str, context: str) -> str:
        """
        Generates an answer based on the provided query and context.
        """
        prompt = f"""
You are a helpful assistant for Biesse. Use the following context to answer the user's question.
If the context doesn't contain the answer, say you don't know based on the provided documents.
Always include citations to the context if possible.

Context:
{context}

Question:
{query}

Answer:
"""
        response = self.model.generate_content(prompt)
        return response.text

llm_service = LLMService()
