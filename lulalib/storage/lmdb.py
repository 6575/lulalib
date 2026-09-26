from typing import Any, cast

import lmdb
import lmdb.aio

import lulalib.abc
import lulalib.core.hashes


class LMDBStorage(lulalib.abc.IStorage[bytes, bytes]):

    def __init__(self, env: lmdb.aio.AsyncEnvironment):
        self._env = env

    async def _get(self, k: bytes, *, strict: bool, **kwargs) -> bytes | None:
        use_int = cast(bool, kwargs.get("use_int", False))
        db = cast(bytes | None, kwargs.get("db"))
        k = lulalib.core.hashes.hash_fnv1a_64(k).to_bytes(8)
        _db = await self._env.open_db(key=db, integerkey=use_int)
        async with self._env.begin(write=False, db=_db) as txn:
            val = await txn.get(k, db=_db)
            if (not val) and strict:
                raise KeyError(k)
            return val

    async def set(self, k: bytes, v: bytes, **kwargs) -> None:
        use_int = cast(bool, kwargs.get("use_int", False))
        db = cast(bytes | None, kwargs.get("db"))
        k = lulalib.core.hashes.hash_fnv1a_64(k).to_bytes(8)
        _db = await self._env.open_db(key=db, integerkey=use_int)
        async with self._env.begin(write=True, db=_db) as txn:
            res = await txn.put(k, v,db=_db)
            if not res:
                raise KeyError(k)

    async def delete(self, k: bytes, **kwargs) -> None:
        use_int = cast(bool, kwargs.get("use_int", False))
        db = cast(bytes | None, kwargs.get("db"))
        k = lulalib.core.hashes.hash_fnv1a_64(k).to_bytes(8)
        _db = await self._env.open_db(key=db, integerkey=use_int)
        async with self._env.begin(write=True, db=_db) as txn:
            res = await txn.delete(k, db=_db)
            if not res:
                raise KeyError(k)

    async def contains(self, k: bytes, **kwargs) -> bool:
        use_int = cast(bool, kwargs.get("use_int", False))
        db = cast(bytes | None, kwargs.get("db"))
        k = lulalib.core.hashes.hash_fnv1a_64(k).to_bytes(8)
        _db = await self._env.open_db(key=db, integerkey=use_int)
        async with self._env.begin(db=_db) as txn:
            async with txn.cursor(db=_db) as cur:
                await cur.first()
                res = await cur.set_key(k)
                return res
            


