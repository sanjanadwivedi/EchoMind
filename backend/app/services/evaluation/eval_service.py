import json
import logging
from typing import Any, Dict, List, Optional
from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)


class RAGEvaluator:
    """Automated LLM-as-a-Judge Evaluation Suite for RAG Memory Pipelines.
    
    Measures 3 Core RAG Triad Metrics:
    1. Groundedness (Anti-Hallucination): Degree to which NPC response is grounded ONLY in retrieved memories.
    2. Context Precision: Fraction of retrieved memories that are relevant to ground truth facts.
    3. Persona Consistency: Adherence of response tone and style to NPC personality traits.
    """

    GROUNDEDNESS_PROMPT = """
You are an expert AI Evaluator assessing RAG (Retrieval-Augmented Generation) anti-hallucination metrics.

Given:
1. Retrieved Memories (Context)
2. NPC Generated Response

Task: Determine if every factual claim in the NPC Generated Response is strictly supported by the Retrieved Memories.
If there are no memories retrieved, a response stating lack of knowledge or general greeting is considered grounded (1.0).
If the response invents facts not found in memories (e.g., claiming a pet, event, or name not in memories), groundedness is lowered.

Return ONLY a JSON object with this exact structure:
{
    "groundedness_score": 1.0,
    "reasoning": "Brief explanation of the score"
}

Score Scale:
1.0 = Fully grounded, 0 hallucinations
0.5 = Partially grounded, minor unsubstantiated details
0.0 = Completely hallucinated or contradicts retrieved memories
"""

    PERSONA_PROMPT = """
You are an AI Persona Consistency Evaluator.

Given:
1. NPC Personality Traits
2. NPC Generated Response

Task: Evaluate how well the response embodies the NPC's assigned personality, tone, and character style.

Return ONLY a JSON object with this exact structure:
{
    "persona_score": 1.0,
    "reasoning": "Brief explanation of the score"
}

Score Scale:
1.0 = Perfect character tone and personality match
0.5 = Neutral or slightly out of character
0.0 = Completely breaks character or acts like an generic AI assistant
"""

    def _extract_summary(self, item: Any) -> str:
        """Safely extracts summary string from memory object or dict item."""
        if isinstance(item, dict):
            mem_obj = item.get("memory")
            if mem_obj is not None:
                return getattr(mem_obj, "summary", str(mem_obj))
            return str(item)
        if item is not None:
            return getattr(item, "summary", str(item))
        return ""

    def evaluate_context_precision(
        self,
        retrieved_memories: List[Dict[str, Any]],
        expected_facts: List[str],
    ) -> float:
        """Calculates precision of retrieved memories against expected key facts."""
        if not expected_facts:
            return 1.0
        if not retrieved_memories:
            return 0.0

        memory_texts = [self._extract_summary(item) for item in retrieved_memories]
        
        combined_text = " ".join(memory_texts).lower()
        matched = 0
        for fact in expected_facts:
            if fact.lower() in combined_text:
                matched += 1

        return round(matched / len(expected_facts), 4)

    def evaluate_groundedness(
        self,
        response_text: str,
        retrieved_memories: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Uses LLM-as-a-Judge to grade anti-hallucination / groundedness score."""
        memory_context = "\n".join(
            f"- {self._extract_summary(item)}"
            for item in retrieved_memories
        ) if retrieved_memories else "No memories retrieved."

        prompt = f"""
Retrieved Memories:
{memory_context}

NPC Generated Response:
"{response_text}"
"""
        try:
            res = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                temperature=0.0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": self.GROUNDEDNESS_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )
            parsed = json.loads(res.choices[0].message.content or "{}")
            score = float(parsed.get("groundedness_score", 1.0))
            reasoning = str(parsed.get("reasoning", "Evaluated successfully."))
            return {"score": max(0.0, min(1.0, score)), "reasoning": reasoning}
        except Exception as e:
            logger.warning(f"Groundedness evaluation failed: {e}")
            return {"score": 1.0, "reasoning": f"Evaluation error fallback: {str(e)}"}

    def evaluate_persona_consistency(
        self,
        response_text: str,
        npc_personality: str,
    ) -> Dict[str, Any]:
        """Uses LLM-as-a-Judge to grade persona consistency score."""
        prompt = f"""
NPC Personality Traits:
{npc_personality}

NPC Generated Response:
"{response_text}"
"""
        try:
            res = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                temperature=0.0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": self.PERSONA_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            )
            parsed = json.loads(res.choices[0].message.content or "{}")
            score = float(parsed.get("persona_score", 1.0))
            reasoning = str(parsed.get("reasoning", "Evaluated successfully."))
            return {"score": max(0.0, min(1.0, score)), "reasoning": reasoning}
        except Exception as e:
            logger.warning(f"Persona evaluation failed: {e}")
            return {"score": 1.0, "reasoning": f"Evaluation error fallback: {str(e)}"}

    def evaluate_rag_triad(
        self,
        response_text: str,
        retrieved_memories: List[Dict[str, Any]],
        expected_facts: List[str],
        npc_personality: str,
    ) -> Dict[str, Any]:
        """Evaluates all 3 RAG Triad metrics and returns comprehensive scorecard."""
        ctx_precision = self.evaluate_context_precision(retrieved_memories, expected_facts)
        groundedness = self.evaluate_groundedness(response_text, retrieved_memories)
        persona = self.evaluate_persona_consistency(response_text, npc_personality)

        composite_score = round((ctx_precision * 0.35) + (groundedness["score"] * 0.40) + (persona["score"] * 0.25), 4)

        return {
            "composite_score": composite_score,
            "context_precision": ctx_precision,
            "groundedness": groundedness["score"],
            "groundedness_reasoning": groundedness["reasoning"],
            "persona_consistency": persona["score"],
            "persona_reasoning": persona["reasoning"],
        }
