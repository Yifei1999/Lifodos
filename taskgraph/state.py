from openpyxl.styles.builtins import total
from typing_extensions import TypedDict
from typing import get_type_hints
from typing import (
    Any,
    Callable,
    Literal,
    Iterable,
    NamedTuple,
    Optional,
    Sequence,
    Type,
    Union, Annotated,
)

class StatusConflictError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


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
    state1 = state1 or {}
    state2 = state2 or {}
    new_state = {}
    for key in state1:
        if key == "downstream_disables":
            new_state[key] = state1[key] + state2[key]
        if key == "paras":
            new_state[key] = state1[key].update(state2[key])

        new_state[key] = state1[key] or state2[key]

    return new_state


if __name__ == "__main__":
    pass

