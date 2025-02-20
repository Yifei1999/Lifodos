import networkx as nx
from typing import Annotated
from typing_extensions import TypedDict
import asyncio
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
)
from logger import mylogger


def logging(func: Callable):
    async def wrapper(*args, **kwargs):
        start_timestamp = datetime.now()
        start_timestamp_str = start_timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
        mylogger.info(f"task '{func.__name__}' has been activated.")

        result = await func(*args, **kwargs)

        end_timestamp = datetime.now()
        end_timestamp_str = start_timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
        sec = (end_timestamp - start_timestamp).seconds
        mylogger.info(f"task '{func.__name__}' has been finished, elapsed consume time {sec}s.")

        return result
    return wrapper


class State(TypedDict):
    pass

async def START(state: State):
    pass

async def END(state: State):
    pass

class TaskGraph(nx.DiGraph):
    def __init__(self, state_schema: Type[Any]):
        super().__init__()

        # dict: task name -> task function call
        self.registered_task = {
            "START": START,
            "END": END
        }
        self.add_node(START, "START")
        self.add_node(END, "END")

    def add_node(self, func: Callable, task_name: str = None, **kwargs):
        super().add_node(task_name)

        # register the task function with task name
        self.registered_task[task_name] = func

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
        mylogger.info("task graph has been started at the START node")

        run_task_list = [start_task]
        run_task_id_list = ["START"]
        finish_flag = False

        while len(run_task_list) > 0:
            # await task completion
            for task_id in run_task_id_list:
                all_node_view[task_id]["status"] = "RUNNING"

            done, running = await asyncio.wait(fs=run_task_list, return_when=asyncio.FIRST_COMPLETED)

            index = None
            for i, each in enumerate(run_task_list):
                 if each.done():
                     index = i

            # task finish, update result and status
            for task in done:
                task_name = run_task_id_list[index]

                task_result = task.result()
                all_node_view[task_name]["status"] = "FINISHED"
                # mylogger.info(f"task {task_name} has been finished!")

                if task_name == "END":
                    finish_flag = True
                    break

            run_task_id_list.pop(index)
            run_task_list.pop(index)

            if finish_flag:
                mylogger.info("task graph has been finished at the END node")
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
                        # mylogger.info(f"task {node} has been started...")

                        initial_state = State()
                        start_task = asyncio.create_task(task_function_call(initial_state))

                        new_task_list += [start_task]
                        new_task_id_list += [node]

            run_task_list = list(running) + new_task_list
            run_task_id_list += new_task_id_list

    def invoke(self):
        pass


@logging
async def wait1(state: State):
    await asyncio.sleep(2)


@logging
async def wait2(state: State):
    await asyncio.sleep(3)



if __name__ == "__main__":
    graph = TaskGraph(State)
    graph.add_node(wait1, "wait11")
    graph.add_node(wait2, "wait22")
    graph.add_edge("START", "wait11")
    graph.add_edge("wait11", "wait22")
    graph.add_edge("wait22", "END")
    graph.compile()


    async def main():
        await graph.stream()

    asyncio.run(main())

