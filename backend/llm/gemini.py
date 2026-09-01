import google.generativeai as genai
import json
import os
import time
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

FLASH = "gemini-2.0-flash"
PRO   = "gemini-2.0-flash"

# Cost per 1M tokens (USD)
COST = {
    FLASH: {"input": 0.075, "output": 0.30},
    PRO:   {"input": 0.075, "output": 0.30},
}


class LLMError(Exception):
    pass


class GeminiClient:
    def __init__(self):
        key = os.environ.get("GOOGLE_API_KEY", "")
        if not key:
            raise ValueError("GOOGLE_API_KEY not set")
        genai.configure(api_key=key)
        self.total_cost: float = 0.0
        self.FLASH = FLASH
        self.PRO = PRO

    def _model(self, name: str, temp: float):
        return genai.GenerativeModel(
            name,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=temp,
                max_output_tokens=8192,
            ),
        )

    def _calc_cost(self, response, model_name: str) -> float:
        try:
            u = response.usage_metadata
            inp = getattr(u, "prompt_token_count", 0)
            out = getattr(u, "candidates_token_count", 0)
            rates = COST.get(model_name, COST[FLASH])
            return (inp * rates["input"] + out * rates["output"]) / 1_000_000
        except Exception:
            return 0.0

    def call(
        self,
        system_prompt: str,
        user_prompt: str,
        model_name: str = FLASH,
        temperature: float = 0.0,
        max_retries: int = 10,
    ) -> Dict[str, Any]:
        """Synchronous JSON call with retry on parse failure or rate limits."""
        model = self._model(model_name, temperature)
        full_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"

        last_err: Optional[Exception] = None
        for attempt in range(1, max_retries + 1):
            try:
                response = model.generate_content(full_prompt)
                raw = response.text.strip()
                # Strip markdown fences if present
                if "```" in raw:
                    import re
                    match = re.search(r'```(?:json)?\s*([\s\S]*?)```', raw)
                    if match:
                        raw = match.group(1).strip()
                # Fallback: extract between first { and last }
                if not raw.startswith("{") and not raw.startswith("["):
                    start = raw.find("{")
                    end = raw.rfind("}")
                    if start != -1 and end != -1:
                        raw = raw[start:end+1]
                data = json.loads(raw)
                cost = self._calc_cost(response, model_name)
                self.total_cost += cost
                return data
            except json.JSONDecodeError as e:
                last_err = e
                logger.warning(f"JSON parse error attempt {attempt}: {e}")
                time.sleep(2 * attempt)
            except Exception as e:
                last_err = e
                error_str = str(e)
                logger.warning(f"LLM error attempt {attempt}: {error_str}")
                if "429" in error_str or "quota" in error_str.lower():
                    logger.warning("Rate limit hit, waiting 15 seconds before retrying...")
                    time.sleep(15)
                else:
                    time.sleep(2 * attempt)

        raise LLMError(f"Failed after {max_retries} attempts: {last_err}")


import httpx

class GroqClient:
    def __init__(self):
        self.key = os.environ.get("GROQ_API_KEY", "")
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        self.total_cost = 0.0
        self.FLASH = "llama-3.3-70b-versatile"
        self.PRO = "llama-3.3-70b-versatile"

    def call(self, system_prompt: str, user_prompt: str, model_name: str = "llama-3.3-70b-versatile", temperature: float = 0.0, max_retries: int = 5) -> Dict[str, Any]:
        # Always use our own model, ignore any Gemini model names passed by stages
        model_name = self.FLASH
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": temperature
        }
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Groq request attempt {attempt+1}...")
                with httpx.Client(timeout=60.0) as client:
                    resp = client.post(self.url, headers=headers, json=payload)
                    resp.raise_for_status()
                    
                    content = resp.json()["choices"][0]["message"]["content"].strip()
                    # Strip markdown if LLM misbehaves
                    if "```" in content:
                        import re
                        match = re.search(r'```(?:json)?\s*([\s\S]*?)```', content)
                        if match:
                            content = match.group(1).strip()
                    # Fallback: extract between first { and last }
                    if not content.startswith("{") and not content.startswith("["):
                        start = content.find("{")
                        end = content.rfind("}")
                        if start != -1 and end != -1:
                            content = content[start:end+1]
                    
                    # Estimate cost (approximate token counts)
                    prompt_len = len(system_prompt) + len(user_prompt)
                    response_len = len(content)
                    est_input_tokens = prompt_len // 4
                    est_output_tokens = response_len // 4
                    self.total_cost += (est_input_tokens * 0.05 + est_output_tokens * 0.08) / 1_000_000

                    return json.loads(content)
            except Exception as e:
                error_str = str(e)
                logger.warning(f"Groq error attempt {attempt+1}: {error_str}")
                if "429" in error_str:
                    logger.warning("Groq rate limit hit, waiting 20 seconds before retrying...")
                    time.sleep(20)
                else:
                    time.sleep(2 * (attempt + 1))
        raise LLMError(f"Groq failed after {max_retries} attempts")

# Singleton
_client: Optional[Any] = None

def get_client() -> Any:
    global _client
    if _client is None:
        # Force a fresh reload of environment variables
        from dotenv import load_dotenv
        load_dotenv(override=True)
        
        groq_key = os.environ.get("GROQ_API_KEY")
        if groq_key and len(groq_key) > 10:
            logger.info(f">>> FORCING GROQ MODE (Key starts with: {groq_key[:6]}...)")
            _client = GroqClient()
        else:
            logger.info(">>> FALLING BACK TO GEMINI (Groq key missing or too short)")
            _client = GeminiClient()
    return _client
