CREATE TABLE quota_usage (
    user_id INTEGER NOT NULL REFERENCES users(id),
    kind TEXT NOT NULL,
    day TEXT NOT NULL,
    used INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, kind, day)
);
