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


class State(TypedDict):
    """
        define the state metadata
        it is not encouraged to pass a lot of parameter that only use once in 'paras'
    """
    downstream_disable: Optional[Iterable[str]]


def merge(state1: State, state2: State) -> State:
    """
    define status merging criteria
    :param state1:
    :param state2:
    :return:
    """
    new_state = {}
    for key in state1:
        new_state[key] = state1[key] or state2[key]

    return new_state


if __name__ == "__main__":
    pass

