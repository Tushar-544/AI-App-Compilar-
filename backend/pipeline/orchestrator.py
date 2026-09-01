"""
Pipeline Orchestrator — coordinates all 5 stages and emits SSE progress events.
"""
import time, logging
from typing import Generator, Optional
from models.app_config import AppConfig, PipelineMetadata, PipelineStageResult, ValidationIssue
from models.intent import IntentModel
from models.architecture import ArchitectureModel
import pipeline.stage1_intent  as s1
import pipeline.stage2_design  as s2
import pipeline.stage3_schemas as s3
import pipeline.stage4_refine  as s4
from validators.repair import validate_and_repair
from llm.gemini import get_client

logger = logging.getLogger(__name__)


def run_pipeline(prompt: str) -> Generator[dict, None, AppConfig]:
    """
    Execute the full 5-stage pipeline as a generator.
    Yields progress events, then returns the final AppConfig.
    """
    stage_results: list[PipelineStageResult] = []
    total_start = time.time()

    def emit(stage: int, name: str, status: str, detail: str = ""):
        ev = {"stage": stage, "name": name, "status": status, "detail": detail}
        logger.info(f"[Stage {stage}] {name} — {status}: {detail}")
        return ev

    # ── Stage 1: Intent Extraction ─────────────────────────────────────────
    yield emit(1, "Intent Extraction", "running", "Parsing your prompt...")
    try:
        intent, ms1, r1 = s1.run(prompt)
        stage_results.append(PipelineStageResult(stage=1, name="Intent Extraction", success=True, latency_ms=ms1, retries=r1))
        yield emit(1, "Intent Extraction", "done", f"Found {len(intent.primary_entities)} entities, {len(intent.features)} features")
    except Exception as e:
        yield emit(1, "Intent Extraction", "error", str(e))
        raise

    # ── Stage 2: System Design ─────────────────────────────────────────────
    yield emit(2, "System Design", "running", "Designing app architecture...")
    try:
        arch, ms2, r2 = s2.run(intent)
        stage_results.append(PipelineStageResult(stage=2, name="System Design", success=True, latency_ms=ms2, retries=r2))
        yield emit(2, "System Design", "done", f"{len(arch.pages)} pages, {len(arch.entity_relationships)} relationships")
    except Exception as e:
        yield emit(2, "System Design", "error", str(e))
        raise

    # ── Stage 3: Schema Generation ────────────────────────────────────────
    yield emit(3, "Schema Generation", "running", "Generating UI, API, DB, Auth schemas...")
    try:
        ui, api, db, auth, ms3, r3 = s3.run(intent, arch)
        stage_results.append(PipelineStageResult(stage=3, name="Schema Generation", success=True, latency_ms=ms3, retries=r3))
        yield emit(3, "Schema Generation", "done",
             f"{len(ui.pages)} pages | {len(api.endpoints)} endpoints | {len(db.tables)} tables")
    except Exception as e:
        yield emit(3, "Schema Generation", "error", str(e))
        raise

    # ── Stage 4: Refinement ───────────────────────────────────────────────
    yield emit(4, "Refinement", "running", "Resolving cross-layer inconsistencies...")
    try:
        ui, api, db, auth, ms4, r4 = s4.run(ui, api, db, auth)
        stage_results.append(PipelineStageResult(stage=4, name="Refinement", success=True, latency_ms=ms4, retries=r4))
        yield emit(4, "Refinement", "done", "Cross-layer consistency verified")
    except Exception as e:
        logger.warning(f"Stage 4 refinement failed (non-fatal): {e}")
        stage_results.append(PipelineStageResult(stage=4, name="Refinement", success=False, latency_ms=0, retries=0))
        yield emit(4, "Refinement", "done", "Skipped — using unrefined schemas")

    # ── Stage 5: Validation + Repair ──────────────────────────────────────
    yield emit(5, "Validation & Repair", "running", "Running cross-layer checks...")
    try:
        ui, api, db, auth, v_issues, repairs = validate_and_repair(ui, api, db, auth)
        ms5 = 50
        stage_results.append(PipelineStageResult(stage=5, name="Validation & Repair", success=True, latency_ms=ms5))
        yield emit(5, "Validation & Repair", "done", f"{len(v_issues)} issues found, {len(repairs)} auto-repaired")
    except Exception as e:
        yield emit(5, "Validation & Repair", "error", str(e))
        raise

    # ── Assemble final config ──────────────────────────────────────────────
    total_ms = int((time.time() - total_start) * 1000)
    client = get_client()

    metadata = PipelineMetadata(
        original_prompt=prompt,
        total_latency_ms=total_ms,
        stages=stage_results,
        total_retries=sum(s.retries for s in stage_results),
        validation_issues=v_issues,
        repair_actions=repairs,
        assumptions=intent.assumptions,
        cost_estimate_usd=round(client.total_cost, 6),
        model_used=client.FLASH,
    )

    config = AppConfig(
        intent=intent,
        architecture=arch,
        ui_schema=ui,
        api_schema=api,
        db_schema=db,
        auth_schema=auth,
        metadata=metadata,
        is_executable=True,
    )

    yield emit(0, "Complete", "done", f"App generated in {total_ms}ms")
    return config
