# author: sawyer-shi

import json
import logging
from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

logger = logging.getLogger(__name__)


class WanImageQueryTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Query Tongyi Wanxiang image generation task status and results.
        """
        logger.info("Starting wan image query")

        try:
            task_id = tool_parameters.get("task_id", "").strip()
            if not task_id:
                yield self.create_text_message("❌ 请输入任务ID")
                return

            api_key = self.runtime.credentials.get("api_key")
            if not api_key:
                yield self.create_text_message("❌ API密钥未配置")
                return

            api_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }

            yield self.create_text_message("🔍 正在查询图像生成结果...")
            yield self.create_text_message(f"📋 任务ID: {task_id}")

            try:
                response = requests.get(api_url, headers=headers, timeout=60)
            except requests.exceptions.Timeout:
                yield self.create_text_message("❌ 请求超时，请稍后重试")
                return
            except requests.exceptions.RequestException as e:
                yield self.create_text_message(f"❌ 请求失败: {str(e)}")
                return

            if response.status_code != 200:
                yield self.create_text_message(f"❌ API 响应状态码: {response.status_code}")
                if response.text:
                    yield self.create_text_message(f"🔧 响应内容: {response.text[:500]}")
                return

            try:
                result_data = response.json()
            except json.JSONDecodeError as e:
                logger.error("Failed to parse JSON: %s - %s", str(e), response.text[:300])
                yield self.create_text_message("❌ API 响应解析失败（非JSON）")
                return

            yield self.create_text_message(self._format_response_text(result_data))
            yield self.create_json_message(result_data)

            output = result_data.get("output", {})
            task_status = output.get("task_status")
            if task_status == "SUCCEEDED":
                image_urls = self._extract_image_urls(output)
                if image_urls:
                    for image_url in image_urls:
                        yield self.create_image_message(image_url)
                else:
                    yield self.create_text_message("❌ 未找到图像结果")

            logger.info("Wan image query completed")

        except Exception as e:
            error_msg = f"❌ 查询图像结果时出现未预期错误: {str(e)}"
            logger.exception(error_msg)
            yield self.create_text_message(error_msg)

    @staticmethod
    def _extract_image_urls(output: dict[str, Any]) -> list[str]:
        image_urls: list[str] = []
        choices = output.get("choices")
        if isinstance(choices, list):
            for choice in choices:
                message = choice.get("message", {})
                content_items = message.get("content", [])
                for content_item in content_items:
                    if content_item.get("type") == "image" and "image" in content_item:
                        image_url = content_item.get("image", "").strip()
                        if image_url.startswith("`") and image_url.endswith("`"):
                            image_url = image_url[1:-1].strip()
                        if image_url:
                            image_urls.append(image_url)

        results = output.get("results")
        if isinstance(results, list):
            for result in results:
                image_url = result.get("url", "").strip()
                if image_url.startswith("`") and image_url.endswith("`"):
                    image_url = image_url[1:-1].strip()
                if image_url:
                    image_urls.append(image_url)

        image_url = output.get("image_url", "").strip()
        if image_url:
            if image_url.startswith("`") and image_url.endswith("`"):
                image_url = image_url[1:-1].strip()
            if image_url:
                image_urls.append(image_url)

        return image_urls

    @staticmethod
    def _format_response_text(result_data: dict[str, Any]) -> str:
        request_id = result_data.get("request_id", "unknown")
        output = result_data.get("output", {})
        usage = result_data.get("usage", {})

        task_id = output.get("task_id", "unknown")
        task_status = output.get("task_status", "unknown")
        submit_time = output.get("submit_time", "unknown")
        scheduled_time = output.get("scheduled_time", "unknown")
        end_time = output.get("end_time", "unknown")
        finished = output.get("finished", False)
        image_count = usage.get("image_count", 0)
        size = usage.get("size", "unknown")

        if task_status == "SUCCEEDED":
            response_text = f"""
🎉 万相图像任务完成！

📋 任务详情:
   • 任务ID: {task_id}
   • 状态: {task_status}
   • 提交时间: {submit_time}
   • 调度时间: {scheduled_time}
   • 完成时间: {end_time}
   • 完成标记: {finished}
   • 图片数量: {image_count}
   • 图片尺寸: {size}

📊 API 响应摘要:
   • Request ID: {request_id}
   • Endpoint: /api/v1/tasks/{task_id}
   • Method: GET
   • Status: Success (200)
"""
        elif task_status == "FAILED":
            code = output.get("code", "unknown") or result_data.get("code", "unknown")
            message = output.get("message", "") or result_data.get(
                "message", "No error message"
            )
            response_text = f"""
❌ 万相图像任务失败

📋 任务详情:
   • 任务ID: {task_id}
   • 状态: {task_status}
   • 提交时间: {submit_time}
   • 调度时间: {scheduled_time}
   • 完成时间: {end_time}
   • 完成标记: {finished}

🚫 错误信息:
   • 错误代码: {code}
   • 错误信息: {message}

📊 API 响应摘要:
   • Request ID: {request_id}
   • Endpoint: /api/v1/tasks/{task_id}
   • Method: GET
   • Status: Success (200)
"""
        else:
            response_text = f"""
⏳ 万相图像任务处理中

📋 任务详情:
   • 任务ID: {task_id}
   • 状态: {task_status}
   • 提交时间: {submit_time}
   • 调度时间: {scheduled_time}

📊 API 响应摘要:
   • Request ID: {request_id}
   • Endpoint: /api/v1/tasks/{task_id}
   • Method: GET
   • Status: Success (200)
"""

        return response_text.strip()
