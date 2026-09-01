from llm.gemini import get_client, FLASH
from models.intent import IntentModel
from models.architecture import ArchitectureModel
import time, logging, json

logger = logging.getLogger(__name__)

SYSTEM = """You are a senior software architect. Given a parsed app intent, produce a
high-level system architecture in JSON.

Return ONLY valid JSON matching this EXACT schema:
{
  "app_name": "string",
  "pages": ["string"],
  "navigation": [
    {"id":"string","label":"string","route":"string","icon":"string","roles":["string"],"is_premium":boolean}
  ],
  "auth_strategy": "string",
  "entity_relationships": [
    {"from_entity":"string","to_entity":"string","relation_type":"has_one|has_many|belongs_to|many_to_many","foreign_key":"string"}
  ],
  "business_flows": [
    {"name":"string","description":"string","steps":["string"],"entities_involved":["string"]}
  ],
  "integrations": ["string"],
  "tech_notes": ["string"]
}

Rules:
- pages: one page per major feature/role section
- navigation items must cover all pages
- entity_relationships: cover ALL entity pairs from intent
- business_flows: key user journeys (create, update, payment, etc.)
- integrations: external services needed (Stripe, SendGrid, etc.)
"""


def run(intent: IntentModel) -> tuple[ArchitectureModel, int, int]:
    client = get_client()
    t0 = time.time()
    retries = 0

    user_msg = f"Design the architecture for this app intent:\n\n{intent.model_dump_json(indent=2)}"

    for attempt in range(3):
        try:
            data = client.call(
                system_prompt=SYSTEM,
                user_prompt=user_msg,
                model_name=FLASH,
                temperature=0.2,
            )
            model = ArchitectureModel(**data)
            ms = int((time.time() - t0) * 1000)
            return model, ms, retries
        except Exception as e:
            retries += 1
            logger.warning(f"Stage2 attempt {attempt+1} failed: {e}")

    raise RuntimeError("Stage 2 (System Design) failed after 3 attempts")
