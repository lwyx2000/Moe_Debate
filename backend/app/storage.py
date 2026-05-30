from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import uuid
from datetime import UTC, datetime
from typing import Any, Iterable

from .config import database_config
from .models import AuthRegisterRequest, AuthToken, ChildProfile, CoachResponse, DebateRequest, DebateSession, DebateTopic, GrowthReport, IntegrationSettings, PracticeSession, PracticeSessionStartRequest, PracticeTurn, PracticeTurnCreateRequest, ProviderConfig, ReportMetric, Rubric, TopicCollection, TrendPoint, UserAccount

BIZ_APP_SETTINGS = "biz_app_settings"
BIZ_DEBATE_SESSIONS = "biz_debate_sessions"
BIZ_PRACTICE_SESSIONS = "biz_practice_sessions"
BIZ_PRACTICE_TURNS = "biz_practice_turns"
BIZ_DEBATE_TOPICS = "biz_debate_topics"
BIZ_TOPIC_COLLECTIONS = "biz_topic_collections"
BIZ_USERS = "biz_users"
BIZ_CHILD_PROFILES = "biz_child_profiles"
BIZ_AUTH_TOKENS = "biz_auth_tokens"
BIZ_TOPIC_FAVORITES = "biz_topic_favorites"


class DbConnection:
    def __init__(self, *, database: str | None = None) -> None:
        import pymysql
        from pymysql.cursors import DictCursor

        config = database_config()
        self._connection = pymysql.connect(
            host=config.host,
            port=config.port,
            user=config.user,
            password=config.password,
            database=database if database is not None else config.database,
            charset=config.charset,
            cursorclass=DictCursor,
            autocommit=False,
        )

    def __enter__(self) -> "DbConnection":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if exc_type is None:
            self._connection.commit()
        else:
            self._connection.rollback()
        self._connection.close()

    def execute(self, sql: str, params: Iterable[Any] | None = None) -> Any:
        cursor = self._connection.cursor()
        cursor.execute(sql, tuple(params or ()))
        return cursor

    def executemany(self, sql: str, params: Iterable[Iterable[Any]]) -> Any:
        cursor = self._connection.cursor()
        cursor.executemany(sql, list(params))
        return cursor


def _ensure_database() -> None:
    config = database_config()
    with DbConnection(database=None) as connection:
        connection.execute(f"CREATE DATABASE IF NOT EXISTS `{config.database}` CHARACTER SET {config.charset} COLLATE {config.charset}_unicode_ci")


def _connect() -> DbConnection:
    _ensure_database()
    return DbConnection()


def _column_exists(connection: DbConnection, table: str, column: str) -> bool:
    row = connection.execute(
        """
        SELECT COUNT(*) AS total
        FROM information_schema.columns
        WHERE table_schema = DATABASE() AND table_name = %s AND column_name = %s
        """,
        (table, column),
    ).fetchone()
    return bool(row and row["total"])


def init_db() -> None:
    with _connect() as connection:
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {BIZ_APP_SETTINGS} (
                setting_key VARCHAR(120) NOT NULL,
                value_json LONGTEXT NOT NULL,
                updated_at VARCHAR(40) NOT NULL,
                CONSTRAINT pk_app_settings PRIMARY KEY (setting_key)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        )
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {BIZ_USERS} (
                id VARCHAR(64) NOT NULL,
                email VARCHAR(120) NOT NULL DEFAULT '',
                display_name VARCHAR(120) NOT NULL,
                role VARCHAR(32) NOT NULL,
                password_hash VARCHAR(255) NOT NULL DEFAULT '',
                created_at VARCHAR(40) NOT NULL,
                CONSTRAINT pk_users PRIMARY KEY (id),
                CONSTRAINT uq_users_email UNIQUE (email)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        )
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {BIZ_TOPIC_COLLECTIONS} (
                id VARCHAR(64) NOT NULL,
                icon VARCHAR(16) NOT NULL,
                title VARCHAR(160) NOT NULL,
                description TEXT NOT NULL,
                updated_at VARCHAR(40) NOT NULL,
                CONSTRAINT pk_topic_collections PRIMARY KEY (id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        )
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {BIZ_DEBATE_TOPICS} (
                id VARCHAR(64) NOT NULL,
                title VARCHAR(240) NOT NULL,
                side_a VARCHAR(240) NOT NULL,
                side_b VARCHAR(240) NOT NULL,
                starter_tips_json LONGTEXT NOT NULL,
                collection_id VARCHAR(64) NOT NULL,
                age_range VARCHAR(32) NOT NULL,
                difficulty VARCHAR(32) NOT NULL,
                tags_json LONGTEXT NOT NULL,
                background TEXT NOT NULL,
                side_a_tips_json LONGTEXT NOT NULL,
                side_b_tips_json LONGTEXT NOT NULL,
                examples_json LONGTEXT NOT NULL,
                updated_at VARCHAR(40) NOT NULL,
                CONSTRAINT pk_debate_topics PRIMARY KEY (id),
                CONSTRAINT fk_debate_topics_topic_collections FOREIGN KEY (collection_id) REFERENCES biz_topic_collections(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        )
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {BIZ_CHILD_PROFILES} (
                id VARCHAR(64) NOT NULL,
                user_id VARCHAR(64) NOT NULL,
                name VARCHAR(120) NOT NULL,
                age INT NOT NULL,
                grade VARCHAR(80) NOT NULL,
                avatar VARCHAR(16) NOT NULL,
                debate_goal TEXT NOT NULL,
                created_at VARCHAR(40) NOT NULL,
                CONSTRAINT pk_child_profiles PRIMARY KEY (id),
                CONSTRAINT fk_child_profiles_users FOREIGN KEY (user_id) REFERENCES biz_users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        )
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {BIZ_DEBATE_SESSIONS} (
                id VARCHAR(64) NOT NULL,
                child_id VARCHAR(64) NULL,
                topic_id VARCHAR(64) NOT NULL,
                side VARCHAR(16) NOT NULL,
                message TEXT NOT NULL,
                coach_reply TEXT NOT NULL,
                next_prompt TEXT NOT NULL,
                rubric_json LONGTEXT NOT NULL,
                duration_minutes INT NOT NULL DEFAULT 5,
                practice_session_id VARCHAR(64) NULL,
                created_at VARCHAR(40) NOT NULL,
                CONSTRAINT pk_debate_sessions PRIMARY KEY (id),
                CONSTRAINT fk_debate_sessions_child_profiles FOREIGN KEY (child_id) REFERENCES biz_child_profiles(id) ON DELETE SET NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        )
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {BIZ_PRACTICE_SESSIONS} (
                id VARCHAR(64) NOT NULL,
                child_id VARCHAR(64) NULL,
                topic_id VARCHAR(64) NOT NULL,
                side VARCHAR(16) NOT NULL,
                started_at VARCHAR(40) NOT NULL,
                ended_at VARCHAR(40) NULL,
                duration_seconds INT NOT NULL DEFAULT 0,
                summary TEXT NOT NULL,
                created_at VARCHAR(40) NOT NULL,
                CONSTRAINT pk_practice_sessions PRIMARY KEY (id),
                CONSTRAINT fk_practice_sessions_child_profiles FOREIGN KEY (child_id) REFERENCES biz_child_profiles(id) ON DELETE SET NULL,
                CONSTRAINT fk_practice_sessions_debate_topics FOREIGN KEY (topic_id) REFERENCES biz_debate_topics(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        )
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {BIZ_PRACTICE_TURNS} (
                id VARCHAR(64) NOT NULL,
                session_id VARCHAR(64) NOT NULL,
                speaker VARCHAR(24) NOT NULL,
                text TEXT NOT NULL,
                badge VARCHAR(80) NOT NULL DEFAULT '',
                audio_url TEXT NOT NULL,
                source VARCHAR(40) NOT NULL DEFAULT 'text',
                rubric_json LONGTEXT NULL,
                created_at VARCHAR(40) NOT NULL,
                CONSTRAINT pk_practice_turns PRIMARY KEY (id),
                CONSTRAINT fk_practice_turns_practice_sessions FOREIGN KEY (session_id) REFERENCES biz_practice_sessions(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        )
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {BIZ_AUTH_TOKENS} (
                token VARCHAR(160) NOT NULL,
                user_id VARCHAR(64) NOT NULL,
                created_at VARCHAR(40) NOT NULL,
                CONSTRAINT pk_auth_tokens PRIMARY KEY (token),
                CONSTRAINT fk_auth_tokens_users FOREIGN KEY (user_id) REFERENCES biz_users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        )
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {BIZ_TOPIC_FAVORITES} (
                user_id VARCHAR(64) NOT NULL,
                topic_id VARCHAR(64) NOT NULL,
                created_at VARCHAR(40) NOT NULL,
                CONSTRAINT pk_topic_favorites PRIMARY KEY (user_id, topic_id),
                CONSTRAINT fk_topic_favorites_users FOREIGN KEY (user_id) REFERENCES biz_users(id) ON DELETE CASCADE,
                CONSTRAINT fk_topic_favorites_debate_topics FOREIGN KEY (topic_id) REFERENCES biz_debate_topics(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        )
        if not _column_exists(connection, BIZ_USERS, "email"):
            connection.execute(f"ALTER TABLE {BIZ_USERS} ADD COLUMN email VARCHAR(120) NOT NULL DEFAULT ''")
        if not _column_exists(connection, BIZ_USERS, "password_hash"):
            connection.execute(f"ALTER TABLE {BIZ_USERS} ADD COLUMN password_hash VARCHAR(255) NOT NULL DEFAULT ''")
        if not _column_exists(connection, BIZ_DEBATE_SESSIONS, "child_id"):
            connection.execute(f"ALTER TABLE {BIZ_DEBATE_SESSIONS} ADD COLUMN child_id VARCHAR(64) NULL")
        if not _column_exists(connection, BIZ_DEBATE_SESSIONS, "duration_minutes"):
            connection.execute(f"ALTER TABLE {BIZ_DEBATE_SESSIONS} ADD COLUMN duration_minutes INT NOT NULL DEFAULT 5")
        if not _column_exists(connection, BIZ_DEBATE_SESSIONS, "practice_session_id"):
            connection.execute(f"ALTER TABLE {BIZ_DEBATE_SESSIONS} ADD COLUMN practice_session_id VARCHAR(64) NULL")


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _elapsed_seconds(started_at: str, ended_at: str | None, stored_duration: int = 0) -> int:
    if stored_duration > 0:
        return stored_duration
    started = _parse_dt(started_at)
    ended = _parse_dt(ended_at) or datetime.now(UTC)
    if started is None:
        return 0
    return max(0, round((ended - started).total_seconds()))


def _row_to_practice_turn(row: dict[str, Any]) -> PracticeTurn:
    rubric = Rubric(**json.loads(row["rubric_json"])) if row.get("rubric_json") else None
    return PracticeTurn(
        id=row["id"],
        sessionId=row["session_id"],
        speaker=row["speaker"],
        text=row["text"],
        badge=row.get("badge") or "",
        audioUrl=row.get("audio_url") or "",
        source=row.get("source") or "text",
        rubric=rubric,
        createdAt=row["created_at"],
    )


def _list_practice_turns(connection: DbConnection, session_id: str) -> list[PracticeTurn]:
    rows = connection.execute(
        f"SELECT * FROM {BIZ_PRACTICE_TURNS} WHERE session_id = %s ORDER BY created_at ASC",
        (session_id,),
    ).fetchall()
    return [_row_to_practice_turn(row) for row in rows]


def _average_rubric(turns: list[PracticeTurn]) -> Rubric | None:
    scored = [turn.rubric for turn in turns if turn.rubric is not None]
    if not scored:
        return None
    count = len(scored)
    return Rubric(
        clarity=round(sum(rubric.clarity for rubric in scored) / count),
        evidence=round(sum(rubric.evidence for rubric in scored) / count),
        manners=round(sum(rubric.manners for rubric in scored) / count),
    )


def _conversation_from_turns(turns: list[PracticeTurn]) -> list[dict[str, Any]]:
    return [
        {
            "speaker": turn.speaker,
            "badge": turn.badge,
            "text": turn.text,
            "audioUrl": turn.audioUrl,
            "source": turn.source,
            "createdAt": turn.createdAt,
            "rubric": turn.rubric,
        }
        for turn in turns
    ]


def _row_to_practice_session(row: dict[str, Any], turns: list[PracticeTurn]) -> PracticeSession:
    duration_seconds = _elapsed_seconds(row["started_at"], row.get("ended_at"), row.get("duration_seconds") or 0)
    return PracticeSession(
        id=row["id"],
        childId=row.get("child_id"),
        topicId=row["topic_id"],
        side=row["side"],
        startedAt=row["started_at"],
        endedAt=row.get("ended_at"),
        durationSeconds=duration_seconds,
        summary=row.get("summary") or "",
        totalTurns=len(turns),
        averageRubric=_average_rubric(turns),
        turns=turns,
    )


def _practice_session_to_debate_session(row: dict[str, Any], turns: list[PracticeTurn]) -> DebateSession:
    kid_turns = [turn for turn in turns if turn.speaker == "kid"]
    coach_turns = [turn for turn in turns if turn.speaker == "coach"]
    latest_kid = kid_turns[-1] if kid_turns else None
    latest_coach = coach_turns[-1] if coach_turns else None
    rubric = _average_rubric(turns) or Rubric(clarity=0, evidence=0, manners=0)
    duration_seconds = _elapsed_seconds(row["started_at"], row.get("ended_at"), row.get("duration_seconds") or 0)
    return DebateSession(
        id=row["id"],
        practiceSessionId=row["id"],
        childId=row.get("child_id"),
        topicId=row["topic_id"],
        side=row["side"],
        message=latest_kid.text if latest_kid else "",
        coachReply=latest_coach.text if latest_coach else "",
        nextPrompt=row.get("summary") or "继续补充一个具体例子。",
        rubric=rubric,
        createdAt=row["started_at"],
        durationMinutes=max(1, (duration_seconds + 59) // 60) if turns else 0,
        durationSeconds=duration_seconds,
        startedAt=row["started_at"],
        endedAt=row.get("ended_at"),
        summary=row.get("summary") or "",
        totalTurns=len(turns),
        conversation=_conversation_from_turns(turns),
    )


def _row_to_session(row: dict[str, Any]) -> DebateSession:
    rubric_data = json.loads(row["rubric_json"])
    conversation = [
        {"speaker": "kid", "badge": row["side"], "text": row["message"], "source": "text", "createdAt": row["created_at"]},
        {"speaker": "coach", "badge": "小鹿教练", "text": row["coach_reply"], "source": "coach", "createdAt": row["created_at"], "rubric": Rubric(**rubric_data)},
        {"speaker": "coach", "badge": "下一步", "text": row["next_prompt"], "source": "coach", "createdAt": row["created_at"]},
    ]
    return DebateSession(
        id=row["id"],
        practiceSessionId=row.get("practice_session_id") or row["id"],
        childId=row.get("child_id"),
        topicId=row["topic_id"],
        side=row["side"],
        message=row["message"],
        coachReply=row["coach_reply"],
        nextPrompt=row["next_prompt"],
        rubric=Rubric(**rubric_data),
        createdAt=row["created_at"],
        durationMinutes=row.get("duration_minutes", 5),
        durationSeconds=(row.get("duration_minutes", 5) or 5) * 60,
        startedAt=row["created_at"],
        endedAt=row["created_at"],
        summary=row["next_prompt"],
        totalTurns=len(conversation),
        conversation=conversation,
    )



def _ensure_topic_seed_for_session(topic_id: str) -> None:
    init_db()
    with _connect() as connection:
        row = connection.execute(f"SELECT id FROM {BIZ_DEBATE_TOPICS} WHERE id = %s", (topic_id,)).fetchone()
    if row is None:
        from .topic_seed import load_seed_collections, load_seed_topics

        seed_topic_bank_if_empty(load_seed_topics(), load_seed_collections())

def create_practice_session(payload: PracticeSessionStartRequest) -> PracticeSession:
    init_db()
    _ensure_topic_seed_for_session(payload.topicId)
    session_id = str(uuid.uuid4())
    started_at = datetime.now(UTC).isoformat()
    with _connect() as connection:
        connection.execute(
            f"""
            INSERT INTO {BIZ_PRACTICE_SESSIONS} (id, child_id, topic_id, side, started_at, ended_at, duration_seconds, summary, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (session_id, payload.childId, payload.topicId, payload.side, started_at, None, 0, "", started_at),
        )
        row = connection.execute(f"SELECT * FROM {BIZ_PRACTICE_SESSIONS} WHERE id = %s", (session_id,)).fetchone()
        return _row_to_practice_session(row, [])


def append_practice_turn(session_id: str, payload: PracticeTurnCreateRequest) -> PracticeTurn | None:
    init_db()
    turn_id = str(uuid.uuid4())
    created_at = datetime.now(UTC).isoformat()
    rubric_json = payload.rubric.model_dump_json() if payload.rubric else None
    with _connect() as connection:
        session = connection.execute(f"SELECT id FROM {BIZ_PRACTICE_SESSIONS} WHERE id = %s", (session_id,)).fetchone()
        if session is None:
            return None
        connection.execute(
            f"""
            INSERT INTO {BIZ_PRACTICE_TURNS} (id, session_id, speaker, text, badge, audio_url, source, rubric_json, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (turn_id, session_id, payload.speaker, payload.text, payload.badge, payload.audioUrl, payload.source, rubric_json, created_at),
        )
        row = connection.execute(f"SELECT * FROM {BIZ_PRACTICE_TURNS} WHERE id = %s", (turn_id,)).fetchone()
    return _row_to_practice_turn(row) if row else None


def get_practice_session(session_id: str) -> PracticeSession | None:
    init_db()
    with _connect() as connection:
        row = connection.execute(f"SELECT * FROM {BIZ_PRACTICE_SESSIONS} WHERE id = %s", (session_id,)).fetchone()
        if row is None:
            return None
        turns = _list_practice_turns(connection, session_id)
    return _row_to_practice_session(row, turns)


def finish_practice_session(session_id: str, summary: str = "") -> PracticeSession | None:
    init_db()
    ended_at = datetime.now(UTC).isoformat()
    with _connect() as connection:
        row = connection.execute(f"SELECT * FROM {BIZ_PRACTICE_SESSIONS} WHERE id = %s", (session_id,)).fetchone()
        if row is None:
            return None
        duration_seconds = _elapsed_seconds(row["started_at"], ended_at, 0)
        turns = _list_practice_turns(connection, session_id)
        summary_text = summary or row.get("summary") or _summary_from_turns(turns)
        connection.execute(
            f"UPDATE {BIZ_PRACTICE_SESSIONS} SET ended_at = %s, duration_seconds = %s, summary = %s WHERE id = %s",
            (ended_at, duration_seconds, summary_text, session_id),
        )
        updated = connection.execute(f"SELECT * FROM {BIZ_PRACTICE_SESSIONS} WHERE id = %s", (session_id,)).fetchone()
        turns = _list_practice_turns(connection, session_id)
    return _row_to_practice_session(updated, turns)


def _summary_from_turns(turns: list[PracticeTurn], fallback: str = "继续补充一个具体例子。") -> str:
    coach_turns = [turn.text for turn in turns if turn.speaker == "coach"]
    if not coach_turns:
        return fallback
    latest = coach_turns[-1].replace("\n", " ").strip()
    return latest[:180] or fallback


def _ensure_practice_session_for_debate(request: DebateRequest) -> PracticeSession:
    if request.practiceSessionId:
        existing = get_practice_session(request.practiceSessionId)
        if existing is not None:
            return existing
    return create_practice_session(PracticeSessionStartRequest(topicId=request.topicId, side=request.side, childId=request.childId))


def save_debate_session(request: DebateRequest, response: CoachResponse) -> DebateSession:
    init_db()
    practice_session = _ensure_practice_session_for_debate(request)
    append_practice_turn(
        practice_session.id,
        PracticeTurnCreateRequest(speaker="kid", text=request.message, badge=request.side, source="text"),
    )
    coach_text = f"{response.reply}\n\n下一步：{response.nextPrompt}"
    append_practice_turn(
        practice_session.id,
        PracticeTurnCreateRequest(speaker="coach", text=coach_text, badge="小鹿教练", source="coach", rubric=response.rubric),
    )
    turns = get_practice_session(practice_session.id).turns if get_practice_session(practice_session.id) else []
    summary = _summary_from_turns(turns, response.nextPrompt)

    session_id = str(uuid.uuid4())
    created_at = datetime.now(UTC).isoformat()
    rubric_json = response.rubric.model_dump_json()

    with _connect() as connection:
        connection.execute(
            f"""
            INSERT INTO {BIZ_DEBATE_SESSIONS} (
                id, child_id, topic_id, side, message, coach_reply, next_prompt, rubric_json, duration_minutes, practice_session_id, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (session_id, request.childId, request.topicId, request.side, request.message, response.reply, response.nextPrompt, rubric_json, 1, practice_session.id, created_at),
        )
        connection.execute(f"UPDATE {BIZ_PRACTICE_SESSIONS} SET summary = %s WHERE id = %s", (summary, practice_session.id))

    session = get_debate_session(practice_session.id)
    if session is not None:
        return session
    return DebateSession(
        id=practice_session.id,
        practiceSessionId=practice_session.id,
        childId=request.childId,
        topicId=request.topicId,
        side=request.side,
        message=request.message,
        coachReply=response.reply,
        nextPrompt=response.nextPrompt,
        rubric=response.rubric,
        createdAt=created_at,
        durationMinutes=1,
        durationSeconds=60,
        startedAt=practice_session.startedAt,
        summary=summary,
        totalTurns=2,
        conversation=[
            {"speaker": "kid", "badge": request.side, "text": request.message, "source": "text", "createdAt": created_at},
            {"speaker": "coach", "badge": "小鹿教练", "text": coach_text, "source": "coach", "createdAt": created_at, "rubric": response.rubric},
        ],
    )


def _session_filter_sql(
    *,
    child_id: str | None = None,
    child_ids: list[str] | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    topic_id: str | None = None,
    collection_id: str | None = None,
) -> tuple[str, list[Any]]:
    clauses: list[str] = []
    params: list[Any] = []
    if child_id:
        clauses.append("sessions.child_id = %s")
        params.append(child_id)
    if child_ids is not None:
        if not child_ids:
            clauses.append("1 = 0")
        else:
            clauses.append(f"sessions.child_id IN ({','.join('%s' for _ in child_ids)})")
            params.extend(child_ids)
    if date_from:
        clauses.append("sessions.created_at >= %s")
        params.append(f"{date_from}T00:00:00")
    if date_to:
        clauses.append("sessions.created_at <= %s")
        params.append(f"{date_to}T23:59:59")
    if topic_id:
        clauses.append("sessions.topic_id = %s")
        params.append(topic_id)
    if collection_id:
        clauses.append("topics.collection_id = %s")
        params.append(collection_id)
    return (" WHERE " + " AND ".join(clauses)) if clauses else "", params


def _rows_to_debate_sessions(connection: DbConnection, rows: list[dict[str, Any]]) -> list[DebateSession]:
    sessions: list[DebateSession] = []
    for row in rows:
        turns = _list_practice_turns(connection, row["id"])
        sessions.append(_practice_session_to_debate_session(row, turns))
    return sessions


def list_debate_sessions(
    limit: int = 20,
    child_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    topic_id: str | None = None,
    collection_id: str | None = None,
) -> list[DebateSession]:
    init_db()
    where_sql, params = _session_filter_sql(child_id=child_id, date_from=date_from, date_to=date_to, topic_id=topic_id, collection_id=collection_id)
    with _connect() as connection:
        rows = connection.execute(
            f"""
            SELECT sessions.* FROM {BIZ_PRACTICE_SESSIONS} sessions
            LEFT JOIN {BIZ_DEBATE_TOPICS} topics ON topics.id = sessions.topic_id
            {where_sql}
            ORDER BY sessions.created_at DESC
            LIMIT %s
            """,
            (*params, limit),
        ).fetchall()
        if rows:
            return _rows_to_debate_sessions(connection, rows)
        legacy_rows = connection.execute(
            f"""
            SELECT sessions.* FROM {BIZ_DEBATE_SESSIONS} sessions
            LEFT JOIN {BIZ_DEBATE_TOPICS} topics ON topics.id = sessions.topic_id
            {where_sql}
            ORDER BY sessions.created_at DESC
            LIMIT %s
            """,
            (*params, limit),
        ).fetchall()
        return [_row_to_session(row) for row in legacy_rows]


def list_debate_sessions_for_children(
    child_ids: list[str],
    limit: int = 20,
    date_from: str | None = None,
    date_to: str | None = None,
    topic_id: str | None = None,
    collection_id: str | None = None,
) -> list[DebateSession]:
    init_db()
    where_sql, params = _session_filter_sql(child_ids=child_ids, date_from=date_from, date_to=date_to, topic_id=topic_id, collection_id=collection_id)
    with _connect() as connection:
        rows = connection.execute(
            f"""
            SELECT sessions.* FROM {BIZ_PRACTICE_SESSIONS} sessions
            LEFT JOIN {BIZ_DEBATE_TOPICS} topics ON topics.id = sessions.topic_id
            {where_sql}
            ORDER BY sessions.created_at DESC
            LIMIT %s
            """,
            (*params, limit),
        ).fetchall()
        if rows:
            return _rows_to_debate_sessions(connection, rows)
        legacy_rows = connection.execute(
            f"""
            SELECT sessions.* FROM {BIZ_DEBATE_SESSIONS} sessions
            LEFT JOIN {BIZ_DEBATE_TOPICS} topics ON topics.id = sessions.topic_id
            {where_sql}
            ORDER BY sessions.created_at DESC
            LIMIT %s
            """,
            (*params, limit),
        ).fetchall()
        return [_row_to_session(row) for row in legacy_rows]


def get_debate_session(session_id: str) -> DebateSession | None:
    init_db()
    with _connect() as connection:
        row = connection.execute(f"SELECT * FROM {BIZ_PRACTICE_SESSIONS} WHERE id = %s", (session_id,)).fetchone()
        if row is not None:
            return _practice_session_to_debate_session(row, _list_practice_turns(connection, session_id))
        legacy = connection.execute(f"SELECT * FROM {BIZ_DEBATE_SESSIONS} WHERE id = %s", (session_id,)).fetchone()
    return _row_to_session(legacy) if legacy else None


def _row_to_user(row: dict[str, Any]) -> UserAccount:
    return UserAccount(id=row["id"], email=row["email"], displayName=row["display_name"], role=row["role"], createdAt=row["created_at"])


def _row_to_child_profile(row: dict[str, Any]) -> ChildProfile:
    return ChildProfile(
        id=row["id"],
        userId=row["user_id"],
        name=row["name"],
        age=row["age"],
        grade=row["grade"],
        avatar=row["avatar"],
        debateGoal=row["debate_goal"],
        createdAt=row["created_at"],
    )


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000).hex()
    return f"pbkdf2_sha256${salt}${digest}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, salt, expected = password_hash.split("$", 2)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    actual = hash_password(password, salt).split("$", 2)[2]
    return hmac.compare_digest(actual, expected)


def get_user_by_email(email: str) -> UserAccount | None:
    init_db()
    with _connect() as connection:
        row = connection.execute(f"SELECT * FROM {BIZ_USERS} WHERE LOWER(email) = LOWER(%s)", (email.strip(),)).fetchone()
    return _row_to_user(row) if row else None


def get_user_by_id(user_id: str) -> UserAccount | None:
    init_db()
    with _connect() as connection:
        row = connection.execute(f"SELECT * FROM {BIZ_USERS} WHERE id = %s", (user_id,)).fetchone()
    return _row_to_user(row) if row else None


def create_user(payload: AuthRegisterRequest) -> UserAccount:
    init_db()
    created_at = datetime.now(UTC).isoformat()
    user = UserAccount(id=str(uuid.uuid4()), email=payload.email.strip().lower(), displayName=payload.displayName.strip(), role=payload.role, createdAt=created_at)
    with _connect() as connection:
        connection.execute(
            f"INSERT INTO {BIZ_USERS} (id, email, display_name, role, password_hash, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
            (user.id, user.email, user.displayName, user.role, hash_password(payload.password), user.createdAt),
        )
    return user


def authenticate_user(email: str, password: str) -> UserAccount | None:
    seed_demo_user_if_empty()
    with _connect() as connection:
        row = connection.execute(f"SELECT * FROM {BIZ_USERS} WHERE LOWER(email) = LOWER(%s)", (email.strip(),)).fetchone()
    if row is None or not verify_password(password, row["password_hash"]):
        return None
    return _row_to_user(row)


def create_auth_token(user: UserAccount) -> AuthToken:
    init_db()
    token = secrets.token_urlsafe(32)
    created_at = datetime.now(UTC).isoformat()
    with _connect() as connection:
        connection.execute(f"INSERT INTO {BIZ_AUTH_TOKENS} (token, user_id, created_at) VALUES (%s, %s, %s)", (token, user.id, created_at))
    return AuthToken(accessToken=token, user=user)


def get_user_by_token(token: str) -> UserAccount | None:
    init_db()
    with _connect() as connection:
        row = connection.execute(
            f"""
            SELECT users.* FROM {BIZ_AUTH_TOKENS} tokens
            JOIN {BIZ_USERS} users ON users.id = tokens.user_id
            WHERE tokens.token = %s
            """,
            (token,),
        ).fetchone()
    return _row_to_user(row) if row else None


def revoke_auth_token(token: str) -> bool:
    init_db()
    with _connect() as connection:
        cursor = connection.execute(f"DELETE FROM {BIZ_AUTH_TOKENS} WHERE token = %s", (token,))
    return cursor.rowcount > 0


def seed_demo_user_if_empty() -> None:
    init_db()
    with _connect() as connection:
        created_at = datetime.now(UTC).isoformat()
        demo_user = connection.execute(f"SELECT * FROM {BIZ_USERS} WHERE id = %s", ("demo-parent",)).fetchone()
        if demo_user is None:
            connection.execute(
                f"INSERT INTO {BIZ_USERS} (id, email, display_name, role, password_hash, created_at) VALUES (%s, %s, %s, %s, %s, %s)",
                ("demo-parent", "demo@example.com", "家长/老师", "admin", hash_password("demo123456"), created_at),
            )
        else:
            connection.execute(
                f"""
                UPDATE {BIZ_USERS}
                SET email = CASE WHEN email = '' THEN %s ELSE email END,
                    password_hash = CASE WHEN password_hash = '' THEN %s ELSE password_hash END,
                    role = CASE WHEN role = 'parent' THEN 'admin' ELSE role END
                WHERE id = %s
                """,
                ("demo@example.com", hash_password("demo123456"), "demo-parent"),
            )

        demo_child = connection.execute(f"SELECT * FROM {BIZ_CHILD_PROFILES} WHERE id = %s", ("demo-child",)).fetchone()
        if demo_child is None:
            connection.execute(
                f"""
                INSERT INTO {BIZ_CHILD_PROFILES} (id, user_id, name, age, grade, avatar, debate_goal, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                ("demo-child", "demo-parent", "小辩手", 8, "二年级", "🦊", "每次表达都说清观点和理由。", created_at),
            )


def get_demo_user() -> UserAccount:
    seed_demo_user_if_empty()
    with _connect() as connection:
        row = connection.execute(f"SELECT * FROM {BIZ_USERS} WHERE id = %s", ("demo-parent",)).fetchone()
    return _row_to_user(row)


def list_child_profiles(user_id: str = "demo-parent") -> list[ChildProfile]:
    seed_demo_user_if_empty()
    with _connect() as connection:
        rows = connection.execute(f"SELECT * FROM {BIZ_CHILD_PROFILES} WHERE user_id = %s ORDER BY created_at ASC", (user_id,)).fetchall()
    return [_row_to_child_profile(row) for row in rows]


def get_child_profile(child_id: str) -> ChildProfile | None:
    init_db()
    with _connect() as connection:
        row = connection.execute(f"SELECT * FROM {BIZ_CHILD_PROFILES} WHERE id = %s", (child_id,)).fetchone()
    return _row_to_child_profile(row) if row else None


def save_child_profile(profile: ChildProfile) -> ChildProfile:
    seed_demo_user_if_empty()
    created_at = profile.createdAt or datetime.now(UTC).isoformat()
    saved = profile.model_copy(update={"createdAt": created_at})
    with _connect() as connection:
        connection.execute(
            f"""
            INSERT INTO {BIZ_CHILD_PROFILES} (id, user_id, name, age, grade, avatar, debate_goal, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                user_id = VALUES(user_id),
                name = VALUES(name),
                age = VALUES(age),
                grade = VALUES(grade),
                avatar = VALUES(avatar),
                debate_goal = VALUES(debate_goal)
            """,
            (saved.id, saved.userId, saved.name, saved.age, saved.grade, saved.avatar, saved.debateGoal, saved.createdAt),
        )
    return saved


def delete_child_profile(child_id: str) -> bool:
    init_db()
    with _connect() as connection:
        cursor = connection.execute(f"DELETE FROM {BIZ_CHILD_PROFILES} WHERE id = %s", (child_id,))
    return cursor.rowcount > 0


DEFAULT_INTEGRATION_SETTINGS = IntegrationSettings(
    llm=ProviderConfig(enabled=False, baseUrl="https://api.openai.com/v1", model="gpt-4o-mini", apiKey=""),
    asr=ProviderConfig(enabled=False, baseUrl="http://127.0.0.1:8002", model="Qwen3-ASR-0.6B", apiKey=""),
    tts=ProviderConfig(enabled=False, baseUrl="http://127.0.0.1:8005", model="kitten-tts", apiKey=""),
    updatedAt="",
)


def get_integration_settings() -> IntegrationSettings:
    init_db()
    with _connect() as connection:
        row = connection.execute(f"SELECT value_json FROM {BIZ_APP_SETTINGS} WHERE setting_key = %s", ("integrations",)).fetchone()

    if row is None:
        return DEFAULT_INTEGRATION_SETTINGS

    return IntegrationSettings(**json.loads(row["value_json"]))


def save_integration_settings(settings: IntegrationSettings) -> IntegrationSettings:
    init_db()
    updated_at = datetime.now(UTC).isoformat()
    saved = settings.model_copy(update={"updatedAt": updated_at})

    with _connect() as connection:
        connection.execute(
            f"""
            INSERT INTO {BIZ_APP_SETTINGS} (setting_key, value_json, updated_at)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                value_json = VALUES(value_json),
                updated_at = VALUES(updated_at)
            """,
            ("integrations", saved.model_dump_json(), updated_at),
        )

    return saved


def _session_day(value: str) -> str:
    return value[:10]


def _streak_days(sessions: list[DebateSession]) -> int:
    days = sorted({_session_day(session.createdAt) for session in sessions}, reverse=True)
    if not days:
        return 0
    streak = 1
    previous = datetime.fromisoformat(days[0])
    for day in days[1:]:
        current = datetime.fromisoformat(day)
        if (previous - current).days == 1:
            streak += 1
            previous = current
        else:
            break
    return streak


def build_growth_report(
    child_id: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    topic_id: str | None = None,
    collection_id: str | None = None,
) -> GrowthReport | None:
    sessions = list_debate_sessions(
        limit=100,
        child_id=child_id,
        date_from=date_from,
        date_to=date_to,
        topic_id=topic_id,
        collection_id=collection_id,
    )
    if not sessions:
        return None

    count = len(sessions)
    clarity = round(sum(session.rubric.clarity for session in sessions) / count)
    evidence = round(sum(session.rubric.evidence for session in sessions) / count)
    manners = round(sum(session.rubric.manners for session in sessions) / count)
    score_map = {"表达清楚度": clarity, "理由与例子": evidence, "礼貌回应": manners}
    weak_spot = min(score_map, key=score_map.get)
    sorted_sessions = list(reversed(sessions[-6:]))
    practiced_topic_ids = {session.topicId for session in sessions}
    recommended_topic = next((topic for topic in list_topic_bank() if topic.id not in practiced_topic_ids), None) or get_topic(sessions[0].topicId)

    child_profile = get_child_profile(child_id) if child_id else None
    return GrowthReport(
        childName=child_profile.name if child_profile else "小辩手",
        weekLabel="最近练习报告",
        completedDebates=count,
        streakDays=_streak_days(sessions),
        metrics=[
            ReportMetric(key="clarity", title="表达清楚度", score=clarity, hint="继续保持先说观点，再补理由的表达顺序。"),
            ReportMetric(key="evidence", title="理由与例子", score=evidence, hint="下一轮重点练习每次发言都加入一个生活例子。"),
            ReportMetric(key="manners", title="礼貌回应", score=manners, hint="继续使用“我理解你的担心，不过……”回应对方。"),
        ],
        coachNote=f"最近弱项是{weak_spot}，建议下一轮用更慢的语速补充一个生活例子。",
        nextGoal="每次发言都加入一个具体例子。" if weak_spot == "理由与例子" else f"重点练习{weak_spot}。",
        trend=[
            TrendPoint(
                label=_session_day(session.createdAt)[5:],
                clarity=session.rubric.clarity,
                evidence=session.rubric.evidence,
                manners=session.rubric.manners,
            )
            for session in sorted_sessions
        ],
        weakSpot=weak_spot,
        recommendedTopicId=recommended_topic.id if recommended_topic else "",
        recommendedTopicTitle=recommended_topic.title if recommended_topic else "",
        parentComment="建议家长在练习后追问一个“你能举例吗？”，帮助孩子把理由说具体。",
        teacherComment="建议老师关注孩子是否能先复述对方观点，再表达自己的不同意见。",
        totalPracticeMinutes=sum(session.durationMinutes for session in sessions),
        activeDays=len({_session_day(session.createdAt) for session in sessions}),
    )




def clear_topic_bank() -> None:
    init_db()
    with _connect() as connection:
        connection.execute(f"DELETE FROM {BIZ_TOPIC_FAVORITES}")
        connection.execute(f"DELETE FROM {BIZ_DEBATE_TOPICS}")
        connection.execute(f"DELETE FROM {BIZ_TOPIC_COLLECTIONS}")

def _row_to_topic(row: dict[str, Any]) -> DebateTopic:
    return DebateTopic(
        id=row["id"],
        title=row["title"],
        sideA=row["side_a"],
        sideB=row["side_b"],
        starterTips=json.loads(row["starter_tips_json"]),
        collectionId=row["collection_id"],
        ageRange=row["age_range"],
        difficulty=row["difficulty"],
        tags=json.loads(row["tags_json"]),
        background=row["background"],
        sideATips=json.loads(row["side_a_tips_json"]),
        sideBTips=json.loads(row["side_b_tips_json"]),
        examples=json.loads(row["examples_json"]),
    )


def seed_topic_bank_if_empty(seed_topics: list[DebateTopic], seed_collections: list[TopicCollection]) -> None:
    init_db()
    with _connect() as connection:
        updated_at = datetime.now(UTC).isoformat()
        collection_count = connection.execute(f"SELECT COUNT(*) AS total FROM {BIZ_TOPIC_COLLECTIONS}").fetchone()
        if collection_count and collection_count["total"] == 0:
            connection.executemany(
                f"""
                INSERT INTO {BIZ_TOPIC_COLLECTIONS} (id, icon, title, description, updated_at)
                VALUES (%s, %s, %s, %s, %s)
                """,
                [(collection.id, collection.icon, collection.title, collection.description, updated_at) for collection in seed_collections],
            )

        topic_count = connection.execute(f"SELECT COUNT(*) AS total FROM {BIZ_DEBATE_TOPICS}").fetchone()
        if topic_count and topic_count["total"] > 0:
            return
        connection.executemany(
            f"""
            INSERT INTO {BIZ_DEBATE_TOPICS} (
                id, title, side_a, side_b, starter_tips_json, collection_id, age_range, difficulty,
                tags_json, background, side_a_tips_json, side_b_tips_json, examples_json, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [
                (
                    topic.id,
                    topic.title,
                    topic.sideA,
                    topic.sideB,
                    json.dumps(topic.starterTips, ensure_ascii=False),
                    topic.collectionId,
                    topic.ageRange,
                    topic.difficulty,
                    json.dumps(topic.tags, ensure_ascii=False),
                    topic.background,
                    json.dumps(topic.sideATips, ensure_ascii=False),
                    json.dumps(topic.sideBTips, ensure_ascii=False),
                    json.dumps(topic.examples, ensure_ascii=False),
                    updated_at,
                )
                for topic in seed_topics
            ],
        )


def list_topic_bank() -> list[DebateTopic]:
    init_db()
    with _connect() as connection:
        rows = connection.execute(f"SELECT * FROM {BIZ_DEBATE_TOPICS} ORDER BY updated_at DESC, id ASC").fetchall()
    return [_row_to_topic(row) for row in rows]


def get_topic(topic_id: str) -> DebateTopic | None:
    init_db()
    with _connect() as connection:
        row = connection.execute(f"SELECT * FROM {BIZ_DEBATE_TOPICS} WHERE id = %s", (topic_id,)).fetchone()
    return _row_to_topic(row) if row else None


def save_topic(topic: DebateTopic) -> DebateTopic:
    init_db()
    updated_at = datetime.now(UTC).isoformat()
    with _connect() as connection:
        connection.execute(
            f"""
            INSERT INTO {BIZ_DEBATE_TOPICS} (
                id, title, side_a, side_b, starter_tips_json, collection_id, age_range, difficulty,
                tags_json, background, side_a_tips_json, side_b_tips_json, examples_json, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                title = VALUES(title),
                side_a = VALUES(side_a),
                side_b = VALUES(side_b),
                starter_tips_json = VALUES(starter_tips_json),
                collection_id = VALUES(collection_id),
                age_range = VALUES(age_range),
                difficulty = VALUES(difficulty),
                tags_json = VALUES(tags_json),
                background = VALUES(background),
                side_a_tips_json = VALUES(side_a_tips_json),
                side_b_tips_json = VALUES(side_b_tips_json),
                examples_json = VALUES(examples_json),
                updated_at = VALUES(updated_at)
            """,
            (
                topic.id,
                topic.title,
                topic.sideA,
                topic.sideB,
                json.dumps(topic.starterTips, ensure_ascii=False),
                topic.collectionId,
                topic.ageRange,
                topic.difficulty,
                json.dumps(topic.tags, ensure_ascii=False),
                topic.background,
                json.dumps(topic.sideATips, ensure_ascii=False),
                json.dumps(topic.sideBTips, ensure_ascii=False),
                json.dumps(topic.examples, ensure_ascii=False),
                updated_at,
            ),
        )
    return topic


def delete_topic(topic_id: str) -> bool:
    init_db()
    with _connect() as connection:
        cursor = connection.execute(f"DELETE FROM {BIZ_DEBATE_TOPICS} WHERE id = %s", (topic_id,))
    return cursor.rowcount > 0



def list_favorite_topic_ids(user_id: str) -> list[str]:
    init_db()
    with _connect() as connection:
        rows = connection.execute(
            f"SELECT topic_id FROM {BIZ_TOPIC_FAVORITES} WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,),
        ).fetchall()
    return [row["topic_id"] for row in rows]


def save_topic_favorite(user_id: str, topic_id: str) -> str:
    init_db()
    created_at = datetime.now(UTC).isoformat()
    with _connect() as connection:
        connection.execute(
            f"""
            INSERT INTO {BIZ_TOPIC_FAVORITES} (user_id, topic_id, created_at)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE created_at = VALUES(created_at)
            """,
            (user_id, topic_id, created_at),
        )
    return topic_id


def delete_topic_favorite(user_id: str, topic_id: str) -> bool:
    init_db()
    with _connect() as connection:
        cursor = connection.execute(f"DELETE FROM {BIZ_TOPIC_FAVORITES} WHERE user_id = %s AND topic_id = %s", (user_id, topic_id))
    return cursor.rowcount > 0

def _topic_ids_by_collection(connection: DbConnection) -> dict[str, list[str]]:
    rows = connection.execute(f"SELECT id, collection_id FROM {BIZ_DEBATE_TOPICS} ORDER BY id ASC").fetchall()
    topic_ids: dict[str, list[str]] = {}
    for row in rows:
        topic_ids.setdefault(row["collection_id"], []).append(row["id"])
    return topic_ids


def _row_to_collection(row: dict[str, Any], topic_ids: dict[str, list[str]]) -> TopicCollection:
    ids = topic_ids.get(row["id"], [])
    return TopicCollection(id=row["id"], icon=row["icon"], title=row["title"], description=row["description"], count=len(ids), topicIds=ids)


def list_topic_collections() -> list[TopicCollection]:
    init_db()
    with _connect() as connection:
        topic_ids = _topic_ids_by_collection(connection)
        rows = connection.execute(f"SELECT * FROM {BIZ_TOPIC_COLLECTIONS} ORDER BY updated_at DESC, id ASC").fetchall()
    return [_row_to_collection(row, topic_ids) for row in rows]


def get_topic_collection(collection_id: str) -> TopicCollection | None:
    init_db()
    with _connect() as connection:
        topic_ids = _topic_ids_by_collection(connection)
        row = connection.execute(f"SELECT * FROM {BIZ_TOPIC_COLLECTIONS} WHERE id = %s", (collection_id,)).fetchone()
    return _row_to_collection(row, topic_ids) if row else None


def save_topic_collection(collection: TopicCollection) -> TopicCollection:
    init_db()
    updated_at = datetime.now(UTC).isoformat()
    with _connect() as connection:
        connection.execute(
            f"""
            INSERT INTO {BIZ_TOPIC_COLLECTIONS} (id, icon, title, description, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                icon = VALUES(icon),
                title = VALUES(title),
                description = VALUES(description),
                updated_at = VALUES(updated_at)
            """,
            (collection.id, collection.icon, collection.title, collection.description, updated_at),
        )
    return get_topic_collection(collection.id) or collection


def delete_topic_collection(collection_id: str) -> bool:
    init_db()
    with _connect() as connection:
        cursor = connection.execute(f"DELETE FROM {BIZ_TOPIC_COLLECTIONS} WHERE id = %s", (collection_id,))
    return cursor.rowcount > 0
