import json
import os
import asyncio
import fastapi
from concurrent.futures import ThreadPoolExecutor
import uvicorn
from contextlib import asynccontextmanager
from logger import mylogger
from datetime import datetime

import feishu

from free_chat import create_instance
from taskgraph.chat import Message

async def ping():
    while True:
        await asyncio.sleep(5)

        print("hello")

@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    mylogger.info("service has been initiated")

    asyncio.create_task(ping())

    yield

    mylogger.info("service has been terminated")
    return

app = fastapi.FastAPI(lifespan=lifespan)
user_pool = {}


@app.get("/")
async def root():
    return fastapi.Response(
        status_code=200,
        content="hello, welcome to Lifodos!",
        media_type="text/plain"
    )

@app.post("/feishu/send-msg")
async def chat(request: fastapi.Request):
    request_js = await request.json()

    user_id  = request_js["open_id"]
    message_body = request_js["message"]

    if user_id not in user_pool:
        graph = create_instance()
        user_pool[user_id] = graph
        asyncio.create_task(graph.stream({
            "user_id": user_id,
            "messages": []
        }))

    graph = user_pool[user_id]
    message = json.loads(message_body["content"])["text"]
    timestamp_ms = message_body["create_time"]
    timestamp_s = int(timestamp_ms) // 1000

    dt = datetime.fromtimestamp(timestamp_s)
    formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')

    graph.add_user_input(Message(message, role="user", create_time=formatted_time))
    return "ok"


if __name__ == "__main__":
    print("INFO:     Running on http://127.0.0.1:80")
    uvicorn.run(app, host="0.0.0.0", port=80)
