import json
import logging

from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)


class MemoryExtractor:

    SYSTEM_PROMPT = """
You are a memory extraction engine for an AI NPC.

Your task is to determine whether the PLAYER'S LATEST MESSAGE contains NEW long-term information worth remembering.

Return ONLY valid JSON.

Schema:

{
    "should_store": true,
    "summary": "...",
    "category": "...",
    "event_type": "...",
    "emotion": "...",
    "importance": 0.0,
    "confidence": 0.0,
    "reason": "..."
}

Allowed categories (choose EXACTLY one):

- personal_fact
- preference
- relationship
- goal
- event
- skill
- location
- other

Rules:

1. Analyze ONLY the PLAYER'S LATEST MESSAGE.
2. Never use the NPC's response.
3. Never combine multiple memories.
4. Never invent information.
5. Never infer facts that were not explicitly stated.
6. Store exactly ONE memory.
7. The summary should describe exactly ONE persistent fact.
8. If the player is only asking a question, recalling an old memory, greeting, or making small talk:
   - should_store = false
   - summary = ""
   - category = "other"
   - event_type = ""
   - emotion = "neutral"
   - importance = 0
   - confidence = 1
   - reason = "Recall question"

Examples:

Player:
"My turtle is named Pixel."

Return:

{
  "should_store": true,
  "summary": "Player's pet turtle is named Pixel.",
  "category": "personal_fact",
  "event_type": "conversation",
  "emotion": "neutral",
  "importance": 0.7,
  "confidence": 1.0,
  "reason": "New persistent personal fact"
}

Player:
"I love coffee."

Return:

{
  "should_store": true,
  "summary": "Player likes coffee.",
  "category": "preference",
  "event_type": "conversation",
  "emotion": "joy",
  "importance": 0.6,
  "confidence": 1.0,
  "reason": "New personal preference"
}

Player:
"What is my turtle's name?"

Return:

{
  "should_store": false,
  "summary": "",
  "category": "other",
  "event_type": "",
  "emotion": "neutral",
  "importance": 0,
  "confidence": 1,
  "reason": "Recall question"
}
"""

    def extract(self, message: str) -> dict:
        """
        Extract a memory from the player's message.

        Returns a parsed dict (not raw JSON string) with keys:
        should_store, summary, category, event_type, emotion,
        importance, confidence, reason.
        """
        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": message,
                    },
                ],
            )

            raw = response.choices[0].message.content
            return json.loads(raw or "{}")

        except json.JSONDecodeError:
            logger.exception("Failed to parse memory extractor JSON response")
            return {"should_store": False}

        except Exception:
            logger.exception("OpenAI API call failed during memory extraction")
            return {"should_store": False}