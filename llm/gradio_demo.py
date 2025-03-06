import gradio as gr
import openai

# 配置 OpenAI API 密钥
openai.api_key = "your_openai_api_key"  # 替换为你的 OpenAI API 密钥


# 定义聊天函数
def chat(message, history):
    # 将历史对话转换为 OpenAI 的消息格式

    #
    # # 调用 OpenAI API 获取回复
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",  # 或其他支持的模型
    #     messages=messages
    # )
    print(history)





    return "1"


# 创建 Gradio 聊天界面
demo = gr.ChatInterface(fn=chat, title="LLM Chat Interface", type="messages")
demo.launch()