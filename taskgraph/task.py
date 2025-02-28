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



START_NAME = "START"
END_NAME = "END"

async def START(state: State) -> State:
    return state


async def END(state: State) -> State:
    return state

