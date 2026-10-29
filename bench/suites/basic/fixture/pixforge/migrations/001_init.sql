CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    plan TEXT NOT NULL DEFAULT 'free' CHECK (plan IN ('free', 'pro')),
    balance INTEGER NOT NULL DEFAULT 0 CHECK (balance >= 0),
    locale TEXT NOT NULL DEFAULT 'en'
);

CREATE TABLE credit_ledger (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    delta INTEGER NOT NULL,
    reason TEXT NOT NULL,
    idempotency_key TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);

CREATE TABLE images (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    url TEXT NOT NULL,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE jobs (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    kind TEXT NOT NULL,
    status TEXT NOT NULL,
    request_id TEXT NOT NULL UNIQUE,
    cost INTEGER NOT NULL,
    provider_job_id TEXT UNIQUE,
    output_url TEXT,
    error TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE processed_events (
    source TEXT NOT NULL,
    event_id TEXT NOT NULL,
    processed_at TEXT NOT NULL,
    PRIMARY KEY (source, event_id)
);
