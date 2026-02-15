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


class WanFirstEndImage2VideoTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Tongyi Wanxiang first/last frame image-to-video tool (async submit).
        """
        logger.info("Starting wan first/last frame image-to-video task")

        try:
            model = tool_parameters.get("model", "wan2.2-kf2v-flash").strip()
            api_key = self.runtime.credentials.get("api_key")
            if not api_key:
                msg = "❌ API密钥未配置"
                logger.error(msg)
                yield self.create_text_message(msg)
                return

            first_frame_image = tool_parameters.get("first_frame_image")
            last_frame_image = tool_parameters.get("last_frame_image")
            template = tool_parameters.get("template", "").strip()

            if template and not last_frame_image:
                last_frame_image = first_frame_image

            if template:
                processed_first = self._process_image(first_frame_image)
                if not processed_first:
                    yield self.create_text_message("❌ 请提供首帧图片")
                    return
                processed_last = (
                    self._process_image(last_frame_image)
                    if last_frame_image
                    else processed_first
                )
            else:
                processed_first = self._process_image(first_frame_image)
                processed_last = self._process_image(last_frame_image)
                if not processed_first:
                    yield self.create_text_message("❌ 请提供首帧图片")
                    return
                if not processed_last:
                    yield self.create_text_message("❌ 请提供尾帧图片")
                    return

            prompt = tool_parameters.get("prompt", "").strip()
            if not template and not prompt:
                yield self.create_text_message("❌ 非模板模式下必须提供提示词")
                return

            payload: dict[str, Any] = {
                "model": model,
                "input": {
                    "first_frame_url": processed_first,
                },
                "parameters": {},
            }

            if not template:
                payload["input"]["last_frame_url"] = processed_last
            if template:
                payload["input"]["template"] = template
                payload["input"]["last_frame_url"] = processed_last
            if not template and prompt:
                payload["input"]["prompt"] = prompt[:800]

            negative_prompt = tool_parameters.get("negative_prompt", "").strip()
            if negative_prompt:
                payload["input"]["negative_prompt"] = negative_prompt[:500]

            params = payload["parameters"]
            resolution = tool_parameters.get("resolution", "720P").strip()
            if resolution:
                params["resolution"] = resolution
            params["duration"] = 5
            if tool_parameters.get("prompt_extend") is not None:
                params["prompt_extend"] = tool_parameters.get("prompt_extend")
            if tool_parameters.get("watermark") is not None:
                params["watermark"] = tool_parameters.get("watermark")
            if tool_parameters.get("seed") is not None:
                try:
                    params["seed"] = int(tool_parameters.get("seed"))
                except (TypeError, ValueError):
                    pass

            api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2video/video-synthesis"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "X-DashScope-Async": "enable",
            }

            debug_payload = json.loads(json.dumps(payload))
            if len(debug_payload["input"]["first_frame_url"]) > 200:
                debug_payload["input"]["first_frame_url"] = "data:image/...[Base64 Hidden]"
            if "last_frame_url" in debug_payload["input"] and len(
                debug_payload["input"]["last_frame_url"]
            ) > 200:
                debug_payload["input"]["last_frame_url"] = "data:image/...[Base64 Hidden]"
            logger.info("Request Payload: %s", json.dumps(debug_payload, ensure_ascii=False))

            yield self.create_text_message("🚀 首尾帧图生视频任务启动中...")
            yield self.create_text_message(f"🤖 使用模型: {model}")
            yield self.create_text_message("⏳ 正在连接通义API...")

            try:
                response = requests.post(
                    api_url,
                    headers=headers,
                    json=payload,
                    timeout=60,
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
                yield self.create_text_message(f"❌ API 响应状态码: {response.status_code}")
                if response.text:
                    yield self.create_text_message(f"🔧 响应内容: {response.text[:500]}")
                return

            try:
                result_data = response.json()
            except json.JSONDecodeError:
                yield self.create_text_message("❌ API 响应解析失败（非JSON）")
                return

            if "output" in result_data:
                yield self.create_text_message(self._format_success_message(result_data))
                yield self.create_json_message(result_data)
                logger.info("Wan first/last frame task submitted")
            else:
                yield self.create_text_message(
                    f"❌ 响应格式异常: {response.text[:500]}"
                )

        except Exception as e:
            error_msg = f"❌ 生成视频时出现未预期错误: {str(e)}"
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
            if image.width < 360 or image.width > 2000 or image.height < 360 or image.height > 2000:
                return ""
            if image.mode == "RGBA":
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            elif image.mode == "P":
                image = image.convert("RGB")
            elif image.mode != "RGB":
                image = image.convert("RGB")

            output_buffer = BytesIO()
            image.save(output_buffer, format="JPEG", quality=95)
            processed_bytes = output_buffer.getvalue()
            base64_string = base64.b64encode(processed_bytes).decode("utf-8")
            return f"data:image/jpeg;base64,{base64_string}"
        except Exception as e:
            logger.error("Error processing image: %s", str(e))
            return ""

    @staticmethod
    def _format_success_message(result_data: dict[str, Any]) -> str:
        task_id = result_data.get("output", {}).get("task_id", "unknown")
        task_status = result_data.get("output", {}).get("task_status", "unknown")
        request_id = result_data.get("request_id", "unknown")
        response_text = f"""
🎬 首尾帧图生视频任务已提交！

📋 任务详情:
   • Task ID: {task_id}
   • Status: {task_status}
   • Request ID: {request_id}

💡 Next Steps:
   • Use the Video Query tool to check progress
   • Task ID: {task_id}
   • Status will update from 'PENDING' → 'RUNNING' → 'SUCCEEDED'/'FAILED'

📊 API Response Summary:
   • Endpoint: /api/v1/services/aigc/image2video/video-synthesis
   • Method: POST
   • Status: Success (200)
   • Task Status: {task_status}
"""
        return response_text.strip()
