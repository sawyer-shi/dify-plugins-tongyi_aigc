# author: sawyer-shi

import base64
import json
import logging
from collections.abc import Generator
from io import BytesIO
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from PIL import Image

logger = logging.getLogger(__name__)


class Wan2_5Image2ImageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Tongyi Wanxiang 2.5 image-to-image tool (async submit).
        """
        logger.info("Starting wan2.5 image-to-image task")

        try:
            api_key = self.runtime.credentials.get("api_key")
            if not api_key:
                msg = "❌ API密钥未配置"
                logger.error(msg)
                yield self.create_text_message(msg)
                return

            api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "X-DashScope-Async": "enable",
            }

            prompt = tool_parameters.get("prompt", "").strip()
            if not prompt:
                msg = "❌ 请输入提示词"
                logger.warning(msg)
                yield self.create_text_message(msg)
                return

            images = tool_parameters.get("images", [])
            if not images or not isinstance(images, list):
                msg = "❌ 请提供参考图像"
                logger.warning(msg)
                yield self.create_text_message(msg)
                return
            if len(images) > 3:
                msg = "❌ 最多支持3张参考图片"
                logger.warning(msg)
                yield self.create_text_message(msg)
                return

            model = tool_parameters.get("model", "wan2.5-i2i-preview")
            negative_prompt = tool_parameters.get("negative_prompt", "")
            prompt_extend = tool_parameters.get("prompt_extend")
            watermark = tool_parameters.get("watermark")
            n = tool_parameters.get("n")
            size = tool_parameters.get("size", "")
            seed = tool_parameters.get("seed")

            yield self.create_text_message("🚀 图生图任务启动中...")
            yield self.create_text_message(f"🤖 使用模型: {model}")
            yield self.create_text_message(
                f"📝 提示词: {prompt[:50]}{'...' if len(prompt) > 50 else ''}"
            )
            yield self.create_text_message(f"📷 参考图片数量: {len(images)}")
            yield self.create_text_message("⏳ 正在处理输入图像文件...")

            processed_images: list[str] = []
            for i, image_data in enumerate(images):
                processed_image = self._process_image(image_data)
                if not processed_image:
                    msg = f"❌ 第 {i + 1} 张图像处理失败"
                    logger.warning(msg)
                    yield self.create_text_message(msg)
                    return
                processed_images.append(processed_image)

            payload: dict[str, Any] = {
                "model": model,
                "input": {
                    "prompt": prompt,
                    "images": processed_images,
                },
                "parameters": {},
            }

            if negative_prompt:
                payload["input"]["negative_prompt"] = negative_prompt.strip()
            if prompt_extend is not None:
                payload["parameters"]["prompt_extend"] = prompt_extend
            if watermark is not None:
                payload["parameters"]["watermark"] = watermark
            if n is not None:
                try:
                    payload["parameters"]["n"] = int(n)
                except (TypeError, ValueError):
                    pass
            if size:
                payload["parameters"]["size"] = size
            if seed is not None:
                try:
                    payload["parameters"]["seed"] = int(seed)
                except (TypeError, ValueError):
                    pass

            logger.info("Submitting request: %s", json.dumps(payload, ensure_ascii=False))

            try:
                response = requests.post(
                    api_url,
                    headers=headers,
                    json=payload,
                    timeout=360,
                )
            except requests.exceptions.Timeout:
                msg = "❌ 请求超时，请稍后重试"
                logger.error(msg)
                yield self.create_text_message(msg)
                return
            except requests.exceptions.RequestException as e:
                msg = f"❌ 请求失败: {str(e)}"
                logger.error(msg)
                yield self.create_text_message(msg)
                return

            if response.status_code != 200:
                logger.error("API status %s: %s", response.status_code, response.text[:300])
                yield self.create_text_message(f"❌ API 响应状态码: {response.status_code}")
                if response.text:
                    yield self.create_text_message(f"🔧 响应内容: {response.text[:500]}")
                return

            try:
                resp_data = response.json()
            except json.JSONDecodeError as e:
                logger.error("Failed to parse JSON: %s - %s", str(e), response.text[:300])
                yield self.create_text_message("❌ API 响应解析失败（非JSON）")
                return

            yield self.create_text_message(self._format_response_text(resp_data))
            yield self.create_json_message(resp_data)
            logger.info("Wan2.5 image-to-image task submitted")

        except Exception as e:
            error_msg = f"❌ 生成图像时出现未预期错误: {str(e)}"
            logger.exception(error_msg)
            yield self.create_text_message(error_msg)

    @staticmethod
    def _process_image(image_data: Any) -> str:
        if not image_data:
            return ""

        if hasattr(image_data, "blob"):
            image_bytes = image_data.blob
        elif hasattr(image_data, "read") and callable(getattr(image_data, "read")):
            image_bytes = image_data.read()
            if isinstance(image_bytes, str):
                image_bytes = image_bytes.encode("utf-8")
        elif isinstance(image_data, bytes):
            image_bytes = image_data
        elif isinstance(image_data, str) and image_data.startswith("data:"):
            try:
                _, base64_data = image_data.split(",", 1)
                image_bytes = base64.b64decode(base64_data)
            except Exception:
                return ""
        elif isinstance(image_data, str) and image_data.startswith(("http://", "https://")):
            return image_data
        elif isinstance(image_data, str) and len(image_data) < 1000:
            try:
                with open(image_data, "rb") as image_file:
                    image_bytes = image_file.read()
            except Exception:
                return ""
        elif isinstance(image_data, str):
            try:
                image_bytes = base64.b64decode(image_data)
            except Exception:
                return ""
        else:
            return ""

        if not isinstance(image_bytes, bytes) or len(image_bytes) == 0:
            return ""

        if len(image_bytes) > 10 * 1024 * 1024:
            return ""

        try:
            image = Image.open(BytesIO(image_bytes))
            if image.width < 384 or image.height < 384:
                return ""
            if image.width > 5000 or image.height > 5000:
                return ""
            aspect_ratio = image.width / image.height
            if aspect_ratio > 4 or aspect_ratio < 0.25:
                return ""

            if image.mode == "RGBA":
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            elif image.mode == "P":
                image = image.convert("RGB")

            output_buffer = BytesIO()
            image.save(output_buffer, format="JPEG", quality=85, optimize=True)
            processed_bytes = output_buffer.getvalue()

            base64_string = base64.b64encode(processed_bytes).decode("utf-8")
            return f"data:image/jpeg;base64,{base64_string}"
        except Exception as e:
            logger.error("Error processing image: %s", str(e))
            return ""

    @staticmethod
    def _format_response_text(result_data: dict[str, Any]) -> str:
        request_id = result_data.get("request_id", "unknown")
        output = result_data.get("output", {})
        task_id = output.get("task_id", "unknown")
        task_status = output.get("task_status", "unknown")

        input_data = result_data.get("input", {})
        prompt = input_data.get("prompt", "unknown")
        images = input_data.get("images", [])
        image_count = len(images)
        model = input_data.get("model", "wan2.5-i2i-preview")

        response_text = f"""
🎨 Wanxiang V2.5 图像编辑任务已提交！

📋 任务详情:
   • 任务ID: {task_id}
   • 状态: {task_status}
   • 模型: {model}
   • 参考图片数量: {image_count}

📝 Prompt: {prompt}

💡 Next Steps:
   • Use the Wanxiang V2.5 Image Query tool to check progress
   • Task ID: {task_id}
   • Status will update from 'PENDING' → 'RUNNING' → 'SUCCEEDED'/'FAILED'

📊 API Response Summary:
   • Request ID: {request_id}
   • Endpoint: /api/v1/services/aigc/image2image/image-synthesis
   • Method: POST
   • Status: Success (200)
   • Task Status: {task_status}
"""
        return response_text.strip()
