from llm.gemini import get_client, FLASH
from models.intent import IntentModel
import time, logging

logger = logging.getLogger(__name__)

SYSTEM = """You are an expert software architect specializing in parsing natural language
app descriptions into structured intent JSON.

Return ONLY valid JSON matching this EXACT schema (no extra fields):
{
  "app_type": "string",
  "app_name": "string",
  "primary_entities": ["string"],
  "features": ["string"],
  "user_roles": ["string"],
  "constraints": ["string"],
  "ambiguities": ["string"],
  "assumptions": ["string"],
  "complexity": "simple|medium|complex",
  "has_payments": boolean,
  "has_analytics": boolean,
  "has_notifications": boolean,
  "has_file_uploads": boolean
}

Rules:
- primary_entities: concrete data models (e.g. User, Contact, Product)
- features: capabilities (e.g. authentication, dashboard, search, export)
- user_roles: at least 2 roles always (e.g. admin, user)
- ambiguities: things NOT specified in the prompt
- assumptions: reasonable defaults you assumed
- complexity: simple(<5 entities), medium(5-10), complex(10+)
"""


def run(prompt: str) -> tuple[IntentModel, int, int]:
    """Returns (IntentModel, latency_ms, retries)."""
    client = get_client()
    t0 = time.time()
    retries = 0

    for attempt in range(5):
        try:
            data = client.call(
                system_prompt=SYSTEM,
                user_prompt=f"Parse this app description into intent:\n\n{prompt}",
                model_name=FLASH,
                temperature=0.0,
            )
            model = IntentModel(**data)
            ms = int((time.time() - t0) * 1000)
            return model, ms, retries
        except Exception as e:
            retries += 1
            logger.warning(f"Stage1 attempt {attempt+1} failed: {e}")

    raise RuntimeError("Stage 1 (Intent Extraction) failed after 5 attempts")
