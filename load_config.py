import json

from langchain.chains.question_answering.map_reduce_prompt import messages
from openai import OpenAI

client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/api/chat"
)

client.chat.completions.create(
    model="glm4",
    messages=[{"role": "system", "content": ""}]
)