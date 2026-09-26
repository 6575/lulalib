from __future__ import annotations
from abc import abstractmethod
from typing import SupportsBytes, Awaitable, Generic, TypeVar, TYPE_CHECKING
from _collections_abc import Buffer
import uuid
import asyncio

from lulalib.core import LulalibConfig
if TYPE_CHECKING:
    from lulalib.abc.itaskobserver import ITaskResultObserver


T = TypeVar("T")


class ITaskResult(SupportsBytes, Awaitable[T], Generic[T]):

    __slots__ = (
        "conf", "task_id", "exp_at",
        "_type_ad", "_state", "data_size",
        "_fut", "_result"
    )

    conf:       LulalibConfig
    task_id:    uuid.UUID
    exp_at:     float
    _typ_ad:    int
    _state:     int
    data_size:  int
    _fut:       asyncio.Future[T] | None
    _result:    bytes

    @classmethod
    @abstractmethod
    def from_buffer(cls, observer: ITaskResultObserver, conf: LulalibConfig, buf: Buffer):
        raise NotImplementedError()

    @property
    @abstractmethod
    def hdr(self) -> bytes:
        raise NotImplementedError()

    @property
    @abstractmethod
    def result(self) -> T:
        raise NotImplementedError()

    @result.setter
    @abstractmethod
    def result(self, value: T):
        raise NotImplementedError()

    @property
    @abstractmethod
    def state(self) -> T:
        raise NotImplementedError()

    @state.setter
    @abstractmethod
    def state(self, value: T):
        raise NotImplementedError()


