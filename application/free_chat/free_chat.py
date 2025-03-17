import asyncio

from datetime import datetime

from logger import mylogger
from taskgraph import START_NAME
from taskgraph.chat import ChatState, ChatGraph, Message
from llm import async_request_proxy
import feishu


class MyChatState(ChatState):
    user_id: str


def create_instance():
    graph = ChatGraph(MyChatState)

    @graph.user_input
    async def update_user_message(state: MyChatState) -> MyChatState:
        return state

    @graph.register
    async def generate_response(state: MyChatState) -> MyChatState:
        message_ordered = sorted(state["messages"], key=lambda x: x["create_time"], reverse=False)
        message_ls = [{"role": each["role"], "content": each["content"]} for each in message_ordered]

        start_dt = datetime.now()
        formatted_create_time = start_dt.strftime("%Y-%m-%d %H:%M:%S")

        message = await async_request_proxy(message_ls)

        state["messages"] += [Message(message["content"], create_time=formatted_create_time, role="assistant")]
        return state

    @graph.system_response
    async def send_response(state: MyChatState) -> MyChatState:
        # send message to FeiShu
        mylogger.info(f'send new message: {state["messages"][-1]["content"]}')
        feishu.feishu_send_msg(state["messages"][-1]["content"], user_id=state["user_id"])
        return state

    @graph.register
    async def waiting_after_response(state: MyChatState) -> MyChatState:
        await asyncio.sleep(5)
        return state

    graph.add_node(update_user_message, "update_user_message", trigger_type="SUFFICIENT")
    graph.add_node(generate_response, "generate_response")
    graph.add_node(send_response, "send_response")
    graph.add_node(waiting_after_response, "waiting_after_response")

    graph.add_edge(START_NAME, "update_user_message")
    graph.add_edge("update_user_message", "generate_response")
    graph.add_edge("generate_response", "send_response")
    graph.add_edge("send_response", "waiting_after_response")
    graph.add_edge("waiting_after_response", "update_user_message")

    graph.compile()
    return graph
