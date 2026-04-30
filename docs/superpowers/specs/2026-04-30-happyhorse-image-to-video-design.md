# HappyHorse Image-to-Video Dify Plugin Tool Design

## 1. Overview
This project adds a new tool to the `tongyi_aigc` Dify plugin to support the "HappyHorse-图生视频-基于首帧" (Image-to-Video) model via the Alibaba Cloud DashScope API.

## 2. Components
- **`tools/happyhorse_image_2_video.yaml`**: The configuration file defining the tool's interface in Dify.
- **`tools/happyhorse_image_2_video.py`**: The implementation file containing the Python class that handles API requests.
- **`provider/tongyi_aigc.yaml`**: Add `tools/happyhorse_image_2_video.yaml` to the `tools` array.
- **`tools/__init__.py`**: Add imports for the new tool class.

## 3. Tool Parameters
Based on the API documentation for `happyhorse-1.0-i2v`:
- `model`: Model name (fixed to `happyhorse-1.0-i2v`).
- `prompt`: Optional text description for video generation.
- `image_input`: Optional file input for the first frame.
- `img_url`: Optional string URL for the first frame. 
  - *Note: One of `image_input` or `img_url` is required. If both are provided, `image_input` takes precedence.*
- `resolution`: `720P` or `1080P` (default).
- `duration`: `[3, 15]` seconds integer (default 5).
- `watermark`: Boolean (default true).
- `seed`: Integer `[0, 2147483647]`.

## 4. API Details
- **Endpoint**: `POST https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis`
- **Headers**: `Authorization`, `Content-Type: application/json`, `X-DashScope-Async: enable`.
- **Payload format**: 
  - `model`: "happyhorse-1.0-i2v"
  - `input`:
    - `prompt`: "..."
    - `media`: `[{"type": "first_frame", "url": "..."}]`
      - *Note: `url` will be either the provided HTTP URL or a generated base64 data URI (using PIL to process the file input, identical to existing tools).*
  - `parameters`: `resolution`, `duration`, `watermark`, `seed`.
- **Flow**: Submits async task -> returns `task_id` formatted for user.
- **Query tool**: The user will use the existing Wan video query tool since the query endpoint is identical and the existing tool can query any video-synthesis task by ID.

## 5. Error Handling
- Validate API key existence.
- Validate that an image is provided.
- Truncate `prompt` strictly to 2500 characters to safely satisfy limits.
- Handle timeout (set to 15 seconds) and non-200 responses gracefully by yielding text/json messages with error details.
- Handle invalid parameter types by catching TypeError/ValueError and yielding a text message.
