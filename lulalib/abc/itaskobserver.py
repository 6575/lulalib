from __future__ import annotations
from typing import TYPE_CHECKING, Any, TypeVar

import asyncio

if TYPE_CHECKING:
    from lulalib.abc import IStorage
    from lulalib.models.taskresult import TaskResult


T = TypeVar("T")


class ITaskResultObserver:

    __slots__ = ("_stor", )

    async def update_task_state(self, result: TaskResult):
        raise NotImplementedError()

    def set_state(self, result: TaskResult):
        raise NotImplementedError()

    async def update_task_result(self, result: TaskResult):
        raise NotImplementedError()

    def set_result(self, result: TaskResult):
        raise NotImplementedError()

    def finalize_result_callback(
            self,
            fut: asyncio.Future[Any], *,
            taskresult: TaskResult
        ):
        raise NotImplementedError()
