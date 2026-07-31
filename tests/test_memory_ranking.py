import os
import sys
from datetime import datetime, timedelta, timezone

# Ensure backend directory is on sys.path for IDE module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from app.services.ranking.memory_ranking_service import MemoryRankingService


class FakeMemory:
    """Minimal mock that mimics the Memory ORM model for ranking tests."""

    def __init__(self, importance=0.5, created_at=None):
        self.importance = importance
        self.created_at = created_at or datetime.now(timezone.utc)
        self.category = "personal_fact"
        self.summary = "test memory"


class TestSimilarityScore:
    def test_zero_distance_gives_max_similarity(self):
        service = MemoryRankingService()
        assert service._similarity_score(0.0) == 1.0

    def test_one_distance_gives_zero_similarity(self):
        service = MemoryRankingService()
        assert service._similarity_score(1.0) == 0.0

    def test_negative_score_clamped_to_zero(self):
        service = MemoryRankingService()
        assert service._similarity_score(1.5) == 0.0

    def test_half_distance(self):
        service = MemoryRankingService()
        assert service._similarity_score(0.5) == 0.5


class TestRecencyScore:
    def test_today_returns_one(self):
        service = MemoryRankingService()
        now = datetime.now(timezone.utc)
        assert service._recency_score(now) == 1.0

    def test_three_days_ago(self):
        service = MemoryRankingService()
        three_days = datetime.now(timezone.utc) - timedelta(days=3)
        assert service._recency_score(three_days) == 0.9

    def test_two_weeks_ago(self):
        service = MemoryRankingService()
        two_weeks = datetime.now(timezone.utc) - timedelta(days=14)
        assert service._recency_score(two_weeks) == 0.7

    def test_two_months_ago(self):
        service = MemoryRankingService()
        two_months = datetime.now(timezone.utc) - timedelta(days=60)
        assert service._recency_score(two_months) == 0.5

    def test_one_year_ago(self):
        service = MemoryRankingService()
        one_year = datetime.now(timezone.utc) - timedelta(days=365)
        assert service._recency_score(one_year) == 0.3

    def test_naive_datetime_handled(self):
        """Naive (no tzinfo) timestamps should not crash."""
        service = MemoryRankingService()
        naive_now = datetime.now()
        # Should not raise
        score = service._recency_score(naive_now)
        assert 0.0 <= score <= 1.0


class TestRanking:
    def test_empty_input(self):
        service = MemoryRankingService()
        assert service.rank([]) == []

    def test_higher_importance_ranks_higher(self):
        service = MemoryRankingService()
        now = datetime.now(timezone.utc)

        items = [
            {"memory": FakeMemory(importance=0.3, created_at=now), "distance": 0.5},
            {"memory": FakeMemory(importance=0.9, created_at=now), "distance": 0.5},
        ]

        ranked = service.rank(items)
        assert ranked[0]["memory"].importance == 0.9

    def test_closer_distance_ranks_higher(self):
        service = MemoryRankingService()
        now = datetime.now(timezone.utc)

        items = [
            {"memory": FakeMemory(importance=0.5, created_at=now), "distance": 0.8},
            {"memory": FakeMemory(importance=0.5, created_at=now), "distance": 0.1},
        ]

        ranked = service.rank(items)
        assert ranked[0]["distance"] == 0.1

    def test_ranking_preserves_all_items(self):
        service = MemoryRankingService()
        now = datetime.now(timezone.utc)

        items = [
            {"memory": FakeMemory(created_at=now), "distance": 0.3},
            {"memory": FakeMemory(created_at=now), "distance": 0.5},
            {"memory": FakeMemory(created_at=now), "distance": 0.7},
        ]

        ranked = service.rank(items)
        assert len(ranked) == 3

    def test_score_key_present(self):
        service = MemoryRankingService()
        now = datetime.now(timezone.utc)

        items = [
            {"memory": FakeMemory(created_at=now), "distance": 0.3},
        ]

        ranked = service.rank(items)
        assert "score" in ranked[0]
        assert ranked[0]["score"] > 0
