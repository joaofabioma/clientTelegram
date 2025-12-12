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
    event_name VARCHAR,
    event_message_id VARCHAR,
    event_data BYTEA,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);


DROP TABLE IF EXISTS telegram_type_events;
CREATE TABLE IF NOT EXISTS telegram_type_events(
    id BIGSERIAL PRIMARY KEY,
    type_name VARCHAR UNIQUE,
    descricao VARCHAR,
    hits BIGINT NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_set_updated_at ON telegram_type_events;

CREATE TRIGGER trg_set_updated_at
BEFORE UPDATE ON telegram_type_events
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();
