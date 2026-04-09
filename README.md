# TongYi AIGC

A powerful Dify plugin providing comprehensive AI-powered image and video generation capabilities using Alibaba Cloud Tongyi's latest Wanxiang, Qwen, and Z-Image models. Supports text-to-image, text-to-video, image-to-image, image-to-video, image translation, and more with professional-grade quality and flexible configuration options.

## Version Information

- **Current Version**: v0.0.1
- **Release Date**: 2026-02-16
- **Compatibility**: Dify Plugin Framework
- **Python Version**: 3.12

### Version History
- **v0.0.1** (2026-02-16): Initial release with image and video generation capabilities

## Quick Start

1. Install the plugin in your Dify environment
2. Configure your Alibaba Cloud API credentials (API Key from DashScope)
3. Start generating images and videos with AI

## Key Features
<img width="362" height="958" alt="CN" src="https://github.com/user-attachments/assets/240b3665-529f-4dc2-b572-7f9f7e277024" /><img width="318" height="954" alt="EN" src="https://github.com/user-attachments/assets/ea3b8fdb-379d-4159-a175-77edb3844db5" />

- **Multiple Generation Modes**: Text-to-image, text-to-video, image-to-image, image-to-video, image translation
- **Latest AI Models**: Supports wan2.6, qwen-image-max, qwen-image-plus, z-image-turbo for images; wan2.6-t2v, wan2.5-t2v-preview, wan2.2-t2v-plus for videos
- **Flexible Image Sizes**: Multiple aspect ratios from 1:1 to 21:9 with various resolutions
- **Video Generation**: Create videos with customizable duration (2-15 seconds) and synchronized audio
- **Image Translation**: Translate text in images with AI-powered OCR and translation (14+ languages)
- **First-Last Frame Video**: Create videos from first and last frame images
- **Reference Video**: Generate videos based on reference video style
- **Batch Generation**: Generate multiple images in a single request (up to 6 images)
- **Watermark Control**: Optional watermark for content authenticity

## Core Features

### Image Generation

#### Wan Text to Image (wan_text_2_image)
Generate images from text descriptions using Wanxiang models.
- **Supported Models**: wan2.6-t2i
- **Features**:
  - Multiple aspect ratios (1:1, 4:3, 3:4, 16:9, 9:16)
  - High resolution output (up to 1696*960)
  - Optional watermark
  - Prompt intelligent rewriting
  - Batch generation (1-4 images)
  - Negative prompt support

#### Wan Image to Image (wan_image_2_image)
Generate images from text and reference images using Wanxiang models.
- **Supported Models**: wan2.7-image-pro, wan2.7-image, wan2.6-image (compatibility)
- **Features**:
  - Reference image guided generation (1-9 images)
  - Multiple aspect ratios (1:1, 2:3, 3:2, 3:4, 4:3, 9:16, 16:9, 21:9)
  - 1K/2K presets for wan2.7 models
  - Optional watermark
  - Sequential grouped image output mode (wan2.7)
  - Interleaved text and image output mode (wan2.6 compatibility)
  - Prompt intelligent rewriting
  - Batch generation (1-4 images; up to 12 in wan2.7 sequential mode)

#### Qwen Text to Image (qwen_text_2_image)
Generate images using Qwen image models.
- **Supported Models**: qwen-image-max, qwen-image-max-2025-12-30, qwen-image-plus, qwen-image-plus-2026-01-09
- **Features**:
  - High quality image generation
  - Multiple aspect ratios (16:9, 4:3, 1:1, 3:4, 9:16)
  - Optional watermark
  - Prompt intelligent rewriting
  - Negative prompt support
  - Random seed for reproducibility

#### Qwen Image to Image (qwen_image_2_image)
Generate images from text and reference images using Qwen models.
- **Supported Models**: qwen-image-edit-max, qwen-image-edit-max-2026-01-16, qwen-image-edit-plus, qwen-image-edit-plus-2025-12-15, qwen-image-edit, qwen-image-edit-plus-2025-10-30
- **Features**:
  - Reference image guided generation (1-3 images)
  - Multiple aspect ratios (1:1, 2:3, 3:2, 3:4, 4:3, 9:16, 16:9, 21:9)
  - Optional watermark
  - Prompt intelligent rewriting
  - Batch generation (1-6 images)
  - High resolution output (up to 2048*872)

#### Z-Image Text to Image (z_image_text_2_image)
Generate images using Z-Image Turbo model.
- **Supported Models**: z-image-turbo
- **Features**:
  - Fast image generation
  - Extensive aspect ratio support (1:1, 2:3, 3:2, 3:4, 4:3, 7:9, 9:7, 9:16, 9:21, 16:9, 21:9)
  - Multiple resolution options (1024 to 2048 pixels)
  - Prompt intelligent rewriting
  - Random seed for reproducibility

#### Image Translation (qwen_image_translate)
Translate text in images with AI-powered OCR and translation.
- **Supported Models**: qwen-mt-image
- **Features**:
  - Automatic text detection
  - Multi-language translation (14 languages)
  - Supported languages: Chinese, English, Japanese, Korean, French, German, Spanish, Russian, Italian, Portuguese, Arabic, Thai, Vietnamese, Indonesian
  - Domain hint for improved translation
  - Sensitive words filtering
  - Terminology support

### Video Generation

#### Text to Video (wan_text_2_video)
Generate videos from text descriptions using Wanxiang models.
- **Supported Models**: wan2.7-t2v, wan2.6-t2v, wan2.5-t2v-preview, wan2.2-t2v-plus, wanx2.1-t2v-turbo, wanx2.1-t2v-plus
- **Features**:
  - Duration: 2-15 seconds (model dependent)
  - Resolution control: `resolution + ratio` (wan2.7) or `size` (wan2.6 and earlier)
  - Synchronized audio generation
  - Prompt intelligent rewriting
  - Single/Multi shot support (shot_type for wan2.6, prompt-driven for wan2.7)
  - Custom audio URL support
  - Negative prompt support

#### Image to Video (wan_first_image_2_video)
Generate video from a single image with text description.
- **Supported Models**: wan2.7-i2v, wan2.6-i2v, wan2.5-i2v-preview, wan2.2-i2v-flash, wan2.2-i2v-plus, wanx2.1-i2v-turbo, wanx2.1-i2v-plus
- **Features**:
  - Multi-modal inputs on wan2.7-i2v: first-frame, first+last frame, or video continuation
  - Single image input as first frame (legacy models)
  - Duration: 2-15 seconds (model dependent)
  - Resolution: 480P, 720P, 1080P
  - Synchronized audio generation
  - Video effect templates
  - Prompt intelligent rewriting
  - Single/Multi shot support

#### First-Last Frame Video (wan_first_end_image_2_video)
Generate video from first and last frame images.
- **Supported Models**: wan2.2-kf2v-flash
- **Features**:
  - First and last frame input
  - Smooth transition generation
  - Resolution: 480P, 720P, 1080P
  - Video effect templates
  - Prompt intelligent rewriting

#### Reference Video (wan_reference_video)
Generate videos based on reference video style.
- **Supported Models**: wan2.6-r2v, wan2.6-r2v-flash
- **Features**:
  - Reference videos or images input (up to 5)
  - Duration: 2-10 seconds
  - Resolution: 720P or 1080P (multiple aspect ratios)
  - Synchronized audio generation (wan2.6-r2v-flash only)
  - Single/Multi shot support
  - Prompt intelligent rewriting

#### Video Query (wan_video_query)
Query the status and results of video generation tasks.
- **Features**:
  - Real-time task status
  - Video download URL retrieval
  - Optional automatic video download

#### Image Translation Query (qwen_image_translate_query)
Query image translation task status and results.
- **Features**:
  - Real-time task status
  - Translated image retrieval

## Technical Advantages

- **Latest AI Models**: Access to Alibaba Cloud's newest Wanxiang, Qwen, and Z-Image models
- **High Quality Output**: Professional-grade image and video generation
- **Flexible Configuration**: Extensive parameter options for fine-tuning
- **Async Processing**: Efficient video generation with task-based workflow
- **Multi-Format Support**: Support for various image and video formats
- **Audio Generation**: Automatic synchronized audio for videos
- **Batch Processing**: Generate multiple images efficiently
- **Image Translation**: AI-powered text translation in images (14+ languages)

## Requirements

- Python 3.12
- Dify Platform access
- Alibaba Cloud API credentials (API Key from DashScope)
- Required Python packages (installed via requirements.txt):
  - dify_plugin>=0.2.0
  - requests>=2.31.0,<3.0.0
  - pillow>=10.0.0,<11.0.0

## Installation & Configuration

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure your Alibaba Cloud API credentials in the plugin settings:
   - **API Key**: Your Alibaba Cloud DashScope API key

3. Install the plugin in your Dify environment

## Usage

### Image Generation Tools

#### 1. Wan Text to Image
Generate images from text descriptions.
- **Parameters**:
  - `model`: Model version (default: wan2.6-t2i)
  - `prompt`: Text description of the image (required, <=2100 chars)
  - `negative_prompt`: Describe what you don't want (<=500 chars)
  - `size`: Image size (default: 1280*1280)
  - `n`: Number of images to generate (1-4, default: 3)
  - `prompt_extend`: Enable prompt intelligent rewriting (default: true)
  - `watermark`: Enable/disable watermark (default: true)
  - `seed`: Random seed for reproducibility

#### 2. Wan Image to Image
Generate images from text and reference images.
- **Parameters**:
  - `model`: Model version (default: wan2.7-image-pro)
  - `prompt`: Text description (required, <=5000 chars)
  - `images`: Reference image files (1-9 images, required)
  - `size`: Image size (default: 2K)
  - `n`: Number of images to generate (1-4, up to 12 when `enable_sequential=true` on wan2.7)
  - `enable_sequential`: Enable grouped image generation for wan2.7 (default: false)
  - `enable_interleave`: Enable interleaved output (default: false)
  - `prompt_extend`: Enable prompt intelligent rewriting (default: true)
  - `watermark`: Enable/disable watermark (default: true)

#### 3. Qwen Text to Image
Generate images using Qwen models.
- **Parameters**:
  - `prompt`: Text description (required)
  - `model`: Model version (default: qwen-image-max)
  - `size`: Image size (default: 1664*928)
  - `negative_prompt`: Describe what you don't want
  - `prompt_extend`: Enable prompt intelligent rewriting
  - `watermark`: Enable/disable watermark (default: true)
  - `seed`: Random seed for reproducibility

#### 4. Qwen Image to Image
Generate images from text and reference images using Qwen models.
- **Parameters**:
  - `prompt`: Text description (required)
  - `images`: Reference image files (1-3 images, required)
  - `model`: Model version (default: qwen-image-edit-max)
  - `size`: Image size (default: 1024*1024)
  - `n`: Number of images to generate (1-6, default: 3)
  - `prompt_extend`: Enable prompt intelligent rewriting
  - `watermark`: Enable/disable watermark (default: true)

#### 5. Z-Image Text to Image
Generate images using Z-Image Turbo.
- **Parameters**:
  - `prompt`: Text description (required, <=800 chars)
  - `model`: Model version (default: z-image-turbo)
  - `size`: Image size (default: 1024*1536)
  - `prompt_extend`: Enable prompt intelligent rewriting (default: false)
  - `seed`: Random seed for reproducibility

#### 6. Image Translation
Translate text in images.
- **Parameters**:
  - `image_url`: Image URL for translation (required)
  - `target_lang`: Target language (required)
  - `source_lang`: Source language (default: auto)
  - `domain_hint`: Domain hint for improved translation
  - `sensitives`: Sensitive words (JSON array)
  - `terminologies`: Terminologies (JSON array)
  - `model`: Model version (default: qwen-mt-image)

### Video Generation Tools

#### 7. Text to Video
Generate videos from text descriptions.
- **Parameters**:
  - `model`: Model version (default: wan2.6-t2v)
  - `prompt`: Text description (required)
  - `negative_prompt`: Describe what you don't want
  - `size`: Video resolution (default: 1920*1080)
  - `duration`: Duration in seconds (model dependent, default: 5)
  - `audio_url`: Custom audio file URL
  - `audio`: Auto generate audio (default: true)
  - `shot_type`: Single or multi shot (default: single)
  - `prompt_extend`: Enable prompt intelligent rewriting (default: true)
  - `watermark`: Enable/disable watermark (default: true)
  - `seed`: Random seed for reproducibility

#### 8. Image to Video
Generate video from an image or continue from a video clip.
- **Parameters**:
  - `model`: Model version (default: wan2.6-i2v, supports wan2.7-i2v)
  - `prompt`: Text description
  - `image_input` / `img_url`: First frame image input
  - `last_frame_input` / `last_frame_url`: Optional last frame image (wan2.7-i2v)
  - `first_clip_url`: Optional first clip video URL for continuation (wan2.7-i2v)
  - `resolution`: Video resolution (default: 1080P)
  - `duration`: Duration in seconds (model dependent, default: 5)
  - `template`: Video effect template
  - `audio_url`: Custom audio file URL (wan2.7-i2v only in first-frame modes)
  - `audio`: Auto generate audio (default: true)
  - `shot_type`: Single or multi shot (default: single)
  - `prompt_extend`: Enable prompt intelligent rewriting (default: true)
  - `watermark`: Enable/disable watermark (default: true)

#### 9. First-Last Frame Video
Generate video from first and last frame images.
- **Parameters**:
  - `model`: Model version (default: wan2.2-kf2v-flash)
  - `prompt`: Text description
  - `first_frame_image`: First frame image (required)
  - `last_frame_image`: Last frame image
  - `resolution`: Video resolution (default: 720P)
  - `template`: Video effect template
  - `prompt_extend`: Enable prompt intelligent rewriting (default: true)
  - `watermark`: Enable/disable watermark (default: true)

#### 10. Reference Video
Generate videos based on reference video style.
- **Parameters**:
  - `model`: Model version (default: wan2.6-r2v)
  - `prompt`: Text description (required, max 1500 chars)
  - `reference_urls`: Reference URLs (videos or images, max 5)
  - `size`: Video resolution (default: 1920*1080)
  - `duration`: Duration in seconds (2-10, default: 5)
  - `shot_type`: Single or multi shot (default: single)
  - `audio`: Auto generate audio (default: true, wan2.6-r2v-flash only)
  - `watermark`: Enable/disable watermark (default: true)

#### 11. Video Query
Query video generation task status.
- **Parameters**:
  - `task_id`: Video generation task ID (required)
  - `download_video`: Download video when available (default: false)

#### 12. Image Translation Query
Query image translation task status.
- **Parameters**:
  - `task_id`: Translation task ID (required)

## Notes

- Video generation is asynchronous; use Video Query to check status and retrieve results
- Image translation is asynchronous; use Image Translation Query to check status
- Duration limits vary by model (see model documentation in tool descriptions)
- Reference images should be under 10MB in size
- Watermark is enabled by default for content authenticity
- Prompt intelligent rewriting is enabled by default for better results

## Developer Information

- **Author**: `https://github.com/sawyer-shi`
- **Email**: sawyer36@foxmail.com
- **License**: Apache License 2.0
- **Source Code**: `https://github.com/sawyer-shi/dify-plugins-tongyi_aigc`
- **Support**: Through Dify platform and GitHub Issues

## License Notice

This project is licensed under Apache License 2.0. See [LICENSE](LICENSE) file for full license text.

---

**Ready to create stunning images and videos with AI?**
