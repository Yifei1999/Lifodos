import asyncio
from state import State
from graph import TaskGraph
from task import logging, START, END


class MyState(State):
    pass


@logging
async def demo_task_wait1(state: State):
    await asyncio.sleep(3)


@logging
async def demo_task_wait2(state: State):
    await asyncio.sleep(6)

@logging
async def demo_task_wait3(state: State):
    await asyncio.sleep(6)





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
        await graph.stream()

    asyncio.run(main())