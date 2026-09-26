import uuid
import secrets
import asyncio
import random
import time
import contextvars
import tempfile

import lmdb
import lmdb.aio

import lulalib
import lulalib.exc


async def test_scheduler():
    # prepare
    dbpath = tempfile.TemporaryDirectory(suffix="_lulalib_stor_test")

    env = lmdb.Environment(dbpath.name)
    aenv = lmdb.aio.wrap(env)
    storage = lulalib.LMDBStorage(aenv)

    shutdown = asyncio.Event()
    ctx_auth = contextvars.ContextVar[uuid.UUID]("ctx_auth")
    ctx_oid = contextvars.ContextVar[uuid.UUID]("ctx_oid")

    ca_token = ctx_auth.set(uuid.uuid4())
    co_token = ctx_oid.set(uuid.uuid4())

    conf = lulalib.LulalibConfig()
    conf.ctx_auth = ctx_auth
    conf.ctx_oid = ctx_oid
    conf.shutdown = shutdown
    conf.set_type_adapter(0, lulalib.MSPDictType())

    scheduler = lulalib.default_scheduler(storage, conf)

    # multithreaded sample function
    @scheduler(ttl=60, raise_on_done=True)
    def idle(sec: int, /):
        time.sleep(sec * .1)
        return {
            "success": True,
            "idle": sec
        }
    try:
        sec = random.randint(3, 10)
        # spawn the task, wait until the task is done
        task = await idle(sec)
        result = await task

        assert result["idle"] == sec

        # a
        exc = False
        try:
            await idle(sec)
        except lulalib.exc.TaskAlreadyDoneError:
            exc = True
        
        assert exc

    finally:
        # reset the context like normally
        ctx_auth.reset(ca_token)
        ctx_oid.reset(co_token)
        await aenv.close()
        dbpath.cleanup()


    