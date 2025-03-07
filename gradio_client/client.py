import gradio as gr
import httpx


async def chat(message, history):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:80/chat",
            json={"user_id": "liuyifei", "user_message": message},
            timeout=999
        )

    reply = response.json()["response"]
    return reply


demo = gr.ChatInterface(fn=chat, title="LLM Chat Interface", type="messages")
demo.launch()