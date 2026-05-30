# Moe Debate · 萌辩岛儿童辩论

这是一个面向儿童辩论练习的全栈项目骨架：

- 前端：Vue 3 + Vite + TypeScript，使用 `animal-island-vue` 的动森风格组件，并补充项目自定义样式。
- 后端：Python FastAPI + MySQL，提供辩题、AI 教练回复、语音输入/输出占位接口。
- 语音建议：先采用 **Qwen3-ASR-0.6B（语音识别） + Kitten-TTS-Server（语音合成）**，通过后端 API 做统一封装。

> 当前仓库没有发现 `stitch_ai/` 设计稿目录，因此先按“一个个页面更新”的方式推进：已完成主页面、辩论练习室、儿童辩题库、成长报告和语音设置；后端已提供登录鉴权、角色权限、辩题、教练反馈、练习历史持久化、题库分类、演示成长报告、语音配置和语音占位接口。后续可把设计稿截图/导出资源放入 `stitch_ai/` 后继续像素级还原。

## 目录

```text
frontend/      Vue 3 前端
backend/       FastAPI 后端和 MySQL 配置
docs/          技术方案文档
```

## 本地启动

### 后端

先准备 MySQL 8.x，并创建应用用户（也可以使用已有用户）：

```sql
CREATE DATABASE IF NOT EXISTS moe_debate CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'moe_debate'@'%' IDENTIFIED BY 'moe_debate_password';
GRANT ALL PRIVILEGES ON moe_debate.* TO 'moe_debate'@'%';
FLUSH PRIVILEGES;
```

确认 `backend/config.toml` 里的连接信息与你本地 MySQL 一致，或复制 `backend/config.example.toml` 到自己的配置文件后设置 `MOE_DEBATE_CONFIG=/path/to/config.toml`。

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问 `http://localhost:5173`。


## MySQL 数据库配置和命名规范

后端已从 SQLite 切换为 MySQL，连接配置集中放在 `backend/config.toml`；也可以用 `MOE_DEBATE_CONFIG` 指向其它 TOML 文件，或用 `MOE_DEBATE_DB_HOST`、`MOE_DEBATE_DB_PORT`、`MOE_DEBATE_DB_USER`、`MOE_DEBATE_DB_PASSWORD`、`MOE_DEBATE_DB_NAME`、`MOE_DEBATE_DB_CHARSET` 覆盖配置。

业务表统一以 `biz_` 开头：`biz_users`、`biz_auth_tokens`、`biz_topic_favorites`、`biz_child_profiles`、`biz_topic_collections`、`biz_debate_topics`、`biz_debate_sessions`、`biz_practice_sessions`、`biz_practice_turns`、`biz_app_settings`。主键约束使用 `pk_` + 去掉 `biz_` 后的表名，例如 `pk_users`、`pk_debate_topics`；外键约束使用 `fk_` + 去掉 `biz_` 后的来源表名 + 目标表名，例如 `fk_child_profiles_users`、`fk_auth_tokens_users`。完整命名见 [`docs/mysql-schema.md`](docs/mysql-schema.md)。

## API

认证说明：除健康检查、辩题只读接口、语音方案只读接口外，孩子档案、练习历史、成长报告、模型配置和后台管理接口都需要在请求头携带 `Authorization: Bearer <accessToken>`。本地 Demo 管理员账号为 `demo@example.com` / `demo123456`。

- `GET /api/health`：健康检查。
- `POST /api/auth/register`：注册家长账号；服务端会强制注册为 `parent` 角色。
- `POST /api/auth/login`：邮箱密码登录，返回 Bearer Token 和当前用户。
- `GET /api/auth/me`：读取当前登录用户。
- `POST /api/auth/logout`：注销当前 Token。
- `GET /api/topics`：获取儿童辩题；支持 `collectionId`、`ageRange`、`difficulty`、`tag`、`q` 查询参数，例如 `/api/topics?collectionId=family-rules&difficulty=easy&tag=阅读&q=习惯`。
- `GET /api/topics/{topic_id}`：获取辩题详情。
- `POST /api/admin/topics`：新增后台辩题，仅 `admin` / `teacher` 可用。
- `PUT /api/admin/topics/{topic_id}`：编辑后台辩题，仅 `admin` / `teacher` 可用。
- `DELETE /api/admin/topics/{topic_id}`：删除后台辩题，仅 `admin` / `teacher` 可用。
- `POST /api/admin/topics/import`：批量导入题库 JSON，可同时导入分类和题目，支持合并更新或替换现有题库，仅 `admin` / `teacher` 可用。
- `GET /api/favorites/topics` / `POST /api/favorites/topics/{topic_id}` / `DELETE /api/favorites/topics/{topic_id}`：账号级辩题收藏，登录后按用户保存到 MySQL。
- `GET /api/topic-collections`：获取题库分类，分类数量和题目 ID 会根据 MySQL 题库动态计算。
- `POST /api/admin/topic-collections`：新增后台题库分类，仅 `admin` / `teacher` 可用。
- `PUT /api/admin/topic-collections/{collection_id}`：编辑后台题库分类，仅 `admin` / `teacher` 可用。
- `DELETE /api/admin/topic-collections/{collection_id}`：删除后台题库分类，仅 `admin` / `teacher` 可用。
- `GET /api/users/demo`：获取本地 demo 用户。
- `GET /api/children`：获取当前用户下的孩子档案。
- `POST /api/children`：新增孩子档案。
- `PUT /api/children/{child_id}`：编辑孩子档案。
- `DELETE /api/children/{child_id}`：删除孩子档案。
- `GET /api/reports/demo`：获取成长报告；支持 `childId`、`dateFrom`、`dateTo`、`topicId`、`collectionId` 查询参数，可按孩子、时间范围、题目和分类筛选。
- `POST /api/debate/respond`：提交孩子的观点并返回教练反馈，同时写入多轮练习会话；请求体可带 `childId` 和 `practiceSessionId`，返回体会带 `practiceSessionId` 方便前端连续多轮提交。
- `POST /api/practice/sessions`：开始一次完整练习会话，保存 `childId`、`topicId`、`side`、`startedAt`。
- `GET /api/practice/sessions/{session_id}`：获取一次练习的完整多轮会话和 `turns`。
- `POST /api/practice/sessions/{session_id}/turns`：手动追加一轮对话，可记录 `speaker`、`text`、`audioUrl`、`source` 和单轮评分。
- `POST /api/practice/sessions/{session_id}/finish`：结束练习并写入 `endedAt`、`durationSeconds`、会话总结。
- `GET /api/debate/sessions`：获取最近练习历史；支持 `childId`、`dateFrom`、`dateTo`、`topicId`、`collectionId` 查询参数，并返回完整多轮 `conversation`、`durationSeconds`、`totalTurns` 和会话总结。
- `GET /api/debate/sessions/{session_id}`：获取单次练习详情。
- `POST /api/speech/transcribe`：语音识别占位接口。
- `POST /api/speech/synthesize`：语音合成占位接口。
- `GET /api/voice/plan`：语音方案建议。
- `GET /api/voice/settings`：语音配置和儿童安全默认值。
- `GET /api/integrations/settings`：获取大模型、ASR、TTS 服务配置，仅 `admin` / `teacher` 可用。
- `PUT /api/integrations/settings`：保存大模型、ASR、TTS 服务配置，仅 `admin` / `teacher` 可用。

## 语音方案结论

详见 [`docs/voice-architecture.md`](docs/voice-architecture.md)。


## 推荐架构

```text
Vue 3 前端
  │  录音 / 文本 / 播放
  ▼
FastAPI 主后端（业务编排）
  ├─ MySQL：账号、孩子档案、题库、练习历史、模型服务配置
  ├─ 云端大模型 API：辩论教练反馈
  ├─ Qwen3-ASR-0.6B 服务：语音转文字（可选本地独立服务）
  └─ Kitten-TTS-Server：文字转语音（可选本地独立服务）
```

推荐不要把 ASR/TTS 模型直接塞进主 FastAPI 进程：主后端负责鉴权、配置、转发和保存历史；ASR/TTS 如果本地部署，单独起 HTTP 服务。这样资源隔离更清楚，后续替换服务也方便。

## 模型怎么配置最方便

推荐方案：**大模型教练用买来的云端 API；ASR/TTS 按资源情况决定是否本地部署**。

- 大模型教练：不用本地跑，填云端 OpenAI-compatible 地址即可，例如 `https://api.openai.com/v1`，模型名填你购买服务支持的模型名，API Key 填服务商密钥。
- Qwen3-ASR-0.6B：可以整合进后端，但更建议单独跑成 ASR HTTP 服务，例如 `http://127.0.0.1:8002`，后端只负责转发音频和接收文本。这样不会让主 API 被模型加载和推理阻塞。
- Kitten-TTS-Server：资源占用相对小，适合本地部署成独立 TTS 服务，例如 `http://127.0.0.1:8005`；后端仍然只调用它的 HTTP API。

进入前端“语音设置”页，在“模型服务配置”里填写大模型、ASR、TTS 三个服务地址、模型名，并点击保存。配置会写入后端 MySQL；本地服务不需要 API Key 时可以留空。


## 当前已完成/未完成

已完成：

- 云端 OpenAI-compatible 大模型教练调用链路：`/api/debate/respond` 会优先读取配置并调用云端大模型，失败时回退到本地启发式教练。
- ASR/TTS 转发链路：`/api/speech/transcribe` 和 `/api/speech/synthesize` 会优先调用配置中的独立服务，失败时回退到开发占位响应。
- 成长报告：`/api/reports/demo` 会优先根据 MySQL 中保存的练习历史动态生成，没有历史时返回 demo 数据。
- 真实登录/鉴权/权限：前端已增加登录/注册页；后端已增加邮箱密码登录、PBKDF2 密码哈希、Bearer Token、`parent` / `teacher` / `admin` 角色和孩子档案访问控制，并把账号和业务数据持久化到 MySQL。

你本地还需要处理：

- 购买的大模型 API：在“语音设置 → 模型服务配置”里填 `baseUrl`、模型名和 API Key，并启用“大模型教练 API”。
- Qwen3-ASR-0.6B：如果要真实识别，需要你启动一个 HTTP 服务，默认约定接口为 `POST /transcribe`，multipart 字段名为 `file`，返回 JSON 至少包含 `text`。
- Kitten-TTS-Server：如果要真实语音合成，需要你启动一个 HTTP 服务，默认约定接口为 `POST /synthesize`，请求 JSON 包含 `text` 和 `model`，返回 JSON 包含 `audioUrl`。如果服务接口不同，改 `backend/app/integrations.py` 里的转发路径和字段即可。


## 前端页面和配置入口

- 路由系统：前端已接入标准 Vue Router（`frontend/src/router.ts` + `frontend/src/main.ts`），把 `/`、`/practice`、`/topics`、`/profiles`、`/history`、`/report`、`/voice-setup` 映射到真实页面组件，并通过 `<RouterView>` 渲染，支持浏览器前进/后退。
- 页面拆分：导航栏和登录/注册区已拆到 `frontend/src/components/AppNav.vue`、`frontend/src/components/AuthGate.vue`；首页、练习室、儿童辩题库、孩子档案、练习历史、成长报告和语音设置都已拆到 `frontend/src/pages/*.vue`。
- 主页面：产品入口和功能说明。
- 辩论练习室：选择当前孩子、辩题、立场，提交观点、录音、播放教练反馈。
- 登录页：邮箱密码登录/注册，支持一键使用 Demo 管理员账号。
- 儿童辩题库：分类总览 + 关键词/分类/年龄/难度/标签筛选，支持后端账号级收藏、详情预览；`admin` / `teacher` 登录后可编辑/新增/删除后台题目、维护分类并批量导入题库 JSON，点击题目可直接进入练习页。
- 孩子档案：创建/编辑/删除多个孩子档案，并切换当前练习对象。
- 练习历史：读取 `/api/debate/sessions?childId=...&dateFrom=...&dateTo=...&topicId=...&collectionId=...`，支持本周、本月、自定义日期、题目和分类筛选，并展示 `biz_practice_sessions` / `biz_practice_turns` 保存的完整多轮练习过程、每轮来源、总轮数和会话总结。
- 成长报告：读取 `/api/reports/demo?childId=...&dateFrom=...&dateTo=...&topicId=...&collectionId=...`，支持同一套筛选条件，展示能力趋势图、最近弱项、推荐下一题、家长/老师评语、总练习时长、真实练习日和连续练习天数；“导出 PDF”使用浏览器打印/另存为 PDF。
- 语音设置：配置大模型 API、Qwen3-ASR 服务、Kitten-TTS 服务地址、模型名和 API Key。

## 后续题库详情/筛选怎么做

当前已完成：题库运行时数据已经从代码内置列表迁移到后端 MySQL，首次启动只会从 `backend/data/topics.json` 和 `backend/data/topic_collections.json` 导入初始数据；后续新增/编辑/删除题目和分类都通过后台接口维护。后端 `DebateTopic` 已包含 `collectionId`、`ageRange`、`difficulty`、`tags`、`background`、正反方提示和生活例子字段；`GET /api/topics` 支持 `collectionId`、`ageRange`、`difficulty`、`tag`、`q` 查询参数；前端已拆出导航和认证组件，并增加 URL 路由映射；“儿童辩题库”页面已增加搜索、分类、年龄、难度、标签、账号级收藏筛选、详情预览、题目管理、分类管理和批量导入，并支持点击题目进入练习页。

后续如果继续增强，可以增加：

1. 推荐下一题目前按“未练题目优先”生成，后续可升级为基于弱项、年龄和难度的更智能推荐。
2. 更多标签和多选筛选。
3. 题库后台增加批量导入预校验、导入错误逐行提示和导入历史记录。
4. 继续把题库页内部的后台表单拆成更细的 `TopicAdminPanel.vue`、`TopicBulkImportPanel.vue`，并补充前端单元测试。
5. 如果要把家长/老师评语改成多人协作输入，需要新增评语编辑表和审核流程；当前版本先由后端根据练习历史生成建议文案。

## 登录鉴权、权限和多孩子档案

当前已实现一套可本地运行的账号系统，适合 MVP 联调和后续替换为正式身份服务：

1. 后端首次启动会创建 Demo 管理员 `demo@example.com` / `demo123456`，并创建 `demo-child` 孩子档案。
2. 前端未登录时会先进入登录/注册页；注册接口只允许创建 `parent` 角色，避免前端自行注册管理员。
3. 密码以 PBKDF2-SHA256 + 随机盐写入 MySQL；登录后后端签发 Bearer Token，前端自动保存并在后续 API 请求中携带。
4. `admin` / `teacher` 可以维护题库和模型服务配置；`parent` 只能管理自己名下的孩子档案、练习历史、成长报告和账号级收藏。
5. 前端“孩子档案”页可以新增、编辑、删除多个孩子档案，并切换当前练习对象。
6. 练习提交时会把当前孩子的 `childId` 一起提交给 `/api/debate/respond`，后端保存练习历史时记录到 `biz_debate_sessions.child_id`；练习历史和成长报告会按权限和 `childId` 查询，多个孩子的数据不会混在一起。
7. 如果后续要接入第三方登录/短信登录，可以保留当前 `current_user` 权限依赖，只替换 `/api/auth/*` 的发 token 逻辑。

## 题库数据维护方式

题库不再以 `backend/app/debate.py` 里的 Python 列表作为运行时数据源。当前流程是：

1. 首次启动后端时，`backend/data/topics.json` 和 `backend/data/topic_collections.json` 会作为初始种子导入 MySQL。
2. 之后使用 Demo 管理员或 `teacher` / `admin` 账号登录，前端“儿童辩题库 → 题库后台管理”里新增、编辑、删除题目，或在“批量导入题库”中粘贴 JSON，会调用 `/api/admin/topics*` 并写入 MySQL。
3. 分类数据也由 MySQL 维护，可在“儿童辩题库 → 分类管理页面”维护，也可通过 `/api/admin/topic-collections*` 接口新增、编辑、删除；`GET /api/topic-collections` 返回的数量和 `topicIds` 根据当前题库动态计算。
4. 如果你要批量初始化题库，可以先改 JSON 种子文件，再清空 MySQL 中的 `biz_debate_topics` 和 `biz_topic_collections` 让后端重新导入；已经上线的数据建议只通过后台接口维护，不要直接改 Python 代码。

## 需要你本地处理的服务

- 大模型 API：你买来的服务不需要本地启动，只需要在“语音设置 → 模型服务配置 → 大模型教练 API”里填写服务地址、模型名、API Key，并打开启用。
- Qwen3-ASR-0.6B：需要你自己启动一个 ASR HTTP 服务；默认后端会调用 `POST /transcribe`，multipart 字段 `file`，返回 `{"text":"..."}`。服务地址在“语音设置 → Qwen3-ASR 识别”里配置。
- Kitten-TTS-Server：需要你自己启动 TTS HTTP 服务；默认后端会调用 `POST /synthesize`，请求 `{"text":"...","model":"..."}`，返回 `{"audioUrl":"..."}`。服务地址在“语音设置 → Kitten-TTS 输出”里配置。
- 如果你启动的 ASR/TTS 服务接口不一样，改 `backend/app/integrations.py` 里的 `transcribe_with_provider` 或 `synthesize_with_provider`。
