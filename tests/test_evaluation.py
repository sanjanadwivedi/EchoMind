from unittest.mock import MagicMock, patch
import pytest

from app.services.evaluation.eval_service import RAGEvaluator


@pytest.fixture
def evaluator():
    return RAGEvaluator()


def test_context_precision_perfect_match(evaluator):
    mock_memory = MagicMock()
    mock_memory.summary = "Player drinks espresso and loves dark roast"
    retrieved = [{"memory": mock_memory}]
    expected = ["espresso", "dark roast"]

    precision = evaluator.evaluate_context_precision(retrieved, expected)
    assert precision == 1.0


def test_context_precision_partial_match(evaluator):
    mock_memory = MagicMock()
    mock_memory.summary = "Player owns a black cat named Luna"
    retrieved = [{"memory": mock_memory}]
    expected = ["Luna", "espresso"]

    precision = evaluator.evaluate_context_precision(retrieved, expected)
    assert precision == 0.5


def test_context_precision_empty_memories(evaluator):
    precision = evaluator.evaluate_context_precision([], ["espresso"])
    assert precision == 0.0


@patch("app.services.evaluation.eval_service.client.chat.completions.create")
def test_groundedness_evaluation(mock_openai, evaluator):
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content='{"groundedness_score": 0.9, "reasoning": "Fully backed by memories"}'))
    ]
    mock_openai.return_value = mock_response

    result = evaluator.evaluate_groundedness(
        response_text="I remember you enjoy espresso!",
        retrieved_memories=[{"memory": MagicMock(summary="Player loves espresso")}],
    )

    assert result["score"] == 0.9
    assert "Fully backed" in result["reasoning"]


@patch("app.services.evaluation.eval_service.client.chat.completions.create")
def test_persona_consistency_evaluation(mock_openai, evaluator):
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content='{"persona_score": 0.95, "reasoning": "Wise and guarded tone"}'))
    ]
    mock_openai.return_value = mock_response

    result = evaluator.evaluate_persona_consistency(
        response_text="The ancient ruins hold many secrets, traveler.",
        npc_personality="Wise, mysterious elder mage.",
    )

    assert result["score"] == 0.95
    assert "Wise" in result["reasoning"]
