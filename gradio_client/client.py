import gradio as gr
import openai
import httpx



async def chat(message, history):
    # 将历史对话转换为 OpenAI 的消息格式
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:80/chat",
            json={"user_id": "liuyifei", "user_message": message}
        )

    reply = response.json()["response"]
    return reply


# 创建 Gradio 聊天界面
demo = gr.ChatInterface(fn=chat, title="LLM Chat Interface", type="messages")
demo.launch()