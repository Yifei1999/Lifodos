import asyncio
import fastapi
import uvicorn
from contextlib import asynccontextmanager
from logger import mylogger

from application.auto_chat_bot.chatgraph_usage import create_instance

user_session = {}

@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    mylogger.info("service has been initiated")

    yield

    mylogger.info("service has been terminated")
    return

app = fastapi.FastAPI(lifespan=lifespan)

# TODO: path to be fixed
# app.mount("/static", StaticFiles(directory=os.path.dirname(__file__) + "/template/static"), name="static")


@app.get("/")
async def root():
    return fastapi.Response(
        status_code=200,
        content="hello, welcome to Lifodos!",
        media_type="text/plain"
    )


@app.post("/chatgraph")
async def chat(request: fastapi.Request):
    request_js = await request.json()

    user_id = request_js["user_id"]
    user_message = request_js["user_message"]

    if user_id not in user_session:
        graph = create_instance()
        task = asyncio.create_task(graph.stream({"messages": []}))

        user_session[user_id] = {
            "graph": graph,
            "task": task
        }
    else:
        graph = user_session[user_id]["graph"]

    await graph.add_user_input(user_message)
    response_msg = await graph.get_system_response()
    return {"response": response_msg}


if __name__ == "__main__":
    print("INFO:     Running on http://127.0.0.1:80")
    uvicorn.run(app, host="0.0.0.0", port=80)
