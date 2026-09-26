from typing import Any, cast
from _collections_abc import Buffer
from time import time
import struct
import uuid

import lulalib.abc
import lulalib.exc
import lulalib.enums
import lulalib.core
import lulalib.traits
import lulalib.models
import lulalib.observers
import lulalib.typeadapters
from lulalib.storage.lmdb import LMDBStorage


class SchedulerLMDBStorage(
    lulalib.abc.IStorage[uuid.UUID, lulalib.models.TaskResult],
    lulalib.traits.SupportsKVTypeAdapters[uuid.UUID, lulalib.models.TaskResult]
):
    """=d"""

    def __init__(self,
                 stor: LMDBStorage,
                 ob: lulalib.observers.TaskResultObserver):
        self._k_ad = None
        self._v_ad = None
        self._stor = stor
        self._ob = ob
        self._ob.storage = self
        self.key_adapter = lulalib.typeadapters.UUIDType()
        self.value_adapter = lulalib.typeadapters.TaskResultType(self._ob)

    @staticmethod
    def _is_expired(buf: Buffer) -> bool:
        return time() > cast(float, struct.unpack_from(">d", buf, struct.calcsize(">QQQI"))[0])

    @staticmethod
    def _is_done(buf: Buffer) -> bool:
        return cast(int, struct.unpack_from(">b", buf, struct.calcsize(">QQQId"))[0]) in (
            lulalib.enums.TaskResultState.DONE,
            lulalib.enums.TaskResultState.CANCELLED,
            lulalib.enums.TaskResultState.ERROR
        )

    async def _cleanup(self, k: bytes, db: bytes | None = None, use_int: bool = False) -> bool:
        _db = await self._stor._env.open_db(db, integerkey=use_int)
        k_removed = False
        async with self._stor._env.begin(db=_db, buffers=True, write=True) as txn:
            async with txn.cursor(db=_db) as cur:
                has_items = await cur.first()
                while has_items:
                    has_items = await cur.next()
                    if not has_items:
                        break
                    key = cur.value()
                    buf = await txn.get(key, db=_db)
                    if not buf:
                        continue
                    if not self._is_expired(buf):
                        continue
                    await cur.delete()
                    if not k_removed:
                        k_removed = key == k
        return k_removed

    async def _get(self, k: uuid.UUID, *, strict: bool, **kwargs) -> lulalib.models.TaskResult | None:
        use_int = cast(bool, kwargs.get("use_int", False))
        db = cast(bytes | None, kwargs.get("db"))
        raise_on_done = cast(bool, kwargs.get("raise_on_done", False))
        kb = self.serialize_key(k)
        cl = await self._cleanup(kb, db, use_int)
        if cl:
            # before parent checks
            if strict:
                raise KeyError()
            return
        b = await self._stor._get(kb, strict=strict, **kwargs)
        if b is None:
            return
        v = self.deserialize_value(b)
        if raise_on_done and self._is_done(b):
            raise lulalib.exc.TaskAlreadyDoneError(
                result=v, task_id=v.task_id
            )
        return v

    async def set(self, k: uuid.UUID, v: lulalib.models.TaskResult, **kwargs) -> None:
        use_int = cast(bool, kwargs.get("use_int", False))
        db = cast(bytes | None, kwargs.get("db"))
        kb = self.serialize_key(k)
        vb = self.serialize_value(v)
        await self._cleanup(kb, db, use_int)
        await self._stor.set(kb, vb, **kwargs)

    async def delete(self, k: uuid.UUID, **kwargs) -> None:
        use_int = cast(bool, kwargs.get("use_int", False))
        db = cast(bytes | None, kwargs.get("db"))
        kb = self.serialize_key(k)
        await self._cleanup(kb, db, use_int)
        return await self._stor.delete(kb, **kwargs)

    async def contains(self, k: bytes, **kwargs) -> bool:
        use_int = cast(bool, kwargs.get("use_int", False))
        db = cast(bytes | None, kwargs.get("db"))
        cl = await self._cleanup(k, db, use_int)
        if cl:
            return False
        return await self._stor.contains(k, **kwargs)


