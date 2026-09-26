from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Hashable

import lulalib.core.hashes
from lulalib.abc.istorage import IStorage


VAL_T = TypeVar("VAL_T")

class ITypeAdapter(Hashable, Generic[VAL_T]):

    def __hash__(self) -> int:
        return lulalib.core.hashes.hash_fnv1a_64(self.__class__.__name__.encode())

    @abstractmethod
    def deserialize(self, data: bytes) -> VAL_T:
        raise NotImplementedError()

    @abstractmethod
    def serialize(self, data: VAL_T) -> bytes:
        raise NotImplementedError()

