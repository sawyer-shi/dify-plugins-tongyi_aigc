# HappyHorse Video Edit Dify Plugin Tool Design

## 1. Overview
This project adds a new tool to the `tongyi_aigc` Dify plugin to support the "HappyHorse-视频编辑" model via the Alibaba Cloud DashScope API.

## 2. Components
- **`tools/happyhorse_video_edit.yaml`**: Defines the tool interface in Dify.
- **`tools/happyhorse_video_edit.py`**: Implements the API submission logic.
- **`provider/tongyi_aigc.yaml`**: Registers `tools/happyhorse_video_edit.yaml` in the tools list.
- **`tools/__init__.py`**: Append `from .happyhorse_video_edit import HappyHorseVideoEditTool` to stay consistent with current HappyHorse tool registration in this branch.

## 3. Tool Parameters
Based on `happyhorse-1.0-video-edit` API:
- `model`: Fixed as `happyhorse-1.0-video-edit`.
- `prompt`: Required text prompt for edit instruction.
- `video_url`: Required public URL of input video.
- `reference_image_1` to `reference_image_5`: Optional file inputs for reference images.
- `resolution`: Optional, `720P` or `1080P` (default).
- `watermark`: Optional boolean.
- `audio_setting`: Optional, `auto` or `origin`.
- `seed`: Optional integer `[0, 2147483647]`.

## 4. API Details
- Endpoint: `POST https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis`
- Headers: `Authorization`, `Content-Type: application/json`, `X-DashScope-Async: enable`
- Payload:
  - `model`: `happyhorse-1.0-video-edit`
  - `input.prompt`
  - `input.media`:
    - exactly one `{"type": "video", "url": video_url}`
    - zero to five `{"type": "reference_image", "url": <processed_image>}`
  - `parameters`: `resolution`, `watermark`, `audio_setting`, `seed`
- Flow: async task submission and return of `task_id`.
- Query: continue using existing task query tool (`wan_video_query`) because it calls the same `/api/v1/tasks/{task_id}` endpoint and can retrieve status/video URL for HappyHorse tasks.

## 5. Error Handling
- Validate API key exists.
- Validate `prompt` and `video_url` are present.
- Validate `video_url` is `http://` or `https://` and reject empty/local file paths.
- Process each reference image with PIL helper; if conversion fails or exceeds limits, return specific error message with index.
- Reference image constraints for validation/processing:
  - formats: JPEG/JPG/PNG/WEBP
  - max size: 10MB each
  - conversion output: data URI (`data:image/...;base64,...`) to match existing project behavior
- Validate optional parameter types with clear error messages.
- Optional parameter validation contract:
  - `resolution`: only `720P` or `1080P`; invalid value -> fail-fast with text error.
  - `audio_setting`: only `auto` or `origin`; invalid value -> fail-fast with text error.
  - `seed`: integer in `[0, 2147483647]`; out of range/non-integer -> fail-fast with text error.
  - `watermark`: accept boolean or common boolean-like strings; otherwise fail-fast.
- Handle request timeout (15s), network errors, non-200 responses, and invalid JSON responses.
- Return readable summary including `task_id`, task status, and key request info; additionally return JSON message for workflow chaining/debug (same pattern as existing HappyHorse tools).
