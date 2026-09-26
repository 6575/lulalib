import secrets
import tempfile

import lmdb
import lmdb.aio

import lulalib
import lulalib.core.hashes


async def test_storage():
    # initialize lmdb env
    dbpath = tempfile.TemporaryDirectory(suffix="_lulalib_sched_test")
    env = lmdb.Environment(dbpath.name, max_dbs=1)
    db = secrets.token_bytes(4)
    aenv = lmdb.aio.wrap(env)
    storage = lulalib.LMDBStorage(aenv)
    
    key = secrets.token_bytes(16)
    value = secrets.token_bytes(16)

    try:
        # test SET
        await storage.set(key, value, db=db, use_int=True)
        # test IN
        key_in_db = await storage.contains(key, db=db, use_int=True)
        assert key_in_db, "key is not IN db"
        # test GET
        value_get = await storage.get(key, strict=True, db=db, use_int=True)
        assert secrets.compare_digest(value_get, value), "SET and GET values do not match"
        # test update via SET
        new_value = secrets.token_bytes(16)
        await storage.set(key, new_value, db=db, use_int=True)
        # test DELETE
        await storage.delete(key, db=db, use_int=True)
        # check with IN
        assert not await storage.contains(key, db=db, use_int=True), "DELETE did not work"
    finally:
        #shutdown
        await aenv.close()
        dbpath.cleanup()

