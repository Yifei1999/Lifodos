import asyncio
import networkx as nx
from enum import Enum, unique
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

from logger import mylogger
try:
    from .state import State, merge
    from .task import START, END
except ImportError as e:
    from state import State, merge
    from task import START, END, START_NAME, END_NAME


@unique
class TaskStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    FINISHED = "FINISHED"


class TaskGraph(nx.DiGraph):
    def __init__(self, state_schema: Type[Any] = State):
        super().__init__()

        self.state_schema = state_schema

        # task name - function call map
        # task name - recent result map
        # task name - running task map
        self._task_register_func_call = {}
        self._task_result_state = {}
        self._task_run_instance = {}

        self.add_node(START, START_NAME)
        self.add_node(END, END_NAME)

    def print_instance_state(self):
        all_node_view = super().nodes()
        format_map = {
            TaskStatus.FINISHED: "32",
            TaskStatus.RUNNING: "33",
            TaskStatus.WAITING: "33",
            TaskStatus.PENDING: "37"
        }
        print("current task status:")

        for task_id in self._task_register_func_call:
            status = all_node_view[task_id]["status"]

            print(task_id + " " * (40 - len(task_id)), end="")
            print(f'\033[{format_map[status]}m' +  status.name + '\033[0m')

    def validate(self, input_state):
        type_adapter = TypeAdapter(self.state_schema)
        user = type_adapter.validate_python(input_state)
        return user

    def register(self, func: Callable):
        async def register_wrapper(*args, **kwargs):
            start_timestamp = datetime.now()
            start_timestamp_str = start_timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
            mylogger.info(f"task '{func.__name__}' has been activated.")

            kwargs = self.validate(*args, **kwargs)

            main_task = asyncio.create_task(func(kwargs))
            sleep_task = asyncio.create_task(asyncio.sleep(10))
            done, running = await asyncio.wait(
                fs=[main_task, sleep_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            if not main_task.done():
                raise Exception("task timeout error!")
            else:
                result = main_task.result()

            # result = await func(kwargs)
            result = self.validate(result)

            end_timestamp = datetime.now()
            end_timestamp_str = start_timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
            sec = (end_timestamp - start_timestamp).seconds
            mylogger.info(f"task '{func.__name__}' has been finished, elapsed consume time {sec}s.")

            return result
        return register_wrapper

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

        assert task_name not in self._task_register_func_call, f"task name {task_name} has been registered"
        super().add_node(task_name, trigger_type = trigger_type, **kwargs)

        # register the task function with task name
        self._task_register_func_call[task_name] = func

    def add_edge(self, task_name_u: str, task_name_v: str, **kwargs):
        super().add_edge(task_name_u, task_name_v, **kwargs)

    def compile(self):
        """
        Task status:
         - `PENDING`: the task is waiting to be activated once condition is satisfied.
         - `RUNNING`: the task has been activated and not finished currently.
         - `FINISHED`: the task has finished and waiting other task to be finished.

        :return:
        """
        nodes_view = super().nodes()
        for node in nodes_view:
            nodes_view[node]["status"] = TaskStatus.PENDING

    def run_task(self):
        pass

    def clear(self):
        # clear the status and prepare to restart the graph
        pass

    async def stream(self, initial_state: dict = None, verbose = False):
        initial_state = self.validate(initial_state)

        all_edge_view = super().edges()
        all_node_view = super().nodes()

        # fetch task, gather and merge the results
        initial_state = initial_state or {}
        start_task_function_call = self._task_register_func_call[START_NAME]
        start_task = asyncio.create_task(start_task_function_call(initial_state))
        self._task_run_instance[START_NAME] = start_task
        mylogger.info("task graph has been started at the START node")

        run_task_names_ls = [START_NAME]

        while len(run_task_names_ls) > 0:
            # 1. activate the task, waiting any one of the task to finish
            for task_id in run_task_names_ls:
                all_node_view[task_id]["status"] = TaskStatus.RUNNING

            # print the task pool status
            if verbose:
                run_task_id = [each for each in run_task_names_ls]
                if END_NAME not in run_task_id and START_NAME not in run_task_id:
                    self.print_instance_state()

            done, running = await asyncio.wait(
                fs=[self._task_run_instance[task_name] for task_name in run_task_names_ls],
                return_when=asyncio.FIRST_COMPLETED
            )

            # traverse and find the index of the finished task
            index = None
            for i, task_id in enumerate(run_task_names_ls):
                 if self._task_run_instance[task_id].done():
                     if index is None:
                         index = i
                     else:
                         raise Exception("multiple finished task")

            # 2. task finished, record the result and status
            # record the task result and pop out of the running list
            finished_task_id = run_task_names_ls[index]
            finished_task_instance = next(iter(done))
            finished_task_result = finished_task_instance.result() or {}
            finished_task_node_attr = all_node_view[finished_task_id]
            finished_task_status = finished_task_node_attr["status"]

            # record result
            self._task_result_state[finished_task_id] = finished_task_result
            if all_node_view[finished_task_id]["status"] != TaskStatus.RUNNING:
                run_task_names_ls.pop(index)
                raise Exception("")
                # continue
            if all_node_view[finished_task_id]["status"] == TaskStatus.RUNNING:
                all_node_view[finished_task_id]["status"] = TaskStatus.WAITING
                run_task_names_ls.pop(index)

            # check the if reached an end task
            if finished_task_id == END_NAME:
                mylogger.info("task graph has been finished at the END node")
                break

            # 3. fetch new task, gather and merge the results
            new_task_name_ls = []
            finished_task_out_edges = super().out_edges(finished_task_id, data=True)

            for finished_task_out_edge in finished_task_out_edges:
                _, prepare_active_task_id, _ = finished_task_out_edge

                # 3.0 check if `node_name` is disabled by the defined prorogation setting
                if ("prop_disables" in finished_task_result) and (prepare_active_task_id in finished_task_result["prop_disables"]):
                    continue

                prepare_active_node_attr = all_node_view[prepare_active_task_id]
                trigger_type = prepare_active_node_attr["trigger_type"]

                # 3.1 check the active mode
                if prepare_active_node_attr["status"] is TaskStatus.PENDING:
                    prepare_task_in_edges = super().in_edges(prepare_active_task_id, data=True)

                    # collect the results of the precursor nodes
                    collected_status = []
                    if trigger_type == "NECESSARY":
                        activate_flag = True
                        # check if all the precursor task are finished
                        for edge in prepare_task_in_edges:
                            pre_requirement_id, _, pre_requirement_link_attr = edge
                            pre_requirement_node_attr = all_node_view[pre_requirement_id]
                            if pre_requirement_node_attr["status"] != TaskStatus.WAITING:
                                activate_flag = False
                                break
                            else:
                                collected_status.append(self._task_result_state[pre_requirement_id])
                    else:
                        activate_flag = False
                        # check if one of the precursor task is finished
                        for edge in prepare_task_in_edges:
                            pre_requirement_id, _, pre_requirement_link_attr = edge
                            pre_requirement_node_attr = all_node_view[pre_requirement_id]
                            if pre_requirement_node_attr["status"] == TaskStatus.WAITING:
                                activate_flag = True
                                collected_status.append(self._task_result_state[pre_requirement_id])
                                break

                    # 3.2 (if task is ready to be active) add new task to the task pool, stop the pre-requirement tasks
                    if activate_flag:
                        start_task_function_call = self._task_register_func_call[prepare_active_task_id]

                        # merge state result
                        if len(collected_status) == 1:
                            input_state = collected_status[0]
                        else:
                            input_state = collected_status[0]
                            for i in range(len(collected_status) - 1):
                                input_state = merge(input_state, collected_status[i + 1])

                        # execute new task
                        input_state_cp = input_state.copy()
                        start_task = asyncio.create_task(start_task_function_call(input_state_cp))
                        new_task_name_ls += [prepare_active_task_id]
                        self._task_run_instance[prepare_active_task_id] = start_task

                        # stop the unfinished pre-requirement tasks
                        prepare_task_in_edges = super().in_edges(prepare_active_task_id, data=True)
                        for edge in prepare_task_in_edges:
                            pre_requirement_id, _, pre_requirement_link_attr = edge
                            pre_requirement_node_attr = all_node_view[pre_requirement_id]
                            pre_requirement_node_status = pre_requirement_node_attr["status"]

                            if pre_requirement_id != finished_task_id:
                                if pre_requirement_node_status == TaskStatus.WAITING:
                                    pre_requirement_node_attr["status"] = TaskStatus.PENDING

                                if pre_requirement_node_status == TaskStatus.RUNNING:
                                    run_task_names_ls.remove(pre_requirement_id)
                                    pre_requirement_node_attr["status"] = TaskStatus.PENDING
                                    self._task_run_instance[pre_requirement_id].cancel()

            finished_task_node_attr["status"] = TaskStatus.FINISHED
            run_task_names_ls += new_task_name_ls

        result_state = self.validate(self._task_result_state[END_NAME])
        return result_state


if __name__ == "__main__":
    pass