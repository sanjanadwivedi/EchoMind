import logging

from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)


class MemoryReflectionService:

    SYSTEM_PROMPT = """
You summarize multiple memories into one higher-level long-term memory.

Rules:

- Merge related memories only.
- Do not invent facts.
- Preserve important information.
- Produce ONE concise summary.
- Return only the summary.
"""

    def reflect(self, memories):

        if len(memories) == 0:
            return None

        text = "\n".join(
            f"- {memory.summary}"
            for memory in memories
        )

        try:
            response = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": text,
                    },
                ],
            )

            content = response.choices[0].message.content
            result = (content or "").strip()
            logger.info(
                "Reflection generated from %d memories", len(memories)
            )
            return result

        except Exception:
            logger.exception("OpenAI API call failed during reflection")
            raise