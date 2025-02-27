import asyncio
from state import State
from graph import TaskGraph
from task import logging, START, END


# define the `state` in the graph, inherited the `State` class
class MyState(State):
    age: int


# define task function
@logging
async def demo_task_wait1(state: MyState):
    await asyncio.sleep(3)
    return state


@logging
async def demo_task_wait2(state: MyState):
    await asyncio.sleep(6)
    return state


@logging
async def demo_task_wait3(state: MyState):
    await asyncio.sleep(2)
    return state


if __name__ == "__main__":
    graph = TaskGraph(MyState)
    graph.add_node(demo_task_wait1, "demo_task_wait1")
    graph.add_node(demo_task_wait2, "demo_task_wait2")
    graph.add_node(demo_task_wait3, "demo_task_wait3")

    graph.add_edge("START", "demo_task_wait1")
    graph.add_edge("START", "demo_task_wait2")
    graph.add_edge("demo_task_wait1", "demo_task_wait3")
    graph.add_edge("demo_task_wait2", "demo_task_wait3")
    graph.add_edge("demo_task_wait3", "END")

    graph.compile()

    async def main():
        result = await graph.stream({"name": "lyf"})
        print(result)

    asyncio.run(main())


