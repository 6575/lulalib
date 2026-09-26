from __future__ import annotations
from typing import TYPE_CHECKING, Any, TypeVar, cast

import uuid
import struct
import asyncio
import threading
import weakref
import functools

from lulalib.exc import TaskAlreadyDoneError
from lulalib.core import LulalibConfig
from lulalib.enums import TaskResultState
if TYPE_CHECKING:
    from _collections_abc import Buffer
    from lulalib.storage import SchedulerLMDBStorage
    from lulalib.models.taskresult import TaskResult


T = TypeVar("T")


class TaskResultObserver:

    __slots__ = ("_stor", "_conf", "_t", "_lock", "_cache")

    _stor: SchedulerLMDBStorage | None
    _conf: LulalibConfig | None

    def __init__(self, t: type[TaskResult]):
        self._t = t
        self._stor = None
        self._conf = None
        self._lock = threading.Lock()
        self._cache: dict[uuid.UUID, TaskResult] = {}

    @property
    def storage(self) -> SchedulerLMDBStorage:
        if not self._stor:
            raise AttributeError()
        return self._stor

    @storage.setter
    def storage(self, value: SchedulerLMDBStorage):
        if self._stor:
            raise AttributeError()
        self._stor = value

    @property
    def conf(self) -> LulalibConfig:
        if not self._conf:
            raise AttributeError()
        return self._conf

    @conf.setter
    def conf(self, value: LulalibConfig):
        if not isinstance(value, LulalibConfig):
            raise TypeError()
        if self._conf:
            raise AttributeError()
        self._conf = value

    async def update_task_state(self, result: TaskResult[Any]):
        await self.storage.set(result.task_id, result)
        # TODO: subscriptions for RPC
        result.notify()

    def set_state(self, result: TaskResult):
        asyncio.get_running_loop().create_task(self.update_task_state(result))

    async def update_task_result(self, result: TaskResult):
        await self.storage.set(result.task_id, result)
        result.notify()

    def set_result(self, result: TaskResult):
        asyncio.get_running_loop().create_task(self.update_task_result(result))

    def _finalize_result_callback(
            self,
            fut: asyncio.Future[Any], *,
            taskresult: TaskResult[Any]
        ):
        exc = fut.exception()
        if isinstance(exc, BaseException):
            taskresult.state = TaskResultState.ERROR
            return
        result = fut.result()
        taskresult.result = result

    def set_callback(self, fut: asyncio.Future[Any], result: TaskResult[Any]):
        fut.add_done_callback(
            functools.partial(self._finalize_result_callback, taskresult=result)
        )

    def get_task_result(self, task_id: uuid.UUID,
                        exp_at: float, _typ_ad: int
        ) -> TaskResult[Any]:
        with self._lock:
            o = self._cache.get(task_id)
        if o:
            return o
        o = self._t(observer=self, task_id=task_id, exp_at=exp_at, _typ_ad=_typ_ad,)
        with self._lock:
            self._cache[task_id] = o
        return o
    
    def task_result_from_buffer(self, buf: Buffer) -> TaskResult[Any]:
        def _check(o: TaskResult, _in: bool):
            if o.state == TaskResultState.DONE and _in:
                    with self._lock:
                        del self._cache[o.task_id]
        l, h = cast(tuple[int , int], struct.unpack_from(">QQ", buf))
        k = uuid.UUID(int=(h << 64) | l)
        with self._lock:
            o = self._cache.get(k)
        if o:
            _check(o, True)
            return o
        o = self._t.from_buffer(self, buf)
        _check(o, False)
        with self._lock:
            self._cache[k] = o
        return o


    