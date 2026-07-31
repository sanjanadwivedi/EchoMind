import json
import logging

from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)


class MemoryIntentClassifier:
    """
    Determines which categories of memories should be searched
    based on the player's latest message.
    """

    VALID_CATEGORIES = [
        "personal_fact",
        "preference",
        "relationship",
        "goal",
        "event",
        "skill",
        "location",
        "other",
    ]

    SYSTEM_PROMPT = """
You are a memory retrieval planner.

Your ONLY job is to determine which memory categories
should be searched to answer the player's question.

You DO NOT answer the player.

Return ONLY valid JSON.

Schema:

{
    "categories": [
        "preference"
    ]
}

Allowed categories:

- personal_fact
- preference
- relationship
- goal
- event
- skill
- location
- other

Rules:

1. Return one or more categories.
2. Return ONLY valid JSON.
3. Never explain your reasoning.
4. Never include markdown.
5. If unsure, return ["other"].

Examples:

Player:
What's my favorite drink?

Return:

{
    "categories": ["preference"]
}

Player:
Tell me about my pet.

Return:

{
    "categories": ["personal_fact"]
}

Player:
How did we meet?

Return:

{
    "categories": ["relationship", "event"]
}

Player:
Where do I live?

Return:

{
    "categories": ["location", "personal_fact"]
}

Player:
What are my goals?

Return:

{
    "categories": ["goal"]
}
"""

    def classify(self, message: str) -> list[str]:

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

            raw_content = response.choices[0].message.content
            data = json.loads(raw_content or "{}")

            categories = data.get("categories", [])

            result = [
                category
                for category in categories
                if category in self.VALID_CATEGORIES
            ]

            logger.debug(
                "Intent classification: message=%r -> categories=%s",
                message[:80],
                result,
            )

            return result

        except Exception:
            logger.exception("Intent classification failed")
            return ["other"]