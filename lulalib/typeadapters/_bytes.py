import lulalib.abc

class BytesType(lulalib.abc.ITypeAdapter[bytes]):
    """
    Monkey type adapter that actually does no serialization and desealization.

    Given `bytes` input is always returned as is.
    Used as a default placeholder.
    """

    def serialize(self, data: bytes) -> bytes:
        return data
    
    def deserialize(self, data: bytes) -> bytes:
        return data

