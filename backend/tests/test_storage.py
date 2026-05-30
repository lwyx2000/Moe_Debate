from app.debate import coach_reply
from app.models import DebateRequest
from app.storage import get_debate_session, list_debate_sessions, save_debate_session


def test_save_and_load_debate_session() -> None:
    request = DebateRequest(topicId="screen-time", side="正方", message="我认为可以，因为我会先写作业。")
    response = coach_reply(request)

    saved = save_debate_session(request, response)
    loaded = get_debate_session(saved.id)

    assert loaded is not None
    assert loaded.id == saved.id
    assert loaded.rubric.clarity == response.rubric.clarity
    assert loaded.message == request.message


def test_list_debate_sessions_limit() -> None:
    request = DebateRequest(topicId="homework-pet", side="反方", message="我认为可以自由安排，因为每天活动不同。")
    save_debate_session(request, coach_reply(request))

    sessions = list_debate_sessions(limit=1)

    assert len(sessions) == 1
    assert sessions[0].topicId in {"screen-time", "homework-pet"}


from app.models import IntegrationSettings, ProviderConfig
from app.storage import get_integration_settings, save_integration_settings


def test_save_and_load_integration_settings() -> None:
    settings = IntegrationSettings(
        llm=ProviderConfig(enabled=True, baseUrl="http://127.0.0.1:8001/v1", model="local-qwen", apiKey=""),
        asr=ProviderConfig(enabled=True, baseUrl="http://127.0.0.1:8002", model="Qwen3-ASR-0.6B", apiKey=""),
        tts=ProviderConfig(enabled=True, baseUrl="http://127.0.0.1:8005", model="kitten-tts", apiKey=""),
    )

    saved = save_integration_settings(settings)
    loaded = get_integration_settings()

    assert saved.updatedAt
    assert loaded.llm.enabled is True
    assert loaded.tts.baseUrl == "http://127.0.0.1:8005"
