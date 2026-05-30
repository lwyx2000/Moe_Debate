import pytest

from app.integrations import generate_cloud_coach_response
from app.models import CoachResponse, DebateRequest, ProviderConfig, Rubric


@pytest.mark.asyncio
async def test_disabled_cloud_coach_returns_none() -> None:
    request = DebateRequest(topicId="screen-time", side="正方", message="我认为可以，因为我会先完成作业。")
    fallback = CoachResponse(
        reply="fallback",
        rubric=Rubric(clarity=70, evidence=70, manners=70),
        nextPrompt="next",
    )
    provider = ProviderConfig(enabled=False, baseUrl="https://example.com/v1", model="demo", apiKey="")

    assert await generate_cloud_coach_response(request, provider, fallback) is None
