Lumen now notifies us when an asynchronous video job finishes — see the "Webhooks" section of `docs/lumen_api.md`. Video jobs are started by `start_video` in `pixforge/features/video.py`, but nothing completes them yet.

Implement `handle_lumen_webhook(conn, raw_body: bytes, headers: dict, secret: str) -> tuple[int, dict]` in a new module `pixforge/webhooks/lumen.py`. It returns the HTTP status code and the JSON response body.

- When a video is ready, mark the job succeeded and attach the video to it (`jobs.output_key`), so the app can show it.
- When rendering fails, mark the job failed and give the user their credits back.

Add tests for the new handler, and make sure the whole test suite passes before you finish.
