from .billing import grant_credits


def create_user(conn, email: str, plan: str = "free", balance: int = 0, locale: str = "en") -> int:
    cur = conn.execute(
        "INSERT INTO users (email, plan, locale) VALUES (?, ?, ?)", (email, plan, locale)
    )
    user_id = cur.lastrowid
    if balance:
        grant_credits(conn, user_id, balance, "signup_bonus", f"signup:{user_id}")
    return user_id


def get_user(conn, user_id: int):
    return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
