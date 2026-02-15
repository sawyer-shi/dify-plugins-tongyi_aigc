# author: sawyer-shi

import base64
import json
import logging
from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

logger = logging.getLogger(__name__)


class WanReferenceVideoTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Tongyi Wanxiang reference-to-video tool (async submit).
        """
        logger.info("Starting wan reference-to-video task")

        try:
            model = tool_parameters.get("model", "wan2.6-r2v").strip()
            api_key = self.runtime.credentials.get("api_key")
            if not api_key:
                msg = "❌ API密钥未配置"
                logger.error(msg)
                yield self.create_text_message(msg)
                return

            reference_videos_str = tool_parameters.get("reference_videos", "").strip()
            if not reference_videos_str:
                yield self.create_text_message("❌ 请提供参考视频")
                return

            reference_videos = [
                url.strip()
                for url in reference_videos_str.split(";")
                if url.strip()
            ]
            if len(reference_videos) > 3:
                yield self.create_text_message("❌ 最多支持3个参考视频")
                return

            processed_videos: list[str] = []
            for video_url in reference_videos:
                processed_video = self._process_video(video_url)
                if not processed_video:
                    yield self.create_text_message(f"❌ 无效的视频: {video_url}")
                    return
                processed_videos.append(processed_video)

            prompt = tool_parameters.get("prompt", "").strip()
            if not prompt:
                yield self.create_text_message("❌ 请输入提示词")
                return

            payload: dict[str, Any] = {
                "model": model,
                "input": {
                    "reference_video_urls": processed_videos,
                    "prompt": prompt[:1500],
                },
                "parameters": {},
            }

            negative_prompt = tool_parameters.get("negative_prompt", "").strip()
            if negative_prompt:
                payload["input"]["negative_prompt"] = negative_prompt[:500]

            params = payload["parameters"]
            size = tool_parameters.get("size", "1920*1080").strip()
            if size:
                params["size"] = size
            duration = tool_parameters.get("duration", 5)
            if duration is not None:
                try:
                    params["duration"] = int(duration)
                except (TypeError, ValueError):
                    pass
            shot_type = tool_parameters.get("shot_type", "single").strip()
            if shot_type:
                params["shot_type"] = shot_type
            if tool_parameters.get("audio") is not None:
                params["audio"] = tool_parameters.get("audio")
            if tool_parameters.get("watermark") is not None:
                params["watermark"] = tool_parameters.get("watermark")
            if tool_parameters.get("seed") is not None:
                try:
                    params["seed"] = int(tool_parameters.get("seed"))
                except (TypeError, ValueError):
                    pass

            api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/video-generation/video-synthesis"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "X-DashScope-Async": "enable",
            }

            debug_payload = json.loads(json.dumps(payload))
            for i, url in enumerate(debug_payload["input"]["reference_video_urls"]):
                if len(url) > 200:
                    debug_payload["input"]["reference_video_urls"][
                        i
                    ] = "data:video/...[Base64 Hidden]"
            logger.info("Request Payload: %s", json.dumps(debug_payload, ensure_ascii=False))

            yield self.create_text_message("🚀 参考生视频任务启动中...")
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
            else:
                yield self.create_text_message(
                    f"❌ 响应格式异常: {response.text[:500]}"
                )

            logger.info("Wan reference-to-video task submitted")

        except Exception as e:
            error_msg = f"❌ 生成视频时出现未预期错误: {str(e)}"
            logger.exception(error_msg)
            yield self.create_text_message(error_msg)

    @staticmethod
    def _format_success_message(result_data: dict[str, Any]) -> str:
        task_id = result_data.get("output", {}).get("task_id", "unknown")
        task_status = result_data.get("output", {}).get("task_status", "unknown")
        return (
            f"🎬 参考生视频任务已提交\nID: {task_id}\nStatus: {task_status}\n"
            "请稍后查询结果。"
        )

    @staticmethod
    def _process_video(video_data: Any) -> str:
        if not video_data:
            return ""

        if isinstance(video_data, str) and (
            video_data.startswith("http") or video_data.startswith("data:")
        ):
            return video_data.strip()

        video_bytes = None
        if hasattr(video_data, "blob"):
            video_bytes = video_data.blob
        elif hasattr(video_data, "read"):
            video_bytes = video_data.read()
        elif isinstance(video_data, bytes):
            video_bytes = video_data

        if not video_bytes:
            return ""

        if len(video_bytes) > 100 * 1024 * 1024:
            logger.error("Video size exceeds 100MB limit")
            return ""

        try:
            b64_str = base64.b64encode(video_bytes).decode("utf-8")
            return f"data:video/mp4;base64,{b64_str}"
        except Exception as e:
            logger.error("Video processing failed: %s", str(e))
            return ""
