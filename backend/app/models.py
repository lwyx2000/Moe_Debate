from pydantic import BaseModel, Field


class DebateTopic(BaseModel):
    id: str
    title: str
    sideA: str
    sideB: str
    starterTips: list[str]
    collectionId: str
    ageRange: str
    difficulty: str
    tags: list[str]
    background: str
    sideATips: list[str]
    sideBTips: list[str]
    examples: list[str]


class TopicCollection(BaseModel):
    id: str
    icon: str
    title: str
    description: str
    count: int = 0
    topicIds: list[str] = Field(default_factory=list)


class TopicBulkImportRequest(BaseModel):
    topics: list[DebateTopic] = Field(default_factory=list)
    collections: list[TopicCollection] = Field(default_factory=list)
    replaceExisting: bool = False


class TopicBulkImportResult(BaseModel):
    importedTopics: int
    importedCollections: int
    mode: str


class DebateRequest(BaseModel):
    topicId: str = Field(min_length=1)
    side: str = Field(pattern="^(正方|反方)$")
    message: str = Field(min_length=1, max_length=1200)
    childId: str | None = None
    practiceSessionId: str | None = None


class Rubric(BaseModel):
    clarity: int = Field(ge=0, le=100)
    evidence: int = Field(ge=0, le=100)
    manners: int = Field(ge=0, le=100)


class CoachResponse(BaseModel):
    reply: str
    rubric: Rubric
    nextPrompt: str
    practiceSessionId: str = ""


class ReportMetric(BaseModel):
    key: str
    title: str
    score: int = Field(ge=0, le=100)
    hint: str


class TrendPoint(BaseModel):
    label: str
    clarity: int
    evidence: int
    manners: int


class GrowthReport(BaseModel):
    childName: str
    weekLabel: str
    completedDebates: int
    streakDays: int
    metrics: list[ReportMetric]
    coachNote: str
    nextGoal: str
    trend: list[TrendPoint] = Field(default_factory=list)
    weakSpot: str = ""
    recommendedTopicId: str = ""
    recommendedTopicTitle: str = ""
    parentComment: str = ""
    teacherComment: str = ""
    totalPracticeMinutes: int = 0
    activeDays: int = 0


class SpeechTranscription(BaseModel):
    filename: str
    text: str
    engine: str


class SpeechSynthesisRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1200)


class SpeechSynthesisResult(BaseModel):
    text: str
    audioUrl: str
    engine: str


class VoiceSettings(BaseModel):
    asrEngine: str
    ttsEngine: str
    fallbackMode: str
    saveRawAudio: bool
    maxRecordingSeconds: int
    childSafetyNotes: list[str]


class VoicePlan(BaseModel):
    input: str
    output: str
    recommendation: str
    notes: list[str]


class UserAccount(BaseModel):
    id: str
    email: str = ""
    displayName: str
    role: str = "parent"
    createdAt: str = ""


class AuthRegisterRequest(BaseModel):
    email: str = Field(min_length=3, max_length=120)
    password: str = Field(min_length=6, max_length=120)
    displayName: str = Field(min_length=1, max_length=80)
    role: str = Field(default="parent", pattern="^(parent|teacher|admin)$")


class AuthLoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=120)
    password: str = Field(min_length=1, max_length=120)


class AuthToken(BaseModel):
    accessToken: str
    tokenType: str = "bearer"
    user: UserAccount


class ChildProfile(BaseModel):
    id: str
    userId: str = "demo-parent"
    name: str = Field(min_length=1)
    age: int = Field(ge=3, le=18)
    grade: str = ""
    avatar: str = "🦊"
    debateGoal: str = "每次表达都说清观点和理由。"
    createdAt: str = ""


class DebateConversationTurn(BaseModel):
    speaker: str
    text: str
    badge: str = ""
    audioUrl: str = ""
    source: str = "text"
    createdAt: str = ""
    rubric: Rubric | None = None


class PracticeSessionStartRequest(BaseModel):
    topicId: str = Field(min_length=1)
    side: str = Field(pattern="^(正方|反方)$")
    childId: str | None = None


class PracticeTurnCreateRequest(BaseModel):
    speaker: str = Field(pattern="^(kid|coach|system)$")
    text: str = Field(min_length=1, max_length=2000)
    badge: str = ""
    audioUrl: str = ""
    source: str = "text"
    rubric: Rubric | None = None


class PracticeSessionFinishRequest(BaseModel):
    summary: str = ""


class PracticeTurn(BaseModel):
    id: str
    sessionId: str
    speaker: str
    text: str
    badge: str = ""
    audioUrl: str = ""
    source: str = "text"
    rubric: Rubric | None = None
    createdAt: str


class PracticeSession(BaseModel):
    id: str
    childId: str | None = None
    topicId: str
    side: str
    startedAt: str
    endedAt: str | None = None
    durationSeconds: int = 0
    summary: str = ""
    totalTurns: int = 0
    averageRubric: Rubric | None = None
    turns: list[PracticeTurn] = Field(default_factory=list)


class DebateSession(BaseModel):
    id: str
    practiceSessionId: str = ""
    childId: str | None = None
    topicId: str
    side: str
    message: str
    coachReply: str
    nextPrompt: str
    rubric: Rubric
    createdAt: str
    durationMinutes: int = 5
    durationSeconds: int = 0
    startedAt: str = ""
    endedAt: str | None = None
    summary: str = ""
    totalTurns: int = 0
    conversation: list[DebateConversationTurn] = Field(default_factory=list)


class ProviderConfig(BaseModel):
    enabled: bool
    baseUrl: str
    model: str
    apiKey: str = ""


class IntegrationSettings(BaseModel):
    llm: ProviderConfig
    asr: ProviderConfig
    tts: ProviderConfig
    updatedAt: str = ""
