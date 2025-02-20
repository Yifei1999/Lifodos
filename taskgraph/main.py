import networkx as nx
from typing import Annotated
from typing_extensions import TypedDict
import asyncio
from typing import (
    Any,
    Callable,
    Literal,
    NamedTuple,
    Optional,
    Sequence,
    Type,
    Union,
    cast,
    get_args,
    get_origin,
    get_type_hints,
    overload,
)


def define_task(para=None):
    def decorator(func: Callable):
        name = func.__name__

        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            return name, result
        return wrapper
    return decorator


class State(TypedDict):
    pass


@define_task()
async def START(state: State):
    pass


@define_task()
async def END(state: State):
    pass


START_NAME = "START"
END_NAME = "END"



class TaskGraph(nx.DiGraph):
    def __init__(self, state_schema: Type[Any]):
        super().__init__()

        # dict: task name -> task function call
        self.registered_task = {
            "START": START,
            "END": END
        }
        self.add_node("START")
        self.add_node("END")

    def add_node(self, task_name: str, **kwargs):

        super().add_node(task_name)

        # register the task name
        # function_name = func.__name__
        self.registered_task[task_name] = globals()[task_name]

    def add_edge(self, task_name_u: str, task_name_v: str, **kwargs):
        super().add_edge(task_name_u, task_name_v, **kwargs)

    def compile(self):
        nodes_view = super().nodes()
        for node in nodes_view:
            nodes_view[node]["status"] = "PENDING"

    def run_task(self):
        pass

    async def stream(self, initial_state: dict = None, verbose = False):
        all_edge_view = super().edges()
        all_node_view = super().nodes()

        # fetch task, gather and merge the results
        initial_state = State()
        task_function_call = self.registered_task["START"]

        start_task = asyncio.create_task(task_function_call(initial_state))
        print("task graph has been started at the START node")

        run_task_list = [start_task]
        new_task_id_list = ["START"]
        finish_flag = False

        while len(run_task_list) > 0:
            # await task completion
            for task_id in new_task_id_list:
                all_node_view[task_id]["status"] = "RUNNING"

            done, running = await asyncio.wait(fs=run_task_list, return_when=asyncio.FIRST_COMPLETED)

            # task finish, update result and status
            for task in done:
                task_name, task_result = task.result()
                all_node_view[task_name]["status"] = "FINISHED"
                print(f"task {task_name} has been finished!")

                if task_name == "END":
                    finish_flag = True
                    break

            if finish_flag:
                print("task graph has been finished at the END node")
                break

            # fetch task, gather and merge the results
            new_task_list = []
            new_task_id_list = []
            for node in all_node_view:
                node_attr = all_node_view[node]

                if node_attr["status"] == "PENDING":
                    task_in_edge = super().in_edges(node, data=True)

                    activate_flag = True
                    for edge in task_in_edge:
                        precursor_name, _, attr_dict = edge
                        precursor_attr = all_node_view[precursor_name]
                        if precursor_attr["status"] != "FINISHED":
                            activate_flag = False
                            break


                    # add new task to the task pool
                    if activate_flag:
                        task_function_call = self.registered_task[node]

                        # merge state result from different edges
                        # 这里需要确定是否被执行
                        print(f"task {node} has been started...")

                        initial_state = State()
                        start_task = asyncio.create_task(task_function_call(initial_state))

                        new_task_list += [start_task]
                        new_task_id_list += [node]

            run_task_list = list(running) + new_task_list



    def invoke(self):
        pass


@define_task()
async def wait1(state: State):
    await asyncio.sleep(2)


@define_task()
async def wait2(state: State):
    await asyncio.sleep(3)


graph = TaskGraph(State)
graph.add_node("wait1")
graph.add_node("wait2")
graph.add_edge("START", "wait1")
graph.add_edge("wait1", "wait2")
graph.add_edge("wait2", "END")
graph.compile()


async def main():
    await graph.stream()

asyncio.run(main())