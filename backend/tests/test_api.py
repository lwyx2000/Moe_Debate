from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_headers() -> dict[str, str]:
    response = client.post("/api/auth/login", json={"email": "demo@example.com", "password": "demo123456"})
    assert response.status_code == 200
    token = response.json()["accessToken"]
    return {"Authorization": f"Bearer {token}"}


def test_auth_login_me_and_logout() -> None:
    headers = auth_headers()
    me_response = client.get("/api/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "demo@example.com"

    logout_response = client.post("/api/auth/logout", headers=headers)
    assert logout_response.status_code == 200

    expired_response = client.get("/api/auth/me", headers=headers)
    assert expired_response.status_code == 401


def test_protected_routes_require_auth() -> None:
    assert client.get("/api/children").status_code == 401
    assert client.post("/api/admin/topics", json={}).status_code == 401
    assert client.get("/api/debate/sessions/not-found").status_code == 401


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_topics() -> None:
    response = client.get("/api/topics")
    assert response.status_code == 200
    topics = response.json()
    assert len(topics) >= 3
    assert {
        "id",
        "title",
        "sideA",
        "sideB",
        "starterTips",
        "collectionId",
        "ageRange",
        "difficulty",
        "tags",
        "background",
        "sideATips",
        "sideBTips",
        "examples",
    }.issubset(topics[0])


def test_topic_filters() -> None:
    response = client.get("/api/topics?collectionId=family-rules&difficulty=easy&tag=阅读")
    assert response.status_code == 200
    topics = response.json()
    assert len(topics) == 1
    assert topics[0]["id"] == "homework-pet"






def test_topic_favorites_are_account_scoped() -> None:
    headers = auth_headers()
    add_response = client.post("/api/favorites/topics/screen-time", headers=headers)
    assert add_response.status_code == 200

    list_response = client.get("/api/favorites/topics", headers=headers)
    assert list_response.status_code == 200
    assert "screen-time" in list_response.json()

    delete_response = client.delete("/api/favorites/topics/screen-time", headers=headers)
    assert delete_response.status_code == 200

    after_delete_response = client.get("/api/favorites/topics", headers=headers)
    assert "screen-time" not in after_delete_response.json()


def test_topic_search_and_detail() -> None:
    search_response = client.get("/api/topics?q=眼睛")
    assert search_response.status_code == 200
    topics = search_response.json()
    assert any(topic["id"] == "screen-time" for topic in topics)

    detail_response = client.get("/api/topics/screen-time")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["background"]
    assert detail["sideATips"]


def test_admin_topic_crud() -> None:
    payload = {
        "id": "admin-test-topic",
        "title": "课间十分钟应不应该全部自由活动？",
        "sideA": "正方：应该自由活动",
        "sideB": "反方：需要安排安静活动",
        "starterTips": ["我认为课间应该自由活动，因为可以放松。"],
        "collectionId": "school-life",
        "ageRange": "8-10",
        "difficulty": "easy",
        "tags": ["课间", "规则"],
        "background": "课间时间短，孩子需要讨论自由和安全的平衡。",
        "sideATips": ["自由活动可以放松大脑。"],
        "sideBTips": ["安排安静活动更安全。"],
        "examples": ["下课后先喝水再活动。"],
    }

    headers = auth_headers()
    client.delete(f"/api/admin/topics/{payload['id']}", headers=headers)

    create_response = client.post("/api/admin/topics", json=payload, headers=headers)
    assert create_response.status_code == 200
    assert create_response.json()["id"] == payload["id"]

    payload["title"] = "课间十分钟要不要全部自由活动？"
    update_response = client.put(f"/api/admin/topics/{payload['id']}", json=payload, headers=headers)
    assert update_response.status_code == 200
    assert update_response.json()["title"] == payload["title"]

    search_response = client.get("/api/topics?q=课间")
    assert any(topic["id"] == payload["id"] for topic in search_response.json())

    delete_response = client.delete(f"/api/admin/topics/{payload['id']}", headers=headers)
    assert delete_response.status_code == 200

    missing_response = client.get(f"/api/topics/{payload['id']}")
    assert missing_response.status_code == 404


def test_topic_collections() -> None:
    response = client.get("/api/topic-collections")
    assert response.status_code == 200
    collections = response.json()
    assert len(collections) >= 4
    assert {"id", "icon", "title", "description", "count", "topicIds"}.issubset(collections[0])




def test_admin_topic_collection_crud() -> None:
    payload = {
        "id": "admin-collection",
        "icon": "🧪",
        "title": "测试分类",
        "description": "用于测试后台可维护分类。",
        "count": 0,
        "topicIds": [],
    }

    headers = auth_headers()
    client.delete(f"/api/admin/topic-collections/{payload['id']}", headers=headers)

    create_response = client.post("/api/admin/topic-collections", json=payload, headers=headers)
    assert create_response.status_code == 200
    assert create_response.json()["title"] == payload["title"]

    payload["title"] = "测试分类更新"
    update_response = client.put(f"/api/admin/topic-collections/{payload['id']}", json=payload, headers=headers)
    assert update_response.status_code == 200
    assert update_response.json()["title"] == payload["title"]

    delete_response = client.delete(f"/api/admin/topic-collections/{payload['id']}", headers=headers)
    assert delete_response.status_code == 200






def test_admin_topic_bulk_import() -> None:
    headers = auth_headers()
    collection_id = "bulk-collection"
    topic_id = "bulk-topic"
    client.delete(f"/api/admin/topics/{topic_id}", headers=headers)
    client.delete(f"/api/admin/topic-collections/{collection_id}", headers=headers)

    payload = {
        "collections": [
            {"id": collection_id, "icon": "📦", "title": "批量分类", "description": "批量导入测试。"}
        ],
        "topics": [
            {
                "id": topic_id,
                "title": "批量导入的题目要不要马上可练？",
                "sideA": "正方：马上可练",
                "sideB": "反方：先审核",
                "starterTips": ["我认为批量导入后可以马上练，因为老师已经检查过。"],
                "collectionId": collection_id,
                "ageRange": "8-10",
                "difficulty": "easy",
                "tags": ["批量", "后台"],
                "background": "测试后台批量导入题库。",
                "sideATips": ["导入效率高。"],
                "sideBTips": ["审核更稳妥。"],
                "examples": ["老师整理好 JSON 后一次导入。"],
            }
        ],
        "replaceExisting": False,
    }

    import_response = client.post("/api/admin/topics/import", json=payload, headers=headers)
    assert import_response.status_code == 200
    assert import_response.json()["importedTopics"] == 1
    assert import_response.json()["importedCollections"] == 1

    detail_response = client.get(f"/api/topics/{topic_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["collectionId"] == collection_id

    client.delete(f"/api/admin/topics/{topic_id}", headers=headers)
    client.delete(f"/api/admin/topic-collections/{collection_id}", headers=headers)


def test_user_and_child_profiles_crud() -> None:
    user_response = client.get("/api/users/demo")
    assert user_response.status_code == 200
    assert user_response.json()["id"] == "demo-parent"

    headers = auth_headers()
    list_response = client.get("/api/children", headers=headers)
    assert list_response.status_code == 200
    assert any(child["id"] == "demo-child" for child in list_response.json())

    payload = {
        "id": "test-child",
        "userId": "demo-parent",
        "name": "小海豚",
        "age": 9,
        "grade": "三年级",
        "avatar": "🐬",
        "debateGoal": "练习用例子支持观点。",
    }

    client.delete(f"/api/children/{payload['id']}", headers=headers)
    create_response = client.post("/api/children", json=payload, headers=headers)
    assert create_response.status_code == 200
    assert create_response.json()["name"] == "小海豚"

    payload["debateGoal"] = "练习礼貌回应对方。"
    update_response = client.put(f"/api/children/{payload['id']}", json=payload, headers=headers)
    assert update_response.status_code == 200
    assert update_response.json()["debateGoal"] == payload["debateGoal"]

    delete_response = client.delete(f"/api/children/{payload['id']}", headers=headers)
    assert delete_response.status_code == 200


def test_demo_report() -> None:
    response = client.get("/api/reports/demo", headers=auth_headers())
    assert response.status_code == 200
    report = response.json()
    assert report["completedDebates"] >= 1
    assert len(report["metrics"]) == 3
    assert report["nextGoal"]
    assert "trend" in report
    assert "weakSpot" in report
    assert "recommendedTopicTitle" in report
    assert report["totalPracticeMinutes"] >= report["completedDebates"]
    assert report["activeDays"] >= 1


def test_debate_response_scores_reason_and_example() -> None:
    headers = auth_headers()
    response = client.post(
        "/api/debate/respond",
        json={
            "topicId": "screen-time",
            "side": "正方",
            "message": "我认为可以多玩一小时，因为我会先完成作业。例如我上周就是这样安排的。",
            "childId": "demo-child",
        },
        headers=headers,
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["rubric"]["evidence"] >= 80
    assert "下一步" not in payload["reply"]
    assert payload["nextPrompt"]
    assert payload["practiceSessionId"]

    second_response = client.post(
        "/api/debate/respond",
        json={
            "topicId": "screen-time",
            "side": "正方",
            "message": "我还可以举一个例子，比如周六先运动再玩。",
            "childId": "demo-child",
            "practiceSessionId": payload["practiceSessionId"],
        },
        headers=headers,
    )
    assert second_response.status_code == 200
    assert second_response.json()["practiceSessionId"] == payload["practiceSessionId"]

    practice_detail_response = client.get(f"/api/practice/sessions/{payload['practiceSessionId']}", headers=headers)
    assert practice_detail_response.status_code == 200
    practice_detail = practice_detail_response.json()
    assert practice_detail["totalTurns"] == 4
    assert len(practice_detail["turns"]) == 4

    finish_response = client.post(f"/api/practice/sessions/{payload['practiceSessionId']}/finish", json={"summary": "完成两轮表达练习。"}, headers=headers)
    assert finish_response.status_code == 200
    assert finish_response.json()["endedAt"]

    sessions_response = client.get("/api/debate/sessions?limit=1&childId=demo-child", headers=headers)
    assert sessions_response.status_code == 200
    sessions = sessions_response.json()
    assert len(sessions) == 1
    assert sessions[0]["message"]
    assert sessions[0]["childId"] == "demo-child"
    assert sessions[0]["durationMinutes"] >= 1
    assert sessions[0]["practiceSessionId"] == payload["practiceSessionId"]
    assert sessions[0]["totalTurns"] == 4
    assert len(sessions[0]["conversation"]) == 4

    filtered_response = client.get("/api/debate/sessions?limit=10&childId=demo-child&topicId=screen-time&collectionId=interest-growth", headers=headers)
    assert filtered_response.status_code == 200
    assert all(session["topicId"] == "screen-time" for session in filtered_response.json())

    report_response = client.get("/api/reports/demo?childId=demo-child&topicId=screen-time&collectionId=interest-growth", headers=headers)
    assert report_response.status_code == 200
    assert report_response.json()["recommendedTopicTitle"]


def test_debate_session_detail_404() -> None:
    response = client.get("/api/debate/sessions/not-found", headers=auth_headers())
    assert response.status_code == 404


def test_voice_settings() -> None:
    response = client.get("/api/voice/settings")
    assert response.status_code == 200
    settings = response.json()
    assert settings["asrEngine"] == "Qwen3-ASR-0.6B"
    assert settings["saveRawAudio"] is False



def test_integration_settings_round_trip() -> None:
    payload = {
        "llm": {"enabled": True, "baseUrl": "http://127.0.0.1:8001/v1", "model": "local-qwen", "apiKey": ""},
        "asr": {"enabled": True, "baseUrl": "http://127.0.0.1:8002", "model": "Qwen3-ASR-0.6B", "apiKey": ""},
        "tts": {"enabled": True, "baseUrl": "http://127.0.0.1:8005", "model": "kitten-tts", "apiKey": ""},
    }

    headers = auth_headers()
    update_response = client.put("/api/integrations/settings", json=payload, headers=headers)
    assert update_response.status_code == 200
    assert update_response.json()["updatedAt"]

    get_response = client.get("/api/integrations/settings", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["llm"]["model"] == "local-qwen"
