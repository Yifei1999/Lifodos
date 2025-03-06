import asyncio
import json
import httpx
from config_load import LLM_PROXY


def response(message: list):
    headers = {"Content-Type": "application/json"}
    js = {
        "model": "glm4",
        "stream": False,
        "messages": message,
        # "keep-alive": 0
    }
    res = httpx.post("http://localhost:11434/api/chat", json=js, headers=headers, timeout=999)
    return res

async def async_request_proxy(messages: list):
    request = {
        "model": LLM_PROXY["model"],
        "stream": False,
        "messages": messages,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(LLM_PROXY["base_url"], json=request, timeout=999)
        return response.json()


if __name__ == "__main__":
    messages = [
        {"role": "system", "content": "you are a professor"},
        {"role": "user", "content": "Hello!"},
        # {"role": "assistant", "content": "Hi there!"},
        # {"role": "user", "content": "Can you help me with Python coding?"}
    ]

    data = asyncio.run(async_request_proxy(messages))
    print(data)