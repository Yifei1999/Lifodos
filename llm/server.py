import asyncio
import json
import httpx
from config_load import LLM_PROXY
from openai import AsyncOpenAI


def response(message: list):
    headers = {"Content-Type": "application/json"}
    js = {
        "model": "glm4",
        "stream": False,
        "messages": message,
        # "keep-alive": 0
    }
    res = httpx.post("http://localhost:11434/v1/chat/completions", json=js, headers=headers, timeout=999)
    return res

async def async_request_proxy(messages: list):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f'Bearer {LLM_PROXY["api_key"]}'
    }

    request = {
        "model": LLM_PROXY["model"],
        "stream": False,
        "messages": messages,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=LLM_PROXY["base_url"] + "/chat/completions",
            headers=headers,
            json=request,
            timeout=999
        )
        return response.json()["choices"][0]["message"]

# async def async_request_proxy(messages: list):
#     client = AsyncOpenAI(
#         base_url=LLM_PROXY["base_url"],
#         api_key=LLM_PROXY["api_key"]
#     )
#     response = await client.chat.completions.create(
#         model=LLM_PROXY["model"],
#         messages=messages,
#         temperature=0,
#         max_tokens=1024
#     )
#
#     # 输出生成的文本
#     return json.loads(response.model_dump_json())["choices"][0]["message"]


if __name__ == "__main__":
    messages = [
        {"role": "system", "content": "you are a professor"},
        {"role": "user", "content": "Hello!"},
        # {"role": "assistant", "content": "Hi there!"},
        # {"role": "user", "content": "Can you help me with Python coding?"}
    ]

    data = asyncio.run(async_request_proxy(messages))
    print(data)


