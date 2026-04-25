"""POST /api/stories/create — generate a structured user story + acceptance criteria from a raw idea."""
import os
import re
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["stories"])


class StoryCreateRequest(BaseModel):
    idea: str
    model: str = "flash"


class StoryCreateResult(BaseModel):
    user_story: str
    acceptance_criteria: list[str]


def _call_llm(model: str, prompt: str) -> str:
    """Call the configured LLM and return the raw text response."""
    from backend.infrastructure.generator_factory import GeneratorFactory
    generator = GeneratorFactory.create(model)
    # We reuse the generator's client directly for a simple text call
    # GeminiGenerator and ClaudeGenerator both expose .generate() but it returns
    # a GenerationResult with bdd_text. We need raw text, so we call the
    # underlying client directly based on provider type.
    from src.generators.gemini_generator import GeminiGenerator
    from src.generators.claude_generator import ClaudeGenerator
    from src.generators.groq_generator import GroqGenerator

    if isinstance(generator, GeminiGenerator):
        from google import genai as _genai
        from google.genai import types as _types
        api_key = os.getenv("GEMINI_API_KEY", "")
        client = _genai.Client(api_key=api_key)
        model_id = generator.model_id
        resp = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=_types.GenerateContentConfig(max_output_tokens=2048),
        )
        return resp.text or ""
    elif isinstance(generator, GroqGenerator):
        from groq import Groq
        api_key = os.getenv("GROQ_API_KEY", "")
        client = Groq(api_key=api_key)
        model_id = generator.model_id
        completion = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
        )
        return completion.choices[0].message.content or ""
    else:
        import anthropic
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        client = anthropic.Anthropic(api_key=api_key)
        from src.generators.claude_generator import MODEL_IDS as CLAUDE_MODEL_IDS
        model_id = CLAUDE_MODEL_IDS.get(model, "claude-sonnet-4-6")
        msg = client.messages.create(
            model=model_id,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text if msg.content else ""


def _build_prompt(idea: str) -> str:
    return f"""Você é um especialista em Product Management e BDD.

A partir da ideia abaixo, gere:
1. Uma user story estruturada no formato: "Como [persona], quero [ação], para [benefício]."
2. Uma lista de 4 a 7 critérios de aceitação objetivos e testáveis.

Ideia: {idea}

Responda APENAS com JSON válido neste formato exato:
{{
  "user_story": "Como [persona], quero [ação], para [benefício].",
  "acceptance_criteria": [
    "critério 1",
    "critério 2",
    "critério 3"
  ]
}}

Não inclua explicações, markdown ou texto fora do JSON."""


def _parse_response(text: str) -> dict:
    """Extract JSON from LLM response, tolerating markdown fences."""
    # Strip markdown code fences if present
    clean = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("`").strip()
    # Find first { ... } block
    match = re.search(r"\{.*\}", clean, re.DOTALL)
    if match:
        return json.loads(match.group())
    return json.loads(clean)


@router.post("/stories/create", response_model=StoryCreateResult)
def create_story(req: StoryCreateRequest):
    if not req.idea.strip():
        raise HTTPException(status_code=422, detail="O campo 'idea' não pode estar vazio.")
    try:
        prompt = _build_prompt(req.idea.strip())
        raw = _call_llm(req.model, prompt)
        data = _parse_response(raw)
        return StoryCreateResult(
            user_story=data["user_story"],
            acceptance_criteria=data["acceptance_criteria"],
        )
    except (json.JSONDecodeError, KeyError) as e:
        raise HTTPException(status_code=500, detail=f"Resposta inválida do modelo: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
