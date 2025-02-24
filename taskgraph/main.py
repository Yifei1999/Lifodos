import networkx as nx
from typing import Annotated
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
    Annotated
)

from logger import mylogger
try:
    from .state import State, merge
except ImportError as e:
    from state import State, merge

# TODO: optional activate of a new node when its precursor is finished
# TODO: overtime execution of a task node
# TODO: support annotated field feature in `status`
# TODO： support flexible tasks function return value, eg: field missing

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
        self.result_status = {}
        self.add_node(START, "START")
        self.add_node(END, "END")

    def add_node(self, func: Callable, task_name: str = None, trigger_type = "NECESSARY", **kwargs):
        """
        add an new task node to the graph

        :param func: the function call of the task.
        :param task_name:
        :param trigger_type: define when to activate the task, can be following values:
           - 'NECESSARY': all the precursor must be finished until the task is activated (default setting).
           - 'SUFFICIENT': once one of the precursor is finished, the task will be activated.
       :param kwargs: user defined task attributes.

       :return:
       """
        super().add_node(task_name, trigger_type = trigger_type, **kwargs)

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
        initial_state = initial_state or {}
        task_function_call = self.registered_task["START"]
        start_task = asyncio.create_task(task_function_call(initial_state))
        mylogger.info("task graph has been started at the START node")

        run_task_list = [("START", start_task)]
        finish_flag = False

        while len(run_task_list) > 0:
            # activate the task, waiting any one of the task to finish
            for each in run_task_list:
                task_id = each[0]
                all_node_view[task_id]["status"] = "RUNNING"

            done, running = await asyncio.wait(
                fs=[name_task_pair[1] for name_task_pair in run_task_list],
                return_when=asyncio.FIRST_COMPLETED
            )

            # traverse and find the index of the finished task
            index = None
            for i, name_task_pair in enumerate(run_task_list):
                 if name_task_pair[1].done():
                     if index is None:
                         index = i
                     else:
                         raise Exception("multiple finished task")

            # task finished, update result and status
            for task in done:
                task_name = run_task_list[index][0]
                task_result = task.result()

                # record the task result and pop out of the running list
                self.result_status[task_name] = task_result
                all_node_view[task_name]["status"] = "FINISHED"
                run_task_list.pop(index)

                if task_name == "END":
                    finish_flag = True
                    break

            # check the end task condition
            if finish_flag:
                mylogger.info("task graph has been finished at the END node")
                break

            # fetch new task, gather and merge the results
            new_task_list = []
            for node_name in all_node_view:
                node_attr = all_node_view[node_name]
                trigger_type = node_attr["trigger_type"]

                if node_attr["status"] == "PENDING":
                    task_in_edge = super().in_edges(node_name, data=True)

                    collected_status = []
                    if trigger_type == "NECESSARY":
                        activate_flag = True
                        # check if all the precursor task are finished
                        for edge in task_in_edge:
                            precursor_name, _, attr_dict = edge
                            precursor_attr = all_node_view[precursor_name]
                            if precursor_attr["status"] != "FINISHED":
                                activate_flag = False
                                break
                            else:
                                collected_status.append(self.result_status[precursor_name])
                    else:
                        activate_flag = False
                        # check if one of the precursor task is finished
                        for edge in task_in_edge:
                            precursor_name, _, attr_dict = edge
                            precursor_attr = all_node_view[precursor_name]
                            if precursor_attr["status"] == "FINISHED":
                                activate_flag = True
                                collected_status.append(self.result_status[precursor_name])
                                break

                    # add new task to the task pool
                    if activate_flag:
                        task_function_call = self.registered_task[node_name]

                        # merge state result from different edges
                        # TODO: 这里需要确定是否被执行
                        if len(collected_status) == 1:
                            input_state = collected_status[0]
                        else:
                            input_state = collected_status[0]
                            for i in range(len(collected_status) - 1):
                                input_state = merge(input_state, collected_status[i + 1])

                        input_state = State()
                        start_task = asyncio.create_task(task_function_call(input_state))

                        new_task_list += [(node_name, start_task)]

            run_task_list += new_task_list

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
    graph.add_node(wait1, "wait11", trigger_type="SUFFICIENT")
    graph.add_node(wait2, "wait22", trigger_type="SUFFICIENT")
    graph.add_node(wait2, "wait33", trigger_type="SUFFICIENT")
    graph.add_edge("START", "wait11")
    graph.add_edge("START", "wait22")

    graph.add_edge("wait11", "wait33")
    graph.add_edge("wait22", "wait33")

    graph.add_edge("wait33", "END")
    graph.compile()


    async def main():
        await graph.stream()

    asyncio.run(main())

