from .models import CoachResponse, DebateRequest, DebateTopic, GrowthReport, ReportMetric, Rubric

DEMO_REPORT = GrowthReport(
    childName="小辩手",
    weekLabel="本周练习报告",
    completedDebates=3,
    streakDays=2,
    metrics=[
        ReportMetric(key="clarity", title="表达清楚度", score=86, hint="能说出观点，下一步练习把理由分成第一、第二。"),
        ReportMetric(key="evidence", title="理由与例子", score=74, hint="已经会说“因为”，继续补生活例子会更有说服力。"),
        ReportMetric(key="manners", title="礼貌回应", score=90, hint="能用“我理解你的担心”回应对方，保持温和语气。"),
    ],
    coachNote="孩子已经能说清楚观点，建议下一轮练习时要求每次发言都补一个生活中的小例子。",
    nextGoal="每次发言都加入一个具体例子。",
)


def _score_message(message: str) -> Rubric:
    has_reason = any(word in message for word in ["因为", "理由", "所以", "原因"])
    has_example = any(word in message for word in ["例如", "比如", "例子", "我经历"])
    has_manners = any(word in message for word in ["我同意", "谢谢", "请", "对方", "补充"])

    clarity = min(96, 58 + len(message) // 8 + (12 if has_reason else 0))
    evidence = min(96, 48 + (24 if has_reason else 0) + (18 if has_example else 0))
    manners = min(96, 62 + (24 if has_manners else 0))
    return Rubric(clarity=clarity, evidence=evidence, manners=manners)


def coach_reply(request: DebateRequest) -> CoachResponse:
    rubric = _score_message(request.message)
    reason_hint = "你已经说出了观点。下一句可以加上“因为……”让理由更清楚。"
    if "因为" in request.message or "理由" in request.message:
        reason_hint = "你的理由很清楚！如果再加一个生活里的小例子，说服力会更强。"
    if any(word in request.message for word in ["例如", "比如", "例子"]):
        reason_hint = "你用了例子，这是很棒的辩论习惯。接下来试试回应对方可能的担心。"

    return CoachResponse(
        reply=f"{request.side}小辩手，我听到了你的观点：{request.message[:80]}。{reason_hint}",
        rubric=rubric,
        nextPrompt="请用一句礼貌的话回应反方/正方可能提出的问题，例如“我理解你的担心，不过……”。",
    )


def filter_topics(
    topics: list[DebateTopic] | None = None,
    collection_id: str | None = None,
    age_range: str | None = None,
    difficulty: str | None = None,
    tag: str | None = None,
    q: str | None = None,
) -> list[DebateTopic]:
    filtered = topics or []
    if collection_id:
        filtered = [topic for topic in filtered if topic.collectionId == collection_id]
    if age_range:
        filtered = [topic for topic in filtered if topic.ageRange == age_range]
    if difficulty:
        filtered = [topic for topic in filtered if topic.difficulty == difficulty]
    if tag:
        filtered = [topic for topic in filtered if tag in topic.tags]
    if q:
        keyword = q.strip().lower()
        if keyword:
            filtered = [
                topic
                for topic in filtered
                if keyword in " ".join(
                    [
                        topic.title,
                        topic.sideA,
                        topic.sideB,
                        topic.background,
                        " ".join(topic.tags),
                        " ".join(topic.starterTips),
                    ]
                ).lower()
            ]
    return filtered
