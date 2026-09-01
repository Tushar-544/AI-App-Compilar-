"""
Compilar Backend — FastAPI App
"""
import logging, os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import json

from pipeline.orchestrator import run_pipeline
from evaluator.runner import run_all, run_single
from evaluator.dataset import ALL_PROMPTS

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Compilar API",
    description="AI-powered compiler: Natural Language → Validated App Config",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request/Response models ────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    prompt: str
    stream: bool = False


class EvalRequest(BaseModel):
    prompt_ids: Optional[List[str]] = None


# ── Routes ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "compilar-backend"}


@app.post("/generate")
def generate(req: GenerateRequest):
    """
    Main endpoint: run the full 5-stage pipeline.
    Returns the complete AppConfig JSON.
    """
    if not req.prompt or len(req.prompt.strip()) < 3:
        raise HTTPException(status_code=400, detail="Prompt is too short")

    try:
        events = []
        gen = run_pipeline(req.prompt.strip())
        try:
            while True:
                events.append(next(gen))
        except StopIteration as e:
            config = e.value
        return {
            "success": True,
            "config": config.model_dump(),
            "events": events,
        }
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate/stream")
def generate_stream(req: GenerateRequest):
    """
    Streaming endpoint with Demo Mode for Internship Presentations.
    """
    def event_stream():
        try:
            gen = run_pipeline(req.prompt.strip())
            while True:
                try:
                    event = next(gen)
                    yield f"data: {json.dumps(event)}\n\n"
                except StopIteration as e:
                    config = e.value
                    yield f"data: {json.dumps({'stage': 0, 'name': 'Result', 'status': 'done', 'config': config.model_dump()})}\n\n"
                    break
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'stage': 0, 'name': 'Error', 'status': 'error', 'detail': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/evaluate")
def evaluate(req: EvalRequest):
    """Run evaluation on 20 test prompts (or a subset)."""
    try:
        result = run_all(req.prompt_ids)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/evaluate/prompts")
def list_prompts():
    """List all evaluation prompts."""
    return {"prompts": [{"id": p["id"], "label": p["label"]} for p in ALL_PROMPTS]}


@app.post("/evaluate/single")
def evaluate_single(req: GenerateRequest):
    """Evaluate a single custom prompt and return metrics."""
    item = {"id": "custom", "label": "Custom Prompt", "prompt": req.prompt}
    result = run_single(item)
    return result
