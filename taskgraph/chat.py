import asyncio
import networkx as nx
from pydantic import TypeAdapter, ValidationError
from datetime import datetime
from typing import (
    Any,
    Callable,
    Literal,
    NamedTuple,
    Optional,
    Sequence,
    Type,
    Union,
    Annotated
)
try:
    from .state import State
    from .graph import TaskGraph
except ImportError as e:
    from state import State
    from graph import TaskGraph
from llm.server import async_request_proxy


class ChatState(State):
    messages: list


class ChatGraph(TaskGraph):
    def __init__(self, state_schema: Type[Any] = ChatState):
        super().__init__(state_schema)

        self._user_input_event = asyncio.Event()
        self._user_input_event.clear()
        self._system_response_event = asyncio.Event()
        self._system_response_event.clear()
        self._message_buffer = None

    async def set_user_input(self, user_input: str):
        self._message_buffer = user_input
        self._user_input_event.set()

    async def get_system_response(self):
        await self._system_response_event.wait()

        message =  self._message_buffer
        self._system_response_event.clear()
        return message

    def user_input(self, func: Callable):
        async def user_input_wrapper(*args, **kwargs):
            await self._user_input_event.wait()

            result = await func(*args, **kwargs)

            result["messages"] += [{"role": "user", "content": self._message_buffer}]
            self._message_buffer = None
            self._user_input_event.clear()
            return result
        return user_input_wrapper

    def system_response(self, func: Callable):
        async def system_response_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            self._message_buffer = result["messages"][-1]["content"]
            self._system_response_event.set()
            return result
        return system_response_wrapper

    def save_context(self):
        pass

    def load_context(self):
        pass


if __name__ == "__main__":
    from taskgraph import State, START_NAME, END_NAME

    async def main():
        class MyChatState(ChatState):
            pass

        chat = ChatGraph(MyChatState)

        @chat.register
        async def generate_response(state: MyChatState) -> MyChatState:
            message = await async_request_proxy(state["messages"])
            state["messages"] += [{"role": "assistant", "content": message["content"]}]
            return state

        @chat.user_input
        async def user_input(state: MyChatState) -> MyChatState:
            return state

        @chat.system_response
        async def system_response(state: MyChatState) -> MyChatState:
            return state

        chat.add_node(generate_response, "generate_response")
        chat.add_node(user_input, "user_input", trigger_type="SUFFICIENT")
        chat.add_node(system_response, "system_response")

        chat.add_edge(START_NAME, "user_input")
        chat.add_edge("user_input", "generate_response")
        chat.add_edge("generate_response", "system_response")
        chat.add_edge("system_response", "user_input")

        chat.compile()
        task = asyncio.create_task(chat.stream({"messages": []}))

        while True:
            user_message = input("> ")
            await chat.set_user_input(user_message)
            response_msg = await chat.get_system_response()
            print("response: " + response_msg)

    asyncio.run(main())
