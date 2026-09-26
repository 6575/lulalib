from typing import TypeVar, Generic, overload


import asyncio
import contextvars

import lulalib.abc
import lulalib.core
import lulalib.meta
import lulalib.models
import lulalib.scheduler
import lulalib.storage
import lulalib.typeadapters
import lulalib.observers

KT = TypeVar("KT")
VT = TypeVar("VT")
STOR_TYP = TypeVar("STOR_TYP", bound=lulalib.abc.IStorage)


class LulalibStorage(Generic[KT, VT]):

    __slots__ = ("_conf", "_def_stor", )

    _def_stor: lulalib.abc.IStorage | None

    def __init__(self):
        self._def_stor = None

    @property
    def storage(self) -> lulalib.abc.IStorage[KT, VT]:
        if self._def_stor is None:
            raise AttributeError()
        return self._def_stor
    
    @storage.setter
    def storage(self, value: lulalib.abc.IStorage[KT, VT]) -> None:
        if not isinstance(value, lulalib.abc.IStorage):
            raise TypeError()
        self._def_stor = value



def default_scheduler(bstor: lulalib.storage.LMDBStorage, conf: lulalib.core.LulalibConfig):
    conf.set_type_adapter(0, lulalib.typeadapters.MSPDictType())
    ob = lulalib.observers.TaskResultObserver(lulalib.models.TaskResult)
    ob.conf = conf
    lulalib.storage.SchedulerLMDBStorage(bstor, ob)
    sched = lulalib.scheduler.Scheduler(ob)
    return sched
    


