from typing import Callable, TypeVar, Any
from uuid import UUID
import asyncio
import concurrent.futures as futures
import logging

RT = TypeVar("RT")
T_FUT_C_T = TypeVar("T_FUT_C_T", bound=Callable[[futures.Future], Any])


def executor(fn: Callable[..., RT],
             fn_args: tuple,
             fn_kwargs: dict,
             callbacks: list[T_FUT_C_T],
             backend: futures.ThreadPoolExecutor | futures.ProcessPoolExecutor
             ) -> asyncio.Future[RT]:
    """
    Execute in threadpool
    """
    loop = asyncio.get_running_loop()
    t_fut = backend.submit(fn, *fn_args, **fn_kwargs)
    #a_fut: asyncio.Future[RT] = loop.create_future()
    a_fut = asyncio.wrap_future(t_fut, loop=loop)

    for callback in callbacks:
        t_fut.add_done_callback(callback)

    return a_fut

