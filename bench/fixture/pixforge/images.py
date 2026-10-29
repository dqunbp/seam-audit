"""The user's image library."""
from . import clock


def save_image(conn, user_id: int, url: str, width: int, height: int) -> int:
    cur = conn.execute(
        "INSERT INTO images (user_id, url, width, height, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, url, width, height, clock.iso_now()),
    )
    return cur.lastrowid


def get_image(conn, image_id: int):
    return conn.execute("SELECT * FROM images WHERE id = ?", (image_id,)).fetchone()


def list_images(conn, user_id: int):
    return conn.execute(
        "SELECT * FROM images WHERE user_id = ? ORDER BY id", (user_id,)
    ).fetchall()
