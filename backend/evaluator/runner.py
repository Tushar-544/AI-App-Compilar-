"""Evaluation runner — runs all 20 prompts and tracks metrics."""
import time, json, logging
from typing import List, Dict, Any
from evaluator.dataset import ALL_PROMPTS
from pipeline.orchestrator import run_pipeline

logger = logging.getLogger(__name__)


def run_single(prompt_item: Dict[str, Any]) -> Dict[str, Any]:
    t0 = time.time()
    result = {
        "id": prompt_item["id"],
        "label": prompt_item["label"],
        "prompt": prompt_item["prompt"][:120] + "..." if len(prompt_item["prompt"]) > 120 else prompt_item["prompt"],
        "success": False,
        "stages_completed": 0,
        "retries": 0,
        "failure_type": None,
        "latency_ms": 0,
        "cost_usd": 0.0,
        "repair_actions": [],
        "validation_issues": 0,
        "assumptions": [],
    }

    try:
        events = []
        gen = run_pipeline(prompt_item["prompt"])
        try:
            while True:
                events.append(next(gen))
        except StopIteration as e:
            config = e.value
        result["success"] = True
        result["stages_completed"] = len([e for e in events if e["status"] == "done"])
        result["retries"] = config.metadata.total_retries
        result["latency_ms"] = config.metadata.total_latency_ms
        result["cost_usd"] = config.metadata.cost_estimate_usd
        result["repair_actions"] = config.metadata.repair_actions
        result["validation_issues"] = len(config.metadata.validation_issues)
        result["assumptions"] = config.metadata.assumptions
    except Exception as e:
        result["failure_type"] = str(e)[:200]
        result["latency_ms"] = int((time.time() - t0) * 1000)
        logger.error(f"Eval failed for {prompt_item['id']}: {e}")

    return result


def run_all(prompt_ids: List[str] = None) -> Dict[str, Any]:
    """Run evaluation. If prompt_ids given, run only those."""
    prompts = ALL_PROMPTS
    if prompt_ids:
        prompts = [p for p in ALL_PROMPTS if p["id"] in prompt_ids]

    results = []
    for i, p in enumerate(prompts):
        logger.info(f"Running eval {i+1}/{len(prompts)}: {p['id']}")
        r = run_single(p)
        results.append(r)

    # Aggregate metrics
    success_count = sum(1 for r in results if r["success"])
    total = len(results)

    summary = {
        "total": total,
        "success": success_count,
        "failed": total - success_count,
        "success_rate": round(success_count / total * 100, 1) if total else 0,
        "avg_latency_ms": round(sum(r["latency_ms"] for r in results) / total) if total else 0,
        "avg_cost_usd": round(sum(r["cost_usd"] for r in results) / total, 5) if total else 0,
        "total_cost_usd": round(sum(r["cost_usd"] for r in results), 4),
        "total_repairs": sum(len(r["repair_actions"]) for r in results),
        "total_retries": sum(r["retries"] for r in results),
    }

    return {"summary": summary, "results": results}
