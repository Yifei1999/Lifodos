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

from prompt_toolkit.key_binding.bindings.named_commands import clear_screen

from logger import mylogger
try:
    from .state import State, merge
except ImportError as e:
    from state import State, merge


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
        self._registered_task = {
            "START": START,
            "END": END
        }
        self._result_status = {}
        self.add_node(START, "START")
        self.add_node(END, "END")

    def print_instance_state(self):
        all_node_view = super().nodes()
        format_map = {
            "FINISHED": "32",
            "RUNNING": "33",
            "PENDING": "37"
        }

        print("current task status:")

        for task_id in self._registered_task:
            status = all_node_view[task_id]["status"]

            print(task_id + " " * (40 - len(task_id)), end="")
            print(f'\033[{format_map[status]}m' +  status + '\033[0m')


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
        self._registered_task[task_name] = func

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
        task_function_call = self._registered_task["START"]
        start_task = asyncio.create_task(task_function_call(initial_state))
        mylogger.info("task graph has been started at the START node")

        run_task_list = [("START", start_task)]
        finish_flag = False

        while len(run_task_list) > 0:
            # activate the task, waiting any one of the task to finish
            for each in run_task_list:
                task_id = each[0]
                all_node_view[task_id]["status"] = "RUNNING"


            # run_task_name = [each[0] for each in run_task_list]
            # if "END" not in run_task_name and "START" not in run_task_name:
            #     self.print_instance_state()

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
            # record the task result and pop out of the running list
            task_name = run_task_list[index][0]
            task = next(iter(done))
            task_result = task.result() or {}

            # record result
            self._result_status[task_name] = task_result
            all_node_view[task_name]["status"] = "FINISHED"
            run_task_list.pop(index)

            if task_name == "END":
                finish_flag = True
                break

            # check the end task condition
            if finish_flag:
                # reach the end of the task graph
                mylogger.info("task graph has been finished at the END node")
                break

            # fetch new task, gather and merge the results
            new_task_list = []
            task_out_edge = super().out_edges(task_name, data=True)
            successor_name_list = [each[1] for each in task_out_edge]

            for node_name in successor_name_list:
                if ("downstream_disables" in task_result) and (node_name in task_result["downstream_disables"]):
                    continue

                node_attr = all_node_view[node_name]
                trigger_type = node_attr["trigger_type"]

                if node_attr["status"] in ("PENDING", "FINISHED"):
                    task_in_edge = super().in_edges(node_name, data=True)

                    # collect the results of the precursor nodes
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
                                collected_status.append(self._result_status[precursor_name])
                    else:
                        activate_flag = False
                        # check if one of the precursor task is finished
                        for edge in task_in_edge:
                            precursor_name, _, attr_dict = edge
                            precursor_attr = all_node_view[precursor_name]
                            if precursor_attr["status"] == "FINISHED":
                                activate_flag = True
                                collected_status.append(self._result_status[precursor_name])
                                break

                    # add new task to the task pool
                    if activate_flag:
                        task_function_call = self._registered_task[node_name]

                        # merge state result from different edges
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
    await asyncio.sleep(3)


@logging
async def wait2(state: State):
    await asyncio.sleep(6)



if __name__ == "__main__":
    graph = TaskGraph(State)
    graph.add_node(wait1, "wait1", trigger_type="SUFFICIENT")
    graph.add_node(wait2, "wait2", trigger_type="SUFFICIENT")

    graph.add_edge("START", "wait1")
    graph.add_edge("wait1", "wait2")
    graph.add_edge("wait2", "END")
    graph.compile()

    async def main():
        await graph.stream()

    asyncio.run(main())

