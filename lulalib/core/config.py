from __future__ import annotations
from typing import TYPE_CHECKING
from uuid import UUID
from asyncio import Event
from contextvars import ContextVar

from lulalib.core.hashes import hash_fnv1a_64
if TYPE_CHECKING:
    from lulalib.abc import ITypeAdapter


class LulalibConfig:

    __slots__ = ("__type_adapters", "__oid_namespace", "__ctx_oid", "__ctx_auth", "__shutdown")
    _oid_namespace: UUID | None
    __ctx_oid: ContextVar[UUID] | None
    __ctx_auth: ContextVar[UUID] | None
    __shutdown: Event | None

    @staticmethod
    def get_typ_key(name: str | bytes | int) -> int:
        if isinstance(name, int):
            return name
        if isinstance(name, bytes):
            return hash_fnv1a_64(name)
        if isinstance(name, str):
            return hash_fnv1a_64(name.encode("utf-8"))
        raise TypeError

    def __init__(self):
        self.__type_adapters = dict[int, "ITypeAdapter"]()
        self.__oid_namespace = None
        self.__ctx_oid = None
        self.__ctx_auth = None

    def set_type_adapter(self, name: str | bytes | int, ad: ITypeAdapter) -> None:
        self.__type_adapters[self.get_typ_key(name)] = ad

    def get_type_adapter(self, name: str | bytes | int) -> ITypeAdapter:
        return self.__type_adapters[self.get_typ_key(name)]

    @property
    def oid_namespace(self) -> UUID:
        if not isinstance(self.__oid_namespace, UUID):
            raise AttributeError("OID namespace unset")
        return self.__oid_namespace

    @oid_namespace.setter
    def oid_namespace(self, value: UUID) -> None:
        self.__oid_namespace = value

    @property
    def ctx_oid(self) -> ContextVar[UUID]:
        if not isinstance(self.__ctx_oid, ContextVar):
            raise AttributeError("OID context unset")
        return self.__ctx_oid

    @ctx_oid.setter
    def ctx_oid(self, value: ContextVar[UUID]):
        self.__ctx_oid = value

    @property
    def ctx_auth(self) -> ContextVar[UUID]:
        if not isinstance(self.__ctx_auth, ContextVar):
            raise AttributeError("auth context unset")
        return self.__ctx_auth

    @ctx_auth.setter
    def ctx_auth(self, value: ContextVar[UUID]):
        self.__ctx_auth = value

    @property
    def shutdown(self) -> Event:
        if not isinstance(self.__shutdown, Event):
            raise AttributeError("auth context unset")
        return self.__shutdown

    @shutdown.setter
    def shutdown(self, value: Event):
        self.__shutdown = value
