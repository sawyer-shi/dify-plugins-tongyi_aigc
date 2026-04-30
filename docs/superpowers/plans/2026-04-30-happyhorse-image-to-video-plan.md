# HappyHorse Image-to-Video Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new Dify plugin tool for "HappyHorse-图生视频-基于首帧" (Image-to-Video) model.

**Architecture:** Create a new tool file `happyhorse_image_2_video.py` and its configuration `happyhorse_image_2_video.yaml`. Update the provider configuration `tongyi_aigc.yaml` and `__init__.py` to expose the new tool. The tool will borrow image processing logic (base64 URI creation) from `wan_first_image_2_video.py`. Testing will be manual or through checking Dify's syntax.

**Tech Stack:** Python, Dify Plugin Framework, Alibaba Cloud DashScope API, Pillow (PIL)

---

## Chunk 1: Create HappyHorse Configuration

### Task 1: Create YAML configuration

**Files:**
- Create: `tongyi_aigc/tools/happyhorse_image_2_video.yaml`

- [ ] **Step 1: Write configuration**
Create the YAML file with parameters:
  - `model`: type `select`, fixed option `happyhorse-1.0-i2v`
  - `prompt`: type `string`, form `llm`, optional
  - `image_input`: type `file`, form `llm`, optional
  - `img_url`: type `string`, form `llm`, optional
  - `resolution`: type `select`, options `720P`, `1080P` (default)
  - `duration`: type `number`, limits `min: 3, max: 15`, default `5`
  - `watermark`: type `boolean`, default `true`
  - `seed`: type `number`, default `0`

- [ ] **Step 2: Verify Syntax**
Visually verify the yaml is well-formed.

- [ ] **Step 3: Commit**
```bash
git add tools/happyhorse_image_2_video.yaml
git commit -m "feat: add happyhorse image-to-video yaml config"
```

## Chunk 2: Implement HappyHorse Python Tool

### Task 2: Create Python tool implementation

**Files:**
- Create: `tongyi_aigc/tools/happyhorse_image_2_video.py`

- [ ] **Step 1: Write tool logic**
Create the Python class `HappyHorseImage2VideoTool` inheriting from `Tool`.
Implement `_invoke` to:
  - Validate API key existence (yield error if missing).
  - Extract and process image using PIL (copy `_process_image` helper from `wan_first_image_2_video.py`), prioritizing `image_input` over `img_url`. Yield error if both are empty/invalid.
  - Construct payload exactly as required by DashScope (`model`, `input.prompt` (truncated to 2500 chars), `input.media` formatted as `[{"type": "first_frame", "url": processed_img}]`, `parameters`).
  - Parse optional parameters safely (resolution, duration, watermark, seed), catching Type/Value errors and yielding specific errors rather than failing silently.
  - Make POST request to `https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis`.
  - Include headers: `Authorization`, `Content-Type: application/json`, and `X-DashScope-Async: enable`.
  - Use a 15-second timeout for the request.
  - Handle timeout and non-200 responses gracefully by yielding text/json messages with error details.
  - Consolidate init messages to a single yield to reduce chatty UI.
  - On success, yield response text containing the `task_id`.

- [ ] **Step 2: Verify Syntax**
Run: `python -m py_compile tools/happyhorse_image_2_video.py`
Expected: No output.

- [ ] **Step 3: Commit**
```bash
git add tools/happyhorse_image_2_video.py
git commit -m "feat: implement happyhorse image-to-video python logic"
```

## Chunk 3: Expose the Tool in Provider

### Task 3: Update Provider Configuration

**Files:**
- Modify: `tongyi_aigc/provider/tongyi_aigc.yaml`
- Modify: `tongyi_aigc/tools/__init__.py`

- [ ] **Step 1: Add to tongyi_aigc.yaml**
Append `- tools/happyhorse_image_2_video.yaml` to the `tools` array.

- [ ] **Step 2: Update __init__.py**
Append `from .happyhorse_image_2_video import HappyHorseImage2VideoTool` to the existing imports in `tongyi_aigc/tools/__init__.py`. DO NOT overwrite existing imports.

- [ ] **Step 3: Verify Syntax**
Run: `python -m py_compile tools/__init__.py`
Expected: No output.

- [ ] **Step 4: Commit**
```bash
git add provider/tongyi_aigc.yaml tools/__init__.py
git commit -m "feat: expose happyhorse image-to-video tool in provider"
```