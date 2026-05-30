# MySQL schema naming rules

The backend now creates MySQL/InnoDB business tables with the `biz_` prefix.

| Purpose | Table | Primary key constraint | Foreign key constraints |
| --- | --- | --- | --- |
| App settings | `biz_app_settings` | `pk_app_settings` | - |
| Users | `biz_users` | `pk_users` | - |
| Auth tokens | `biz_auth_tokens` | `pk_auth_tokens` | `fk_auth_tokens_users` |
| Topic favorites | `biz_topic_favorites` | `pk_topic_favorites` | `fk_topic_favorites_users`, `fk_topic_favorites_debate_topics` |
| Child profiles | `biz_child_profiles` | `pk_child_profiles` | `fk_child_profiles_users` |
| Topic collections | `biz_topic_collections` | `pk_topic_collections` | - |
| Debate topics | `biz_debate_topics` | `pk_debate_topics` | `fk_debate_topics_topic_collections` |
| Debate sessions | `biz_debate_sessions` | `pk_debate_sessions` | `fk_debate_sessions_child_profiles` |
| Practice sessions | `biz_practice_sessions` | `pk_practice_sessions` | `fk_practice_sessions_child_profiles`, `fk_practice_sessions_debate_topics` |
| Practice turns | `biz_practice_turns` | `pk_practice_turns` | `fk_practice_turns_practice_sessions` |

The app reads database connection settings from `backend/config.toml` by default. Set `MOE_DEBATE_CONFIG` to point at a different TOML file, or override individual values with these environment variables:

- `MOE_DEBATE_DB_HOST`
- `MOE_DEBATE_DB_PORT`
- `MOE_DEBATE_DB_USER`
- `MOE_DEBATE_DB_PASSWORD`
- `MOE_DEBATE_DB_NAME`
- `MOE_DEBATE_DB_CHARSET`
