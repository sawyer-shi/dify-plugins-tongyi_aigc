# HappyHorse Video Edit Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new Dify plugin tool for "HappyHorse-视频编辑" (video + reference images + prompt).

**Architecture:** Create a new standalone tool pair (`happyhorse_video_edit.yaml` and `happyhorse_video_edit.py`) following existing HappyHorse tool conventions. The tool accepts a required `video_url`, optional 0-5 reference image files, and submits an async task to DashScope `video-synthesis`. Register the tool in provider config and keep `tools/__init__.py` aligned with current branch convention.

**Tech Stack:** Python, Dify Plugin Framework, requests, Pillow (PIL), DashScope HTTP API

---

## Chunk 1: Tool YAML Configuration

### Task 1: Create `happyhorse_video_edit.yaml`

**Files:**
- Create: `tongyi_aigc/tools/happyhorse_video_edit.yaml`

- [ ] **Step 1: Define tool identity and description**
Add `identity`, bilingual `label`, `description`, and `extra.python.source: tools/happyhorse_video_edit.py`.

- [ ] **Step 2: Define required core parameters**
Add:
  - `model` (select, fixed option `happyhorse-1.0-video-edit`)
  - `prompt` (string, required, form `llm`)
  - `video_url` (string, required, form `llm`)

- [ ] **Step 3: Define reference image parameters**
Add file parameters `reference_image_1` to `reference_image_5`:
  - `reference_image_1` required false
  - `reference_image_2`~`reference_image_5` required false
All as `type: file`, `form: llm`.

- [ ] **Step 4: Define optional generation parameters**
Add:
  - `resolution` select: `720P`, `1080P` (default)
  - `watermark` boolean (default true)
  - `audio_setting` select: `auto` (default), `origin`
  - `seed` number (optional, no default)

- [ ] **Step 5: Verify YAML format**
Visually verify structure and indentation match existing tool YAML files.

- [ ] **Step 6: Commit**
```bash
git add tools/happyhorse_video_edit.yaml
git commit -m "feat: add happyhorse video edit yaml config"
```

## Chunk 2: Python Tool Implementation

### Task 2: Create `happyhorse_video_edit.py`

**Files:**
- Create: `tongyi_aigc/tools/happyhorse_video_edit.py`

- [ ] **Step 1: Scaffold class and imports**
Create `HappyHorseVideoEditTool(Tool)` with imports aligned to existing HappyHorse tools:
`base64`, `json`, `logging`, `requests`, `Generator`, `Any`, `BytesIO`, `Image`, `ToolInvokeMessage`.

- [ ] **Step 2: Implement input validation**
In `_invoke`:
  - validate API key
  - validate required `prompt` and `video_url`
  - validate `video_url` begins with `http://` or `https://`

- [ ] **Step 3: Implement reference image collection**
Loop through `reference_image_1`~`reference_image_5`:
  - if provided, process with `_process_image`
  - on failure, return specific image index error
  - append each valid image as `{"type": "reference_image", "url": <data_uri>}`

- [ ] **Step 4: Build payload and parameter validation**
Construct `payload` with media list containing:
  - first item: `{"type": "video", "url": video_url}`
  - then optional reference images
Validate and map params:
  - `resolution` only `720P`/`1080P`
  - `audio_setting` only `auto`/`origin`
  - `watermark` boolean parsing
  - `seed` int in `[0, 2147483647]`
Invalid inputs fail-fast with user-facing text error.

- [ ] **Step 5: Submit async request and handle response**
POST to `https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis` with headers:
`Authorization`, `Content-Type: application/json`, `X-DashScope-Async: enable`.
Use `timeout=15`.
Handle:
  - timeout / request exceptions
  - non-200 responses
  - JSON parsing errors
  - API error bodies with `code`
On success, emit summary text + JSON with `task_id`.
On success, summary text must include: `task_id`, `task_status`, and key request info (model, resolution/audio_setting if present, prompt preview).

- [ ] **Step 6: Add helpers**
Implement:
  - `_process_image` with explicit behavior:
    - accept Dify file object / bytes / data URI
    - enforce format compatibility (JPEG/JPG/PNG/WEBP output path)
    - enforce max size 10MB per reference image
    - convert image to base64 data URI for payload `url`
    - raise clear `ValueError` on invalid file/size/processing failure
  - `_format_response_text` for task summary and next-step guidance

- [ ] **Step 7: Verify syntax**
Run:
```bash
python -m py_compile tools/happyhorse_video_edit.py
```
Expected: no output.

- [ ] **Step 8: Commit**
```bash
git add tools/happyhorse_video_edit.py
git commit -m "feat: implement happyhorse video edit python logic"
```

## Chunk 3: Provider Registration

### Task 3: Register the tool

**Files:**
- Modify: `tongyi_aigc/provider/tongyi_aigc.yaml`
- Modify: `tongyi_aigc/tools/__init__.py`

- [ ] **Step 1: Register YAML in provider**
Append `- tools/happyhorse_video_edit.yaml` in the `tools:` list.

- [ ] **Step 2: Update tools package init**
Append:
```python
from .happyhorse_video_edit import HappyHorseVideoEditTool
```
Do not remove existing lines.

- [ ] **Step 3: Verify syntax**
Run:
```bash
python -m py_compile tools/__init__.py
```
Expected: no output.

- [ ] **Step 4: Commit**
```bash
git add provider/tongyi_aigc.yaml tools/__init__.py
git commit -m "feat: expose happyhorse video edit tool in provider"
```
