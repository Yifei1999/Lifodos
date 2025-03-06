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


class ChatGraph(TaskGraph):
    def __init__(self, state_schema: Type[Any] = State):
        super().__init__(state_schema)

        self._user_input_event = asyncio.Event()
        self._user_input_event.clear()
        self._system_response_event = asyncio.Event()
        self._system_response_event.clear()
        self._message_buffer = None

    async def USER_INPUT(self, state: State) -> State:

        await self._user_input_event.wait()

        state["messages"] += [{"role": "user", "content": self._message_buffer}]
        self._user_input_event.clear()
        self._message_buffer = None
        return state

    async def SYSTEM_RESPONSE(self, state: State) -> State:
        self._message_buffer = state["messages"][-1]["content"]

        self._system_response_event.set()
        return state

    async def set_user_input(self, user_input: str):
        self._message_buffer = user_input
        self._user_input_event.set()

    async def get_system_response(self):
        await self._system_response_event.wait()

        message =  self._message_buffer
        self._system_response_event.clear()
        return message

    def save_context(self):
        pass

    def load_context(self):
        pass


def create_instance():
    from .task import START_NAME, END_NAME

    class MyState(State):
        messages: list

    graph = ChatGraph(MyState)

    @graph.register
    async def generate_response(state: MyState):
        state["messages"] += [{"role": "assistant", "content": "hello world!"}]
        return state

    graph.add_node(generate_response, "generate_response")
    graph.add_node(graph.USER_INPUT, "user_input", trigger_type="SUFFICIENT")
    graph.add_node(graph.SYSTEM_RESPONSE, "system_response")

    graph.add_edge(START_NAME, "user_input")
    graph.add_edge("user_input", "generate_response")
    graph.add_edge("generate_response", "system_response")
    graph.add_edge("system_response", "user_input")

    graph.compile()

    return graph


if __name__ == "__main__":
    async def main():
        pass
        # result = await graph.stream({"age": 1})
        # print(result)


    asyncio.run(main())