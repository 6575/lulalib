from typing import TypeVar, Generic

import lulalib.abc


KT = TypeVar("KT")
VT = TypeVar("VT")


class SupportsKVTypeAdapters(Generic[KT, VT]):

    _k_ad: lulalib.abc.ITypeAdapter[KT] | None
    _v_ad: lulalib.abc.ITypeAdapter[VT] | None

    def serialize_key(self, data: KT) -> bytes:
        return self.key_adapter.serialize(data)

    def deserialize_key(self, data: bytes) -> KT:
        return self.key_adapter.deserialize(data)

    def serialize_value(self, data: VT) -> bytes:
        return self.value_adapter.serialize(data)

    def deserialize_value(self, data: bytes) -> VT:
        return self.value_adapter.deserialize(data)

    @property
    def key_adapter(self) -> lulalib.abc.ITypeAdapter[KT]:
        if not self._k_ad:
            raise AttributeError()
        return self._k_ad

    @key_adapter.setter
    def key_adapter(self, value: lulalib.abc.ITypeAdapter[KT]):
        if not isinstance(value, lulalib.abc.ITypeAdapter):
            raise TypeError()
        if self._k_ad:
            raise AttributeError()
        self._k_ad = value
    
    @property
    def value_adapter(self) -> lulalib.abc.ITypeAdapter[VT]:
        if not self._v_ad:
            raise AttributeError()
        return self._v_ad

    @value_adapter.setter
    def value_adapter(self, value: lulalib.abc.ITypeAdapter[VT]):
        if not isinstance(value, lulalib.abc.ITypeAdapter):
            raise TypeError()
        if self._v_ad:
            raise AttributeError()
        self._v_ad = value