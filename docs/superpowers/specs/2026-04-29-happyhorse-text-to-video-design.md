# HappyHorse Text-to-Video Dify Plugin Tool Design

## 1. Overview
This project adds a new tool to the `tongyi_aigc` Dify plugin to support the "HappyHorse-文生视频" (Text-to-Video) model via the Alibaba Cloud DashScope API.

## 2. Components
- **`tools/happyhorse_text_2_video.yaml`**: The configuration file defining the tool's interface in Dify.
- **`tools/happyhorse_text_2_video.py`**: The implementation file containing the Python class that handles API requests.
- **`provider/tongyi_aigc.yaml`**: Add `tools/happyhorse_text_2_video.yaml` to the `tools` array.
- **`tools/__init__.py`**: Add imports for the new tool class.

## 3. Tool Parameters
Based on the API documentation for `happyhorse-1.0-t2v`:
- `model`: Model name (fixed to `happyhorse-1.0-t2v`).
- `prompt`: Text description for video generation (up to 5000 non-Chinese or 2500 Chinese characters).
- `resolution`: `720P` or `1080P` (default).
- `ratio`: `16:9` (default), `9:16`, `1:1`, `4:3`, `3:4`.
- `duration`: `[3, 15]` seconds integer (default 5).
- `watermark`: Boolean (default true).
- `seed`: Integer `[0, 2147483647]`.

## 4. API Details
- **Endpoint**: `POST https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis`
- **Headers**: `Authorization`, `Content-Type: application/json`, `X-DashScope-Async: enable`.
- **Flow**: Submits async task -> returns `task_id` formatted for user.
- **Query tool**: The user will use the existing Wan video query tool since the query endpoint is identical and the existing tool can query any video-synthesis task by ID.

## 5. Error Handling
- Validate API key existence.
- Validate `prompt` is not empty.
- Limit prompt length.
- Handle timeout and non-200 responses gracefully by yielding text/json messages with error details.
