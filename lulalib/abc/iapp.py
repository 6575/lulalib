from abc import ABC, abstractmethod
from typing import TypeVar, Callable as F
from uuid import UUID
from contextvars import ContextVar

from lulalib.abc import ITypeAdapter


T = TypeVar("T")


class IApp(ABC):

    __slots__ = ("_running", "_typ_ad", "_ctx_oid", "_ctx_auth")

    @abstractmethod
    def set_type_adapter(self, name: str | bytes | int, ad: ITypeAdapter) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get_type_adapter(self, name: str | bytes | int) -> ITypeAdapter:
        raise NotImplementedError()

    @abstractmethod
    def set_oid_ctx(self, ctx: ContextVar[UUID]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get_oid_ctx(self) -> ContextVar[UUID]:
        raise NotImplementedError()

    @abstractmethod
    def set_auth_ctx(self, ctx: ContextVar[UUID]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get_auth_ctx(self) -> ContextVar[UUID]:
        raise NotImplementedError()

