from abc import ABC, abstractmethod
from typing import Generic, Literal, TypeVar, overload, final

_VT = TypeVar("_VT")
_KT = TypeVar("_KT")


class IStorage(ABC, Generic[_KT, _VT]):

    @overload
    async def get(self, k: _KT, *, strict: Literal[False], **kwargs) -> _VT | None:
        raise NotImplementedError()
    
    @overload
    async def get(self, k: _KT, *, strict: Literal[True], **kwargs) -> _VT:
        raise NotImplementedError()

    @overload
    async def get(self, k: _KT, **kwargs) -> _VT | None:
        raise NotImplementedError()

    @final
    async def get(self, k: _KT, *, strict: bool = False, **kwargs) -> _VT | None:
        return await self._get(k, strict=strict, **kwargs)

    @abstractmethod
    async def _get(self, k: _KT, *, strict: bool = False, **kwargs) -> _VT | None:
        raise NotImplementedError()

    @abstractmethod
    async def set(self, k: _KT, v: _VT, **kwargs) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, k: _KT, **kwargs) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def contains(self, k: _KT, **kwargs) -> bool:
        raise NotImplementedError()
