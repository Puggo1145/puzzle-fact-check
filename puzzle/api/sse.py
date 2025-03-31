# sse.py
import asyncio
import json
from typing import Any, AsyncGenerator

class SSEManager:
    def __init__(self):
        # 使用 asyncio 队列保存待发送的事件
        self.event_queue = asyncio.Queue()

    async def send_event(self, event_type: str, data: Any) -> None:
        """将事件放入队列，数据会被 JSON 序列化"""
        event = {"event": event_type, "data": data}
        await self.event_queue.put(event)

    async def event_generator(self) -> AsyncGenerator[str, None]:
        """
        异步生成 SSE 格式的事件字符串
        每个事件格式为：
            event: <event_type>
            data: <json_serialized_data>
        """
        while True:
            event = await self.event_queue.get()
            data = json.dumps(event["data"], ensure_ascii=False)
            yield f"event: {event['event']}\ndata: {data}\n\n"
