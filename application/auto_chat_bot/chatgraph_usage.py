from taskgraph import START_NAME
from taskgraph.chat import ChatState, ChatGraph
from llm import async_request_proxy


class MyChatState(ChatState):
    pass


def create_instance():
    graph = ChatGraph(MyChatState)

    @graph.register
    async def generate_response(state: MyChatState) -> MyChatState:
        message = await async_request_proxy(state["messages"])
        state["messages"] += [{"role": "assistant", "content": message["content"]}]
        return state


    @graph.user_input
    async def user_input(state: MyChatState) -> MyChatState:
        return state


    @graph.system_response
    async def system_response(state: MyChatState) -> MyChatState:
        return state


    graph.add_node(generate_response, "generate_response")
    graph.add_node(user_input, "user_input", trigger_type="SUFFICIENT")
    graph.add_node(system_response, "system_response")

    graph.add_edge(START_NAME, "user_input")
    graph.add_edge("user_input", "generate_response")
    graph.add_edge("generate_response", "system_response")
    graph.add_edge("system_response", "user_input")

    graph.compile()
    return graph