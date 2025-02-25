from openpyxl.styles.builtins import total
from typing_extensions import TypedDict
from typing import get_type_hints
from typing import (
    Any,
    Callable,
    Literal,
    Iterable,
    Optional,
    Sequence,
    Type,
    Union,
    Annotated
)

class StatusConflictError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def add_message():
    pass


class State(TypedDict, total=False):
    """
    define the state metadata

    these variables are pre-defined:
     - `downstream_disable`: the model whose name is in will not be activated when the current task is finished.
     - `paras`: it is not encouraged to pass a lot of parameter that only use once in 'paras'.
    """
    downstream_disables: Optional[Iterable[str]]
    paras: Optional[Any]


def merge(state1: State, state2: State) -> State:
    """
    define status merging criteria
    :param state1:
    :param state2:
    :return:
    """
    # hints = get_type_hints(State, include_extras=True)
    # name_annotation = hints.get("messages")
    # if isinstance(name_annotation, tuple) and len(name_annotation) == 2:
    #     message_process_func = name_annotation[1]
    # else:
    #     message_process_func = None

    state1 = state1 or {}
    state2 = state2 or {}
    keys = set(state1.keys()) | set(state2.keys())

    new_state = {}
    for key in keys:
        if key == "downstream_disables":
            new_state[key] = set(state1.get(key, {})) | (set(state2.get(key, {})))
            break
        if key == "paras":
            new_state[key] = state1.get(key, {}).update(state2.get(key, {}))
            break

        new_state[key] = state1.get(key, None) or state2.get(key, None)
    return new_state


if __name__ == "__main__":
    merge({}, {})

