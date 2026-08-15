import json
import re

from google import genai

from config.settings import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    is_gemini_configured,
)


class GeminiService:
    """
    Central Gemini service for Lumina Recruit.

    All AI agents should communicate with Gemini
    through this service.
    """

    def __init__(self):

        if not is_gemini_configured():

            raise RuntimeError(
                "Gemini is not configured. "
                "Add GEMINI_API_KEY to the project's .env file."
            )

        try:

            self.client = genai.Client(
                api_key=GEMINI_API_KEY
            )

        except Exception as exc:

            raise RuntimeError(
                f"Failed to initialize Gemini: {exc}"
            ) from exc

        self.model = GEMINI_MODEL

    # ========================================================
    # BASIC TEXT GENERATION
    # ========================================================

    def generate(
        self,
        prompt: str,
    ) -> str:

        if not prompt or not prompt.strip():

            raise ValueError(
                "Gemini prompt cannot be empty."
            )

        try:

            response = self.client.models.generate_content(

                model=self.model,

                contents=prompt,
            )

        except Exception as exc:

            raise RuntimeError(
                f"Gemini API request failed: {exc}"
            ) from exc

        text = getattr(
            response,
            "text",
            None
        )

        if not text:

            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return text.strip()

    # ========================================================
    # JSON GENERATION
    # ========================================================

    def generate_json(
        self,
        prompt: str,
    ):

        response_text = self.generate(
            prompt
        )

        return self._extract_json(
            response_text
        )

    # ========================================================
    # JSON EXTRACTION
    # ========================================================

    @staticmethod
    def _extract_json(
        text: str
    ):

        cleaned = text.strip()

        # ----------------------------------------------------
        # Remove Markdown code fences
        # ----------------------------------------------------

        cleaned = re.sub(
            r"^```(?:json)?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"\s*```$",
            "",
            cleaned,
        )

        cleaned = cleaned.strip()

        # ----------------------------------------------------
        # Direct JSON
        # ----------------------------------------------------

        try:

            return json.loads(
                cleaned
            )

        except json.JSONDecodeError:
            pass

        # ----------------------------------------------------
        # Find JSON object
        # ----------------------------------------------------

        object_match = re.search(
            r"\{.*\}",
            cleaned,
            re.DOTALL,
        )

        if object_match:

            try:

                return json.loads(
                    object_match.group(0)
                )

            except json.JSONDecodeError:
                pass

        # ----------------------------------------------------
        # Find JSON array
        # ----------------------------------------------------

        array_match = re.search(
            r"\[.*\]",
            cleaned,
            re.DOTALL,
        )

        if array_match:

            try:

                return json.loads(
                    array_match.group(0)
                )

            except json.JSONDecodeError:
                pass

        raise ValueError(
            "Gemini did not return valid JSON.\n\n"
            f"Response:\n{cleaned}"
        )


# ============================================================
# SINGLETON HELPER
# ============================================================

def get_llm_service():

    return GeminiService()