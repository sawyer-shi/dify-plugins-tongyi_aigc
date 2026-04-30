# HappyHorse Reference-to-Video Dify Plugin Tool Design

## 1. Overview
This project adds a new tool to the `tongyi_aigc` Dify plugin to support the "HappyHorse-参考生视频" (Reference-to-Video) model via the Alibaba Cloud DashScope API.

## 2. Components
- **`tools/happyhorse_reference_video.yaml`**: The configuration file defining the tool's interface in Dify.
- **`tools/happyhorse_reference_video.py`**: The implementation file containing the Python class that handles API requests.
- **`provider/tongyi_aigc.yaml`**: Add `tools/happyhorse_reference_video.yaml` to the `tools` array.
- **`tools/__init__.py`**: Add imports for the new tool class.

## 3. Tool Parameters
Based on the API documentation for `happyhorse-1.0-r2v`:
- `model`: Model name (fixed to `happyhorse-1.0-r2v`).
- `prompt`: Text description for video generation. Users reference images via `character1`, `character2`, etc.
- `image_input_1` through `image_input_9`: Optional file inputs for the 1st through 9th reference images.
  - *At least one image (`image_input_1`) must be provided.*
- `resolution`: `720P` or `1080P` (default).
- `ratio`: `16:9` (default), `9:16`, `3:4`, `4:3`, `1:1`.
- `duration`: `[3, 15]` seconds integer (default 5).
- `watermark`: Boolean (default true).
- `seed`: Integer `[0, 2147483647]`.

## 4. API Details
- **Endpoint**: `POST https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis`
- **Headers**: `Authorization`, `Content-Type: application/json`, `X-DashScope-Async: enable`.
- **Payload format**: 
  - `model`: "happyhorse-1.0-r2v"
  - `input`:
    - `prompt`: "..."
    - `media`: `[{"type": "reference_image", "url": "..."}]`
      - *Note: `url` will be generated base64 data URIs using PIL to process the file inputs. This matches DashScope's support for data URIs demonstrated in the HappyHorse text/image-to-video endpoints.*
  - `parameters`: `resolution`, `ratio`, `duration`, `watermark`, `seed`.
- **Flow**: Submits async task -> returns `task_id` formatted for user.
- **Query tool**: The existing generic `wan_video_query` tool can be used. It queries `/api/v1/tasks/{task_id}` globally and checks for `video_url` in the result, which works across all DashScope async generation models.

## 5. Error Handling
- Validate API key existence.
- Validate that at least one valid image is provided in `image_input_1`.
- Collect non-null `image_input_X` inputs in order, processing each into a base64 string.
- If processing any image fails (e.g. exceeds 10MB limit), yield a `ValueError` indicating the image index and size limit.
- Truncate `prompt` safely to 2500 characters to prevent API rejection while satisfying practical boundaries without complex encoding counts.
- Handle timeout (15 seconds) and non-200 responses gracefully.
- Handle invalid parameter types securely by yielding descriptive error text.
