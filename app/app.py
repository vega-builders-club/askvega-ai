# Application Api
import uvicorn
import logging
import pickle

from pathlib import Path
from typing import Optional
from starlette.applications import Starlette
from starlette.websockets import WebSocket
from starlette.routing import WebSocketRoute
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from langchain.vectorstores import VectorStore

from callback import QuestionGenCallbackHandler, StreamingLLMCallbackHandler
from qa_chain import get_chain
from schema import ChatResponse

vectorstore: Optional[VectorStore] = None


async def load_vectorstore():
    print("Server is Good to go!!!")
    logging.info("Loading vectorstore")
    if not Path("askvega.pk1").exists():
        raise ValueError("Please run the indexer first")
    with open("askvega.pk1", "rb") as f:
        global vectorstore
        vectorstore = pickle.load(f)


async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    question_handler = QuestionGenCallbackHandler(websocket)
    stream_handler = StreamingLLMCallbackHandler(websocket)
    qa_chain = get_chain(vectorstore, question_handler, stream_handler)
    chat_history = []

    # Process Incoming Messages
    while True:
        try:
            # Receive and send message back to the client
            question = await websocket.receive_text()
            resp = ChatResponse(sender="you", message=question, type="stream")
            await websocket.send_json(resp.dict())

            # Construct Response
            start_resp = ChatResponse(sender="bot", message="", type="start")
            await websocket.send_json(start_resp.dict())

            response = await qa_chain.acall({
                "question": question, "chat_history": chat_history
            })
            chat_history.append((question, response["answer"]))

            end_resp = ChatResponse(sender="bot", message="", type="end")
            await websocket.send_json(end_resp.dict())
        except Exception as e:
            logging.error(e)
            resp = ChatResponse(
                sender="bot", message="Sorry, something went wrong. Try again.", type="error")
            await websocket.send_json(resp.dict())

routes = [
    WebSocketRoute("/ws", websocket_endpoint)
]

middleware = [
    Middleware(CORSMiddleware, allow_origins=['*'], allow_methods=["*"],
               allow_headers=["*"],)
]

app = Starlette(debug=True, routes=routes, on_startup=[
                load_vectorstore], middleware=middleware)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
