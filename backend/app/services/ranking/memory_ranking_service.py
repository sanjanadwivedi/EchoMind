from datetime import datetime, timezone


class MemoryRankingService:
    """
    Ranks retrieved memories before they are sent to the LLM.
    """

    SIMILARITY_WEIGHT = 0.60
    IMPORTANCE_WEIGHT = 0.25
    RECENCY_WEIGHT = 0.15

    def _similarity_score(self, distance: float) -> float:
        """
        Convert Chroma distance to similarity.
        Lower distance = higher similarity.
        """
        return max(0.0, 1.0 - distance)

    def _recency_score(self, created_at: datetime) -> float:
        """
        Recent memories receive a slightly higher score.
        Handles both timezone-aware and timezone-naive datetimes.
        """

        # Always use timezone-aware UTC
        if created_at.tzinfo is not None:
            now = datetime.now(timezone.utc)
        else:
            now = datetime.now(timezone.utc)
            created_at = created_at.replace(tzinfo=timezone.utc)

        age_days = max(0, (now - created_at).days)

        if age_days <= 1:
            return 1.0
        elif age_days <= 7:
            return 0.9
        elif age_days <= 30:
            return 0.7
        elif age_days <= 90:
            return 0.5
        else:
            return 0.3

    def rank(self, retrieved_memories):
        ranked = []

        for item in retrieved_memories:

            memory = item["memory"]

            similarity = self._similarity_score(
                item["distance"]
            )

            score = (
                similarity * self.SIMILARITY_WEIGHT
                + memory.importance * self.IMPORTANCE_WEIGHT
                + self._recency_score(memory.created_at)
                * self.RECENCY_WEIGHT
            )

            ranked.append(
                {
                    "memory": memory,
                    "distance": item["distance"],
                    "score": score,
                }
            )

        ranked.sort(
            key=lambda x: x["score"],
            reverse=True,
        )

        return ranked