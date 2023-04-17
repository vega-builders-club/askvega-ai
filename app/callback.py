# Callback Handler
from typing import Any, Dict
from langchain.callbacks.base import AsyncCallbackHandler
from schema import ChatResponse


class StreamingLLMCallbackHandler(AsyncCallbackHandler):
    def __init__(self, websocket):
        self.websocket = websocket

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        resp = ChatResponse(sender="bot", message=token, type="stream")
        await self.websocket.send_json(resp.dict())


class QuestionGenCallbackHandler(AsyncCallbackHandler):
    def __init__(self, websocket) -> None:
        self.websocket = websocket

    async def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> None:
        resp = ChatResponse(
            sender="bot", message="Synthesizing question...", type="info")
        await self.websocket.send_json(resp.dict())
