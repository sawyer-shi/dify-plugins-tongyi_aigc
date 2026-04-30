# HappyHorse Text-to-Video Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a new Dify plugin tool for "HappyHorse-文生视频" (Text-to-Video) model.

**Architecture:** Create a new tool file `happyhorse_text_2_video.py` and its configuration `happyhorse_text_2_video.yaml`. Update the provider configuration `tongyi_aigc.yaml` and `__init__.py` to expose the new tool. Testing will be manual or through checking Dify's syntax.

**Tech Stack:** Python, Dify Plugin Framework, Alibaba Cloud DashScope API

---

## Chunk 1: Create HappyHorse Configuration

### Task 1: Create YAML configuration

**Files:**
- Create: `tongyi_aigc/tools/happyhorse_text_2_video.yaml`

- [ ] **Step 1: Write configuration**
Create the YAML file with parameters:
  - `model`: fixed to `happyhorse-1.0-t2v`
  - `prompt`: text input for video generation
  - `resolution`: Select options `720P` or `1080P` (default)
  - `ratio`: Select options `16:9` (default), `9:16`, `1:1`, `4:3`, `3:4`
  - `duration`: string input, limits `[3, 15]`, default `5`
  - `watermark`: boolean, default `true`
  - `seed`: number, default `0`

- [ ] **Step 2: Verify Syntax**
Visually verify the yaml is well-formed. There's no yaml compiler command readily available in base python, but ensure indentation is correct.

- [ ] **Step 3: Commit**
```bash
git add tools/happyhorse_text_2_video.yaml
git commit -m "feat: add happyhorse yaml config"
```

## Chunk 2: Implement HappyHorse Python Tool

### Task 2: Create Python tool implementation

**Files:**
- Create: `tongyi_aigc/tools/happyhorse_text_2_video.py`

- [ ] **Step 1: Write tool logic**
Create the Python class `HappyhorseText2VideoTool` inheriting from `Tool`.
Implement `_invoke` to:
  - Validate API key existence (yield error if missing).
  - Extract prompt, truncate to 2500 characters, yield error if empty.
  - Parse and append resolution, ratio, duration (with integer conversion fallback), watermark, and seed.
  - Construct payload exactly as required by DashScope (`model`, `input: {prompt}`, `parameters`).
  - Make POST request to `https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis`.
  - Include headers: `Authorization`, `Content-Type: application/json`, and `X-DashScope-Async: enable`.
  - Handle timeout and non-200 responses gracefully by yielding text/json messages with error details.
  - On success, yield response text containing the `task_id` for progress tracking.

- [ ] **Step 2: Verify Syntax**
Run: `python -m py_compile tools/happyhorse_text_2_video.py`
Expected: No output (meaning syntax is correct).

- [ ] **Step 3: Commit**
```bash
git add tools/happyhorse_text_2_video.py
git commit -m "feat: implement happyhorse text-to-video python logic"
```

## Chunk 3: Expose the Tool in Provider

### Task 3: Update Provider Configuration

**Files:**
- Modify: `tongyi_aigc/provider/tongyi_aigc.yaml`
- Modify: `tongyi_aigc/tools/__init__.py`

- [ ] **Step 1: Add to tongyi_aigc.yaml**
Add `- tools/happyhorse_text_2_video.yaml` to the `tools` array.

- [ ] **Step 2: Update __init__.py**
Add the import to `tongyi_aigc/tools/__init__.py`:
`from .happyhorse_text_2_video import HappyhorseText2VideoTool`

- [ ] **Step 3: Verify Syntax**
Run: `python -m py_compile tools/__init__.py`
Expected: No output.

- [ ] **Step 4: Commit**
```bash
git add provider/tongyi_aigc.yaml tools/__init__.py
git commit -m "feat: expose happyhorse tool in provider"
```