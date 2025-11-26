CREATE DATABASE client_telegram;

DROP TABLE IF EXISTS elegram_sessions;
CREATE TABLE IF NOT EXISTS telegram_sessions (
    id BIGSERIAL PRIMARY KEY,
    session_name VARCHAR UNIQUE,
    session_data BYTEA,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);


DROP TABLE IF EXISTS telegram_events;
CREATE TABLE IF NOT EXISTS telegram_events(
    id BIGSERIAL PRIMARY KEY,
    event_data BYTEA,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);