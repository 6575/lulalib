from typing import cast, Any
import msgpack

from lulalib.abc import ITypeAdapter


class MSPDictType(ITypeAdapter[dict[str, Any]]):
    """
    MessagePack seralization
    """

    def deserialize(self, data: bytes) -> dict[str, Any]:
        return cast(dict[str, Any], msgpack.unpackb(data, raw=False))
    
    def serialize(self, data: dict[str, Any]) -> bytes:
        return cast(bytes, msgpack.packb(data, use_bin_type=True))
