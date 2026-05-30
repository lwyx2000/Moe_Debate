from __future__ import annotations

import json
from typing import Any

import httpx
from fastapi import UploadFile

from .models import CoachResponse, DebateRequest, ProviderConfig, Rubric, SpeechSynthesisResult, SpeechTranscription


def _auth_headers(provider: ProviderConfig) -> dict[str, str]:
    return {"Authorization": f"Bearer {provider.apiKey}"} if provider.apiKey else {}


def _json_from_text(text: str) -> dict[str, Any] | None:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        value = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def _rubric_from_payload(payload: dict[str, Any], fallback: Rubric) -> Rubric:
    rubric = payload.get("rubric")
    if not isinstance(rubric, dict):
        return fallback

    def score(key: str, default: int) -> int:
        value = rubric.get(key, default)
        if not isinstance(value, int | float):
            return default
        return max(0, min(100, int(value)))

    return Rubric(
        clarity=score("clarity", fallback.clarity),
        evidence=score("evidence", fallback.evidence),
        manners=score("manners", fallback.manners),
    )


async def generate_cloud_coach_response(
    request: DebateRequest,
    provider: ProviderConfig,
    fallback: CoachResponse,
) -> CoachResponse | None:
    if not provider.enabled:
        return None

    prompt = f"""
你是儿童辩论教练。请用温柔、鼓励、适合小学生的中文反馈。
孩子选择的立场：{request.side}
孩子发言：{request.message}

请只输出 JSON，格式如下：
{{
  "reply": "一句到三句教练反馈，不要写‘下一步’字样",
  "rubric": {{"clarity": 0-100, "evidence": 0-100, "manners": 0-100}},
  "nextPrompt": "下一句练习提示"
}}
""".strip()

    url = f"{provider.baseUrl.rstrip('/')}/chat/completions"
    body = {
        "model": provider.model,
        "messages": [
            {"role": "system", "content": "你是儿童辩论训练产品里的安全、耐心、简洁的中文教练。"},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.4,
        "response_format": {"type": "json_object"},
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=body, headers=_auth_headers(provider))
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, ValueError):
        return None

    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    if not isinstance(content, str):
        return None

    parsed = _json_from_text(content)
    if parsed is None:
        return CoachResponse(reply=content[:500], rubric=fallback.rubric, nextPrompt=fallback.nextPrompt)

    return CoachResponse(
        reply=str(parsed.get("reply") or fallback.reply),
        rubric=_rubric_from_payload(parsed, fallback.rubric),
        nextPrompt=str(parsed.get("nextPrompt") or fallback.nextPrompt),
    )


async def transcribe_with_provider(file: UploadFile, provider: ProviderConfig) -> SpeechTranscription | None:
    if not provider.enabled:
        return None

    filename = file.filename or "recording.webm"
    content = await file.read()
    url = f"{provider.baseUrl.rstrip('/')}/transcribe"

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                url,
                data={"model": provider.model},
                files={"file": (filename, content, file.content_type or "audio/webm")},
                headers=_auth_headers(provider),
            )
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, ValueError):
        return None

    text = data.get("text") or data.get("transcript") or data.get("result") or ""
    return SpeechTranscription(filename=filename, text=str(text), engine=provider.model)


async def synthesize_with_provider(text: str, provider: ProviderConfig) -> SpeechSynthesisResult | None:
    if not provider.enabled:
        return None

    url = f"{provider.baseUrl.rstrip('/')}/synthesize"
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                url,
                json={"text": text, "model": provider.model},
                headers=_auth_headers(provider),
            )
            response.raise_for_status()
            data = response.json()
    except (httpx.HTTPError, ValueError):
        return None

    audio_url = data.get("audioUrl") or data.get("audio_url") or data.get("url") or ""
    return SpeechSynthesisResult(text=text, audioUrl=str(audio_url), engine=provider.model)
