from __future__ import annotations
from typing import (
    TYPE_CHECKING,
    Generator,
    Awaitable,
    SupportsBytes,
    Hashable,
    TypeVar,
    Generic,
    cast,
    Any
)
from _collections_abc import Buffer
import uuid
import threading
import struct
import asyncio
import logging
from dataclasses import dataclass, field

from lulalib.exc import TaskAlreadyDoneError, TaskResultRetException
from lulalib.abc import ITypeAdapter
from lulalib.enums import TaskResultState
if TYPE_CHECKING:
    from lulalib.observers.taskresultobserver import TaskResultObserver

T = TypeVar("T")
TASK_RESULT_HDR = ">QQQIdb"
TASK_RESULT_SZ = struct.calcsize(TASK_RESULT_HDR)

g_lock = threading.Lock()

def callback(fut: asyncio.Future):
    print("Callback: ", fut.result())

@dataclass(slots=True, repr=False)
class TaskResult(SupportsBytes, Generic[T], Awaitable[T]):
    observer:   TaskResultObserver
    task_id:    uuid.UUID
    exp_at:     float
    _typ_ad:    int
    _state:     int = field(default=TaskResultState.NULL)
    data_size:  int = field(default=0)
    _result:    bytes = field(default=b"")
    _waiters:   list[asyncio.Future[T]] = field(default_factory=list)

    @classmethod
    def from_buffer(cls, observer: TaskResultObserver, buf: Buffer):
        print("[FROM BUFFER]")
        tidl, tidh, _typ_ad, dsz, exp, st = cast(
            tuple[int, int, int, int, float, int],
            struct.unpack_from(TASK_RESULT_HDR, buf, 0))
        result=memoryview(buf)[TASK_RESULT_SZ:].tobytes()
        return cls(
            observer=observer,
            task_id=uuid.UUID(int=(tidh << 64) | tidl),
            _typ_ad=_typ_ad,
            data_size=dsz,
            exp_at=exp,
            _state=st,
            _result=result
        )

    def __repr__(self) -> str:
        return f"<TaskResult id={str(self.task_id)} state={self.state}>"

    def __bytes__(self) -> bytes:
        return self.hdr + self._result

    def __await__(self) -> Generator[Any, None, T]:
        fut: asyncio.Future[T] = asyncio.get_event_loop().create_future()
        fut.add_done_callback(callback)
        if self._state == TaskResultState.REPEATED:
            fut.set_exception(TaskAlreadyDoneError(result=self, task_id=self.task_id))
        elif self._state == TaskResultState.ERROR:
            fut.set_exception(TaskResultRetException())
        elif self._state == TaskResultState.DONE:
            fut.set_result(self.result)
        else:
            print("Added fut to the set")
            with g_lock:
                self._waiters.append(fut)
                print("[AWAIT] size:", len(self._waiters))
                print("[AWAIT] ptr:", hex(id(self._waiters)))
        return fut.__await__()

    def notify(self):
        print("notifying")
        i = 0
        for fut in self._waiters:
            i += 1
            asyncio.get_event_loop().call_soon_threadsafe(fut.set_result, self.result)
        print(f"[NOTIFY]Done {i} notifications")
        print("[NOTIFY] ptr:", hex(id(self._waiters)))
        print(len(self._waiters))
        self._waiters.clear()

    @property
    def id(self) -> bytes:
        return struct.pack(
            ">QQ",
            int(self.task_id) & ((1 << 64) - 1),
            int(self.task_id) >> 64
        )

    @property
    def hdr(self) -> bytes:
        return struct.pack(
            TASK_RESULT_HDR,
            int(self.task_id) & ((1 << 64) - 1), int(self.task_id) >> 64,
            self._typ_ad,
            self.data_size, self.exp_at, self.state
        )

    @property
    def state(self) -> int:
        return self._state

    @state.setter
    def state(self, value: int):
        if value in (TaskResultState.DONE, TaskResultState.CANCELLED):
            raise ValueError()
        self._state = value
        self.observer.set_state(self)

    @property
    def result(self) -> T:
        """Deserialized result"""
        adapter = cast(ITypeAdapter[T], self.observer.conf.get_type_adapter(self._typ_ad))
        return adapter.deserialize(self._result)

    @result.setter
    def result(self, value: T):
        adapter = cast(ITypeAdapter[T], self.observer.conf.get_type_adapter(self._typ_ad))
        try:
            v = adapter.serialize(value)
        except:
            self._state = TaskResultState.ERROR
            logging.error("Unable to write Task Result")
        else:
            self._state = TaskResultState.DONE
            self._result = v
            self.observer.set_result(self)


        