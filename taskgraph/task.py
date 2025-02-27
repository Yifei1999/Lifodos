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

