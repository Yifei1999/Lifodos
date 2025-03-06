import asyncio
from state import State
from graph import TaskGraph
from task import START_NAME, END_NAME

# Warning: Python version should be 3.8+

# 1. Define the transit `state` in the graph, inherited the `State` class
class MyState(State):
    age: int

# 2. Init a TaskGraph instance
graph = TaskGraph(MyState)


# 3. Define task functions. Task functions should be registered by using `@graph.register` decorator
# Requirements of the task functions:
# - The parameter of the function should be of `MyState` type. The arguments should pass the type & field validation.
# - The output of the function should pass the validation as well.
@graph.register
async def demo_task_wait1(state: MyState):
    await asyncio.sleep(3)
    return state


@graph.register
async def demo_task_wait2(state: MyState):
    await asyncio.sleep(6)
    return state


@graph.register
async def demo_task_wait3(state: MyState):
    await asyncio.sleep(2)
    return state


if __name__ == "__main__":
    # 4. Add task node to the graph, binding task name with corresponding task functions
    graph.add_node(demo_task_wait1, "demo_task_wait_1", trigger_type="SUFFICIENT")
    graph.add_node(demo_task_wait2, "demo_task_wait_2")
    graph.add_node(demo_task_wait3, "demo_task_wait_3")

    # 5. Use task name to add the directed edge, establish the task flow
    #  - The name of START node is pre-defined by var `START_NAME`, END node is in the same way
    graph.add_edge(START_NAME, "demo_task_wait_1")
    graph.add_edge("demo_task_wait_1", "demo_task_wait_2")
    graph.add_edge("demo_task_wait_2", "demo_task_wait_3")
    graph.add_edge("demo_task_wait_3", "demo_task_wait_1")


    # 6. Compile the graph and use `graph.stream` to get the results
    graph.compile()
    async def main():
        result = await graph.stream({"age": 1})
        print(result)

    asyncio.run(main())



