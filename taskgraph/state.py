from typing_extensions import TypedDict
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


class State(TypedDict, total=False):
    """
    define the state metadata

    these variables are pre-defined:
     - `paras`: it is not encouraged to pass a lot of parameters that only use once, put them in 'paras' instead.
    """
    paras: Optional[Any]


def merge(state1: State, state2: State) -> State:
    """
    define status merging criteria
    :param state1: returned state of task 1
    :param state2: returned state of task 2
    :return: merged status

    merging rule:
     - `paras`: update the `paras` from task 1 using `paras` from task 2
     - others: 

    """
    # hints = get_type_hints(State, include_extras=True)
    # name_annotation = hints.get("messages")
    # if isinstance(name_annotation, tuple) and len(name_annotation) == 2:
    #     message_process_func = name_annotation[1]
    # else:
    #     message_process_func = None

    state1 = state1 or {}
    state2 = state2 or {}
    # get all keys
    keys = set(state1.keys()) | set(state2.keys())

    new_state = {}
    for key in keys:
        # define unique merging strategy
        if key == "paras":
            new_state[key] = state1.get(key, {}).update(state2.get(key, {}))
            break

        new_state[key] = state1.get(key, None) or state2.get(key, None)
    return new_state


if __name__ == "__main__":
    merge({}, {})

