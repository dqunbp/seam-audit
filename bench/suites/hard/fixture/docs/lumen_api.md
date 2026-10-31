# Lumen API v2 — reference

_Copied from docs.lumen.ai on 2026-02-10._

All requests are `POST` with a JSON body and `Authorization: Bearer <api key>`.
Errors use standard HTTP status codes with a body `{"error": {"code": "...", "message": "..."}}`.
`429` responses carry a `Retry-After` header (seconds).

Lumen bills you only for requests whose `status` is `succeeded`.

Output files are served from `cdn.lumen.ai` and are **deleted 24 hours after creation**.
Copy anything you want to keep to your own storage.

## POST /v2/images — text to image

Request: `{"prompt": "...", "size": "1024x1024"}`

Response `200`:

```json
{"id": "img_8f2", "status": "succeeded",
 "images": [{"url": "https://cdn.lumen.ai/o/8f2.png", "width": 1024, "height": 1024}]}
```

`status` is one of:

| status      | meaning                                                                   |
|-------------|---------------------------------------------------------------------------|
| `succeeded` | `images` holds one or more images                                        |
| `filtered`  | the output was removed by moderation; `images` is `[]`, `filter_reason` set |

## POST /v2/upscale — image upscaling

Request: `{"image_url": "https://...", "factor": 2}` — `factor` is `2` or `4`.

The input image must be reachable over HTTPS and at most **2048 px** on its longest side.

Response `200`:

```json
{"id": "ups_41c", "status": "succeeded",
 "image": {"url": "https://cdn.lumen.ai/o/41c.png", "width": 2048, "height": 2048}}
```

`status` is one of:

| status      | meaning |
|-------------|---------|
| `succeeded` | `image` is the upscaled image |
| `rejected`  | the input was not accepted (`reason`: `input_too_large`, `unsupported_format`). Not an HTTP error. `image` echoes the **original input image unchanged** so clients can keep displaying it. |
| `filtered`  | the output was removed by moderation; `image` is `null`, `reason` set |

## POST /v2/videos — text to video (asynchronous)

Request: `{"prompt": "...", "callback_url": "https://your.app/hooks/lumen", "duration_s": 5}`

Response `202`: `{"id": "vid_77a", "status": "queued"}`

The result is delivered later to `callback_url` as webhook events (below).
Rendering usually takes 1–10 minutes.

## Webhooks

Lumen sends `POST` requests with a JSON body to the `callback_url` of the job.

### Signature

Every delivery has a header:

```
Lumen-Signature: t=1772366400,v1=5257a869e7ecebeda32affa62cdca3fa51cad7e77a0e56ff536d0ce8e108d8bd
```

`v1` is the hex HMAC-SHA256, keyed with your endpoint secret, of the string `"<t>.<raw request body>"`.
Reject deliveries with an invalid signature, and deliveries whose `t` is more than 5 minutes
away from the current time (replay protection).

### Events

Every event has the envelope:

```json
{"id": "evt_1a2b3c", "type": "<event type>", "created": 1772366400, "data": { ... }}
```

`data.job_id` is the Lumen job id returned by `POST /v2/videos` (`vid_...`).

**`video.progress`** — rendering progress, sent zero or more times.

```json
{"job_id": "vid_77a", "progress": 0.4}
```

**`video.completed`** — rendering finished.

```json
{"job_id": "vid_77a",
 "videos": [{"url": "https://cdn.lumen.ai/o/77a.mp4", "duration_s": 5}],
 "moderation": null}
```

If moderation removed the output after rendering, `videos` is `[]` and
`moderation` is `{"reason": "..."}`. The job is still reported as `video.completed`,
but there is nothing to deliver, and you are not billed for it.

**`video.failed`** — rendering failed.

```json
{"job_id": "vid_77a", "error": {"code": "render_error", "message": "..."}}
```

### Delivery guarantees

- **At least once.** The same event (same `id`) may be delivered more than once.
- **No ordering guarantee.** For example, a `video.progress` event can arrive after `video.completed`.
- Short jobs can finish very quickly: events for a job may be delivered **before the `POST /v2/videos`
  call that created it has returned** to you.
- Respond with any `2xx` within 10 seconds to acknowledge. Any other response, or a timeout,
  is retried with exponential backoff for up to 24 hours.
