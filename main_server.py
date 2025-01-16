import os
import fastapi
from fastapi.staticfiles import StaticFiles
import uvicorn
from contextlib import asynccontextmanager
from logger import mylogger


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    mylogger.info("service has been initiated")

    yield

    mylogger.info("service has been terminated")
    return

app = fastapi.FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=os.path.dirname(__file__) + "/template/static"), name="static")


@app.get("/")
async def root():
    return fastapi.Response(
        status_code=200,
        content="hello, welcome to Lifodos!",
        media_type="text/plain"
    )


if __name__ == "__main__":
    print("INFO:     Running on http://127.0.0.1:80")
    uvicorn.run(app, host="0.0.0.0", port=80)
