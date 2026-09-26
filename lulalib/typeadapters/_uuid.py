import typing
import uuid
import struct

import lulalib.abc

class UUIDType(lulalib.abc.ITypeAdapter[uuid.UUID]):
    
    def serialize(self, data: uuid.UUID) -> bytes:
        return struct.pack(">QQ", int(data) & ((1 << 64) - 1), int(data) >> 64)

    def deserialize(self, data: bytes) -> uuid.UUID:
        low, high = typing.cast(tuple[int, int], struct.unpack(">QQ", data))
        return uuid.UUID(int=(high << 64) | low)

