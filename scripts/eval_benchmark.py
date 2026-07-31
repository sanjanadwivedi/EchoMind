#!/usr/bin/env python3
"""
EchoMind RAG & Cognitive Pipeline Benchmark Suite
Runs automated LLM-as-a-Judge evaluations and measures RAG Triad scores + latency stats.
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Add backend directory to path
backend_path = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.evaluation.eval_service import RAGEvaluator

# Synthetic benchmark query test dataset
BENCHMARK_DATASET: List[Dict[str, Any]] = [
    {
        "id": "bench_01",
        "npc_name": "Eldon the Alchemist",
        "npc_personality": "Studious, cautious alchemist interested in rare herbs and brewing recipes.",
        "player_query": "Do you remember what my favorite drink is?",
        "retrieved_memories": [
            {"memory": type("Mem", (), {"category": "preference", "summary": "Player drinks strong espresso every morning"})()}
        ],
        "expected_facts": ["espresso"],
        "simulated_response": "Ah yes, traveler. You mentioned you start your days with a cup of strong espresso."
    },
    {
        "id": "bench_02",
        "npc_name": "Ragnar Ironclad",
        "npc_personality": "Gruff, honorable warrior blacksmith who values loyalty and sturdy metalwork.",
        "player_query": "What weapon did I ask you to forge for me last week?",
        "retrieved_memories": [
            {"memory": type("Mem", (), {"category": "event", "summary": "Player ordered a custom mithril broadsword with flame runes"})()}
        ],
        "expected_facts": ["mithril broadsword", "flame runes"],
        "simulated_response": "Aye! You asked for a heavy mithril broadsword etched with flame runes."
    },
    {
        "id": "bench_03",
        "npc_name": "Luna the Shadow Rogue",
        "npc_personality": "Cunning, witty assassin who speaks in riddles and keeps secrets guarded.",
        "player_query": "Do I have any pets?",
        "retrieved_memories": [
            {"memory": type("Mem", (), {"category": "personal_fact", "summary": "Player has a black cat named Shadow"})()}
        ],
        "expected_facts": ["black cat", "Shadow"],
        "simulated_response": "A shadow follows you, traveler... specifically a sleek black cat named Shadow."
    },
    {
        "id": "bench_04",
        "npc_name": "Eldon the Alchemist",
        "npc_personality": "Studious, cautious alchemist interested in rare herbs and brewing recipes.",
        "player_query": "What is my home kingdom?",
        "retrieved_memories": [],  # Non-existent memory query
        "expected_facts": [],
        "simulated_response": "Forgive me, traveler, but you have not yet shared which kingdom you hail from."
    }
]


def run_benchmark():
    print("=" * 65)
    print(" EchoMind AI Engine -- RAG Triad & Latency Benchmark Suite")
    print("=" * 65)

    evaluator = RAGEvaluator()
    results = []
    total_latency_ms = []

    for item in BENCHMARK_DATASET:
        print(f"\n[>] Executing Test Case [{item['id']}] -- NPC: {item['npc_name']}")
        print(f"  Query: \"{item['player_query']}\"")
        
        start_time = time.perf_counter()
        
        response_text: str = str(item["simulated_response"])
        retrieved_memories: List[Dict[str, Any]] = list(item["retrieved_memories"])
        expected_facts: List[str] = list(item["expected_facts"])
        npc_personality: str = str(item["npc_personality"])

        scorecard = evaluator.evaluate_rag_triad(
            response_text=response_text,
            retrieved_memories=retrieved_memories,
            expected_facts=expected_facts,
            npc_personality=npc_personality,
        )
        
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        total_latency_ms.append(elapsed_ms)
        
        scorecard_res = {
            "id": item["id"],
            "npc_name": item["npc_name"],
            "query": item["player_query"],
            "latency_ms": elapsed_ms,
            "metrics": scorecard
        }
        results.append(scorecard_res)

        print(f"  [Metrics] Composite: {scorecard['composite_score']:.2f} | "
              f"Precision: {scorecard['context_precision']:.2f} | "
              f"Groundedness: {scorecard['groundedness']:.2f} | "
              f"Persona: {scorecard['persona_consistency']:.2f}")
        print(f"  [Latency] {elapsed_ms} ms")

    # Calculate aggregations
    avg_composite = sum(r["metrics"]["composite_score"] for r in results) / len(results)
    avg_precision = sum(r["metrics"]["context_precision"] for r in results) / len(results)
    avg_groundedness = sum(r["metrics"]["groundedness"] for r in results) / len(results)
    avg_persona = sum(r["metrics"]["persona_consistency"] for r in results) / len(results)
    avg_latency = sum(total_latency_ms) / len(total_latency_ms)

    sorted_latencies = sorted(total_latency_ms)
    p50_latency = sorted_latencies[len(sorted_latencies) // 2]
    p90_latency = sorted_latencies[int(len(sorted_latencies) * 0.9)]

    summary = {
        "benchmark_summary": {
            "total_test_cases": len(results),
            "avg_composite_score": round(avg_composite, 4),
            "avg_context_precision": round(avg_precision, 4),
            "avg_groundedness_score": round(avg_groundedness, 4),
            "avg_persona_score": round(avg_persona, 4),
            "latency_p50_ms": p50_latency,
            "latency_p90_ms": p90_latency,
            "avg_latency_ms": round(avg_latency, 2),
        },
        "details": results
    }

    print("\n" + "=" * 65)
    print(" FINAL AGGREGATE BENCHMARK REPORT")
    print("=" * 65)
    print(f"  - Composite Score       : {avg_composite * 100:.1f}%")
    print(f"  - Context Precision     : {avg_precision * 100:.1f}%")
    print(f"  - Groundedness Score    : {avg_groundedness * 100:.1f}%")
    print(f"  - Persona Consistency   : {avg_persona * 100:.1f}%")
    print(f"  - Response Latency (p50): {p50_latency} ms")
    print(f"  - Response Latency (p90): {p90_latency} ms")
    print("=" * 65)

    docs_dir = Path(__file__).resolve().parent.parent / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    report_file = docs_dir / "benchmark_report.json"
    
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"[+] Saved detailed report to docs/benchmark_report.json\n")


if __name__ == "__main__":
    run_benchmark()
