# HappyHorse Reference-to-Video Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new Dify plugin tool for "HappyHorse-参考生视频" (Reference-to-Video) model.

**Architecture:** Create a new tool file `happyhorse_reference_video.py` and its configuration `happyhorse_reference_video.yaml`. Update the provider configuration `tongyi_aigc.yaml` and `__init__.py` to expose the new tool. Testing will be manual or through checking Dify's syntax.

**Tech Stack:** Python, Dify Plugin Framework, Alibaba Cloud DashScope API, Pillow (PIL)

---

## Chunk 1: Create HappyHorse Configuration

### Task 1: Create YAML configuration

**Files:**
- Create: `tongyi_aigc/tools/happyhorse_reference_video.yaml`

- [ ] **Step 1: Write configuration**
Create the YAML file with parameters:
  - `model`: type `select`, fixed option `happyhorse-1.0-r2v`
  - `prompt`: type `string`, form `llm`, required `true`
  - `image_input_1`: type `file`, form `llm`, required `true` (The first image is mandatory)
  - `image_input_2` through `image_input_9`: type `file`, form `llm`, required `false` (Optional extra images)
  - `resolution`: type `select`, options `720P`, `1080P` (default)
  - `ratio`: type `select`, options `16:9` (default), `9:16`, `3:4`, `4:3`, `1:1`
  - `duration`: type `number`, limits `min: 3, max: 15`, default `5`
  - `watermark`: type `boolean`, default `true`
  - `seed`: type `number` (optional, no default)

- [ ] **Step 2: Verify Syntax**
Visually verify the yaml is well-formed.

- [ ] **Step 3: Commit**
```bash
git add tools/happyhorse_reference_video.yaml
git commit -m "feat: add happyhorse reference-to-video yaml config"
```

## Chunk 2: Implement HappyHorse Python Tool

### Task 2: Create Python tool implementation

**Files:**
- Create: `tongyi_aigc/tools/happyhorse_reference_video.py`

- [ ] **Step 1: Write tool logic**
Create the Python class `HappyHorseReferenceVideoTool` inheriting from `Tool`.
Implement `_invoke` to:
  - Validate API key existence (yield error if missing).
  - Iterate through keys `image_input_1` to `image_input_9`.
  - Process each provided image using the `_process_image` helper (copied from `happyhorse_image_2_video.py`). If `ValueError` is caught (e.g. >10MB), yield a specific error message identifying which input failed.
  - Append successfully processed images to the `media` array with format `{"type": "reference_image", "url": processed_img}`.
  - If the `media` array is empty, yield an error `"❌ 请至少提供一张有效的参考图像 (image_input_1)"`.
  - Extract and truncate `prompt` to 2500 characters safely (`str()`).
  - Parse optional parameters safely (resolution, ratio, duration, watermark, seed), catching Type/Value errors and yielding specific errors.
  - Construct payload: `model`, `input.prompt`, `input.media`, `parameters`.
  - Make POST request to `https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis`.
  - Include headers: `Authorization`, `Content-Type: application/json`, `X-DashScope-Async: enable`.
  - Use a 15-second timeout.
  - Consolidate initialization text message into a single yield block.
  - Handle timeout and non-200 responses gracefully by yielding text/json messages.
  - On success, yield response text containing the `task_id` (via `_format_response_text` helper).

- [ ] **Step 2: Verify Syntax**
Run: `python -m py_compile tools/happyhorse_reference_video.py`
Expected: No output.

- [ ] **Step 3: Commit**
```bash
git add tools/happyhorse_reference_video.py
git commit -m "feat: implement happyhorse reference-to-video python logic"
```

## Chunk 3: Expose the Tool in Provider

### Task 3: Update Provider Configuration

**Files:**
- Modify: `tongyi_aigc/provider/tongyi_aigc.yaml`
- Modify: `tongyi_aigc/tools/__init__.py`

- [ ] **Step 1: Add to tongyi_aigc.yaml**
Append `- tools/happyhorse_reference_video.yaml` to the `tools` array.

- [ ] **Step 2: Update __init__.py**
Append `from .happyhorse_reference_video import HappyHorseReferenceVideoTool` to the existing imports in `tongyi_aigc/tools/__init__.py`. DO NOT overwrite existing imports.

- [ ] **Step 3: Verify Syntax**
Run: `python -m py_compile tools/__init__.py`
Expected: No output.

- [ ] **Step 4: Commit**
```bash
git add provider/tongyi_aigc.yaml tools/__init__.py
git commit -m "feat: expose happyhorse reference-to-video tool in provider"
```