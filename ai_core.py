#ai_core.py
"""
ai_core.py
-----------
Thin wrapper around Google's Generative AI (Gemini) SDK.
Centralises model configuration so the rest of the app never talks
to the SDK directly. Swap MODEL_NAME or provider here if needed.
"""
 
import os
import google.generativeai as genai
from dotenv import load_dotenv
 
load_dotenv()
 
API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-1.5-pro"
 
if not API_KEY:
    raise RuntimeError(
        "GOOGLE_API_KEY not set. Copy .env.example to .env and add your key."
    )
 
genai.configure(api_key=API_KEY)
_model = genai.GenerativeModel(MODEL_NAME)
 
 
def generate_legal_text(prompt: str) -> str:
    """
    Sends a prompt to the Generative AI model and returns clean text.
    Raises a RuntimeError with a friendly message on failure so the
    API layer can translate it into a proper HTTP error.
    """
    try:
        response = _model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,   # low temperature -> consistent legal phrasing
                "max_output_tokens": 2048,
            },
        )
        text = (response.text or "").strip()
        if not text:
            raise ValueError("Empty response from model")
        return text
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"AI generation failed: {exc}") from exc
