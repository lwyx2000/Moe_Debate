from fastapi import Depends, FastAPI, Header, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from .debate import DEMO_REPORT, coach_reply, filter_topics
from .integrations import generate_cloud_coach_response, synthesize_with_provider, transcribe_with_provider
from .topic_seed import load_seed_collections, load_seed_topics
from .storage import append_practice_turn, authenticate_user, build_growth_report, clear_topic_bank, create_auth_token, create_practice_session, create_user, delete_child_profile, delete_topic, delete_topic_collection, delete_topic_favorite, finish_practice_session, get_child_profile, get_debate_session, get_demo_user, get_integration_settings, get_practice_session, get_topic, get_topic_collection, get_user_by_email, get_user_by_token, init_db, list_child_profiles, list_debate_sessions, list_debate_sessions_for_children, list_favorite_topic_ids, list_topic_bank, list_topic_collections, revoke_auth_token, save_child_profile, save_debate_session, save_integration_settings, save_topic_favorite, save_topic, save_topic_collection, seed_demo_user_if_empty, seed_topic_bank_if_empty
from .models import (
    AuthLoginRequest,
    AuthRegisterRequest,
    AuthToken,
    ChildProfile,
    CoachResponse,
    DebateRequest,
    DebateSession,
    DebateTopic,
    GrowthReport,
    IntegrationSettings,
    PracticeSession,
    PracticeSessionFinishRequest,
    PracticeSessionStartRequest,
    PracticeTurn,
    PracticeTurnCreateRequest,
    SpeechSynthesisRequest,
    SpeechSynthesisResult,
    SpeechTranscription,
    TopicBulkImportRequest,
    TopicBulkImportResult,
    TopicCollection,
    UserAccount,
    VoicePlan,
    VoiceSettings,
)

app = FastAPI(title="Moe Debate API", version="0.1.0")


def _ensure_topic_bank() -> None:
    seed_topic_bank_if_empty(load_seed_topics(), load_seed_collections())


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    _ensure_topic_bank()
    seed_demo_user_if_empty()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def _bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token


def current_user(authorization: str | None = Header(default=None)) -> UserAccount:
    token = _bearer_token(authorization)
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    user = get_user_by_token(token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token")
    return user


def current_admin(user: UserAccount = Depends(current_user)) -> UserAccount:
    if user.role not in {"admin", "teacher"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin permission required")
    return user


def _assert_child_access(child_id: str | None, user: UserAccount) -> None:
    if child_id is None or user.role in {"admin", "teacher"}:
        return
    profile = get_child_profile(child_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Child profile not found")
    if profile.userId != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Child profile permission denied")


@app.post("/api/auth/register", response_model=AuthToken)
def register(payload: AuthRegisterRequest) -> AuthToken:
    if get_user_by_email(payload.email) is not None:
        raise HTTPException(status_code=409, detail="Email already registered")
    safe_payload = payload.model_copy(update={"role": "parent"})
    user = create_user(safe_payload)
    return create_auth_token(user)


@app.post("/api/auth/login", response_model=AuthToken)
def login(payload: AuthLoginRequest) -> AuthToken:
    user = authenticate_user(payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return create_auth_token(user)


@app.get("/api/auth/me", response_model=UserAccount)
def me(user: UserAccount = Depends(current_user)) -> UserAccount:
    return user


@app.post("/api/auth/logout")
def logout(authorization: str | None = Header(default=None)) -> dict[str, str]:
    token = _bearer_token(authorization)
    if token:
        revoke_auth_token(token)
    return {"status": "ok"}


def _topic_bank() -> list[DebateTopic]:
    _ensure_topic_bank()
    return list_topic_bank()


@app.get("/api/topics", response_model=list[DebateTopic])
def list_topics(
    collectionId: str | None = Query(default=None, description="题库分类 ID，例如 family-rules"),
    ageRange: str | None = Query(default=None, description="适合年龄段，例如 7-9"),
    difficulty: str | None = Query(default=None, description="难度：easy / medium / hard"),
    tag: str | None = Query(default=None, description="中文标签，例如 阅读"),
    q: str | None = Query(default=None, description="关键词搜索：标题、背景、标签、提示卡"),
) -> list[DebateTopic]:
    return filter_topics(topics=_topic_bank(), collection_id=collectionId, age_range=ageRange, difficulty=difficulty, tag=tag, q=q)


@app.get("/api/topics/{topic_id}", response_model=DebateTopic)
def topic_detail(topic_id: str) -> DebateTopic:
    _ensure_topic_bank()
    topic = get_topic(topic_id)
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic




@app.get("/api/favorites/topics", response_model=list[str])
def favorite_topics(user: UserAccount = Depends(current_user)) -> list[str]:
    return list_favorite_topic_ids(user.id)


@app.post("/api/favorites/topics/{topic_id}")
def add_favorite_topic(topic_id: str, user: UserAccount = Depends(current_user)) -> dict[str, str]:
    _ensure_topic_bank()
    if get_topic(topic_id) is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    save_topic_favorite(user.id, topic_id)
    return {"status": "saved", "id": topic_id}


@app.delete("/api/favorites/topics/{topic_id}")
def remove_favorite_topic(topic_id: str, user: UserAccount = Depends(current_user)) -> dict[str, str]:
    delete_topic_favorite(user.id, topic_id)
    return {"status": "deleted", "id": topic_id}

@app.post("/api/admin/topics", response_model=DebateTopic)
def create_admin_topic(topic: DebateTopic, user: UserAccount = Depends(current_admin)) -> DebateTopic:
    _ensure_topic_bank()
    if get_topic(topic.id) is not None:
        raise HTTPException(status_code=409, detail="Topic already exists")
    return save_topic(topic)


@app.put("/api/admin/topics/{topic_id}", response_model=DebateTopic)
def update_admin_topic(topic_id: str, topic: DebateTopic, user: UserAccount = Depends(current_admin)) -> DebateTopic:
    if topic_id != topic.id:
        raise HTTPException(status_code=400, detail="Topic id in path and payload must match")
    _ensure_topic_bank()
    return save_topic(topic)


@app.delete("/api/admin/topics/{topic_id}")
def delete_admin_topic(topic_id: str, user: UserAccount = Depends(current_admin)) -> dict[str, str]:
    _ensure_topic_bank()
    if not delete_topic(topic_id):
        raise HTTPException(status_code=404, detail="Topic not found")
    return {"status": "deleted", "id": topic_id}




@app.post("/api/admin/topics/import", response_model=TopicBulkImportResult)
def import_admin_topics(payload: TopicBulkImportRequest, user: UserAccount = Depends(current_admin)) -> TopicBulkImportResult:
    if not payload.topics and not payload.collections:
        raise HTTPException(status_code=400, detail="No topics or collections to import")
    if payload.replaceExisting:
        clear_topic_bank()

    for collection in payload.collections:
        save_topic_collection(collection)

    existing_collection_ids = {collection.id for collection in list_topic_collections()}
    missing_collection_ids = {topic.collectionId for topic in payload.topics if topic.collectionId not in existing_collection_ids}
    if missing_collection_ids:
        raise HTTPException(status_code=400, detail=f"Missing topic collections: {', '.join(sorted(missing_collection_ids))}")

    for topic in payload.topics:
        save_topic(topic)

    return TopicBulkImportResult(
        importedTopics=len(payload.topics),
        importedCollections=len(payload.collections),
        mode="replace" if payload.replaceExisting else "upsert",
    )

@app.get("/api/topic-collections", response_model=list[TopicCollection])
def topic_collections() -> list[TopicCollection]:
    _ensure_topic_bank()
    return list_topic_collections()


@app.post("/api/admin/topic-collections", response_model=TopicCollection)
def create_admin_topic_collection(collection: TopicCollection, user: UserAccount = Depends(current_admin)) -> TopicCollection:
    _ensure_topic_bank()
    if get_topic_collection(collection.id) is not None:
        raise HTTPException(status_code=409, detail="Topic collection already exists")
    return save_topic_collection(collection)


@app.put("/api/admin/topic-collections/{collection_id}", response_model=TopicCollection)
def update_admin_topic_collection(collection_id: str, collection: TopicCollection, user: UserAccount = Depends(current_admin)) -> TopicCollection:
    if collection_id != collection.id:
        raise HTTPException(status_code=400, detail="Collection id in path and payload must match")
    _ensure_topic_bank()
    return save_topic_collection(collection)


@app.delete("/api/admin/topic-collections/{collection_id}")
def delete_admin_topic_collection(collection_id: str, user: UserAccount = Depends(current_admin)) -> dict[str, str]:
    _ensure_topic_bank()
    if any(topic.collectionId == collection_id for topic in list_topic_bank()):
        raise HTTPException(status_code=409, detail="Move or delete topics in this collection first")
    if not delete_topic_collection(collection_id):
        raise HTTPException(status_code=404, detail="Topic collection not found")
    return {"status": "deleted", "id": collection_id}


@app.get("/api/users/demo", response_model=UserAccount)
def demo_user() -> UserAccount:
    return get_demo_user()


@app.get("/api/children", response_model=list[ChildProfile])
def children(user: UserAccount = Depends(current_user)) -> list[ChildProfile]:
    return list_child_profiles(user_id=user.id)


@app.get("/api/children/{child_id}", response_model=ChildProfile)
def child_detail(child_id: str, user: UserAccount = Depends(current_user)) -> ChildProfile:
    profile = get_child_profile(child_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Child profile not found")
    _assert_child_access(child_id, user)
    return profile


@app.post("/api/children", response_model=ChildProfile)
def create_child(profile: ChildProfile, user: UserAccount = Depends(current_user)) -> ChildProfile:
    if get_child_profile(profile.id) is not None:
        raise HTTPException(status_code=409, detail="Child profile already exists")
    return save_child_profile(profile.model_copy(update={"userId": user.id}))


@app.put("/api/children/{child_id}", response_model=ChildProfile)
def update_child(child_id: str, profile: ChildProfile, user: UserAccount = Depends(current_user)) -> ChildProfile:
    if child_id != profile.id:
        raise HTTPException(status_code=400, detail="Child id in path and payload must match")
    _assert_child_access(child_id, user)
    return save_child_profile(profile.model_copy(update={"userId": user.id if user.role == "parent" else profile.userId}))


@app.delete("/api/children/{child_id}")
def delete_child(child_id: str, user: UserAccount = Depends(current_user)) -> dict[str, str]:
    _assert_child_access(child_id, user)
    if not delete_child_profile(child_id):
        raise HTTPException(status_code=404, detail="Child profile not found")
    return {"status": "deleted", "id": child_id}


@app.get("/api/reports/demo", response_model=GrowthReport)
def get_demo_report(
    childId: str | None = None,
    dateFrom: str | None = None,
    dateTo: str | None = None,
    topicId: str | None = None,
    collectionId: str | None = None,
    user: UserAccount = Depends(current_user),
) -> GrowthReport:
    _assert_child_access(childId, user)
    report_filters = {
        "date_from": dateFrom,
        "date_to": dateTo,
        "topic_id": topicId,
        "collection_id": collectionId,
    }
    if childId is None and user.role == "parent":
        first_child = next(iter(list_child_profiles(user_id=user.id)), None)
        if not first_child:
            return DEMO_REPORT
        return build_growth_report(child_id=first_child.id, **report_filters) or DEMO_REPORT
    return build_growth_report(child_id=childId, **report_filters) or DEMO_REPORT


@app.post("/api/debate/respond", response_model=CoachResponse)
async def respond(request: DebateRequest, user: UserAccount = Depends(current_user)) -> CoachResponse:
    _assert_child_access(request.childId, user)
    if request.practiceSessionId:
        session = get_practice_session(request.practiceSessionId)
        if session is None:
            raise HTTPException(status_code=404, detail="Practice session not found")
        _assert_child_access(session.childId, user)
    fallback = coach_reply(request)
    settings = get_integration_settings()
    response = await generate_cloud_coach_response(request, settings.llm, fallback) or fallback
    saved_session = save_debate_session(request, response)
    return response.model_copy(update={"practiceSessionId": saved_session.practiceSessionId})


@app.post("/api/practice/sessions", response_model=PracticeSession)
def start_practice_session(payload: PracticeSessionStartRequest, user: UserAccount = Depends(current_user)) -> PracticeSession:
    _assert_child_access(payload.childId, user)
    return create_practice_session(payload)


@app.get("/api/practice/sessions/{session_id}", response_model=PracticeSession)
def practice_session_detail(session_id: str, user: UserAccount = Depends(current_user)) -> PracticeSession:
    session = get_practice_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Practice session not found")
    _assert_child_access(session.childId, user)
    return session


@app.post("/api/practice/sessions/{session_id}/turns", response_model=PracticeTurn)
def add_practice_turn(session_id: str, payload: PracticeTurnCreateRequest, user: UserAccount = Depends(current_user)) -> PracticeTurn:
    session = get_practice_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Practice session not found")
    _assert_child_access(session.childId, user)
    turn = append_practice_turn(session_id, payload)
    if turn is None:
        raise HTTPException(status_code=404, detail="Practice session not found")
    return turn


@app.post("/api/practice/sessions/{session_id}/finish", response_model=PracticeSession)
def finish_practice(session_id: str, payload: PracticeSessionFinishRequest, user: UserAccount = Depends(current_user)) -> PracticeSession:
    session = get_practice_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Practice session not found")
    _assert_child_access(session.childId, user)
    finished = finish_practice_session(session_id, payload.summary)
    if finished is None:
        raise HTTPException(status_code=404, detail="Practice session not found")
    return finished


@app.get("/api/debate/sessions", response_model=list[DebateSession])
def debate_sessions(
    limit: int = Query(default=20, ge=1, le=100),
    childId: str | None = None,
    dateFrom: str | None = None,
    dateTo: str | None = None,
    topicId: str | None = None,
    collectionId: str | None = None,
    user: UserAccount = Depends(current_user),
) -> list[DebateSession]:
    _assert_child_access(childId, user)
    if childId is not None or user.role in {"admin", "teacher"}:
        return list_debate_sessions(
            limit=limit,
            child_id=childId,
            date_from=dateFrom,
            date_to=dateTo,
            topic_id=topicId,
            collection_id=collectionId,
        )
    child_ids = [profile.id for profile in list_child_profiles(user_id=user.id)]
    return list_debate_sessions_for_children(
        child_ids,
        limit=limit,
        date_from=dateFrom,
        date_to=dateTo,
        topic_id=topicId,
        collection_id=collectionId,
    )


@app.get("/api/debate/sessions/{session_id}", response_model=DebateSession)
def debate_session_detail(session_id: str, user: UserAccount = Depends(current_user)) -> DebateSession:
    session = get_debate_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Debate session not found")
    _assert_child_access(session.childId, user)
    return session


@app.post("/api/speech/transcribe", response_model=SpeechTranscription)
async def transcribe_stub(file: UploadFile) -> SpeechTranscription:
    """Transcribe audio through configured ASR service, with a development fallback."""
    settings = get_integration_settings()
    result = await transcribe_with_provider(file, settings.asr)
    if result is not None:
        return result

    return SpeechTranscription(
        filename=file.filename or "recording.webm",
        text="语音识别服务尚未接入；当前接口用于前端联调。",
        engine="planned:qwen3-asr-0.6b",
    )


@app.post("/api/speech/synthesize", response_model=SpeechSynthesisResult)
async def synthesize_stub(payload: SpeechSynthesisRequest) -> SpeechSynthesisResult:
    """Synthesize speech through configured TTS service, with a development fallback."""
    settings = get_integration_settings()
    result = await synthesize_with_provider(payload.text, settings.tts)
    if result is not None:
        return result

    return SpeechSynthesisResult(
        text=payload.text,
        audioUrl="",
        engine="planned:kitten-tts-server",
    )




@app.get("/api/integrations/settings", response_model=IntegrationSettings)
def integration_settings(user: UserAccount = Depends(current_admin)) -> IntegrationSettings:
    return get_integration_settings()


@app.put("/api/integrations/settings", response_model=IntegrationSettings)
def update_integration_settings(settings: IntegrationSettings, user: UserAccount = Depends(current_admin)) -> IntegrationSettings:
    return save_integration_settings(settings)


@app.get("/api/voice/settings", response_model=VoiceSettings)
def voice_settings() -> VoiceSettings:
    return VoiceSettings(
        asrEngine="Qwen3-ASR-0.6B",
        ttsEngine="Kitten-TTS-Server",
        fallbackMode="browser-speech-synthesis",
        saveRawAudio=False,
        maxRecordingSeconds=60,
        childSafetyNotes=[
            "默认不保存儿童原始音频。",
            "录音前端必须显示明确的开始、停止和识别状态。",
            "如需保存音频，必须增加家长授权和删除入口。",
        ],
    )


@app.get("/api/voice/plan", response_model=VoicePlan)
def voice_plan() -> VoicePlan:
    return VoicePlan(
        input="Qwen3-ASR-0.6B for Mandarin-first local speech recognition; Moonshine as a low-latency fallback when multilingual real-time agents are needed.",
        output="Kitten-TTS-Server for lightweight local text-to-speech; Moonshine TTS can be evaluated later if one unified voice-agent stack is preferred.",
        recommendation="Start with Qwen3-ASR-0.6B + Kitten-TTS-Server behind the Python API.",
        notes=[
            "Moonshine is useful for on-device voice agents, but it is not only a TTS engine.",
            "Qwen3-ASR provides stronger ASR positioning for Chinese debate input.",
            "Kitten TTS is small and easy to self-host for child-friendly spoken feedback.",
        ],
    )
