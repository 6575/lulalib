import pytest
import pytest_asyncio

import asyncio
import secrets
import tempfile
import lmdb
import lmdb.aio


@pytest.fixture(scope="module")
def event_loop() -> asyncio.AbstractEventLoop:
    loop = asyncio.new_event_loop()
    return loop

@pytest.fixture(scope="function")
def token16() -> bytes:
    return secrets.token_bytes(16)

