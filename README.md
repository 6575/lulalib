# Lulalib
**Lulalib** is a simple, yet extendable caching and task scheduling micro framework.


## Documentation
In this section, abstract and non-abstract key components are presented.

### Abstract key components
`lulalib.abc` features abstract bases (Interfaces) for every significant component of the application
- `IStorage[KT, VT]` is an abstract base for the storage component.
    - `.get(k: KT) -> VT | None` or `.get(k: KT, *, strict = True) -> VT`
        - Retrieve the value from the *storage*.
        - When `strict` is used and there is not value matched the key, `KeyError` is raised;
    - `.set(k: KT, v: KT) -> None`
        - Set the value to the key;
    - `.contains(k: KT) -> bool`
        - Check if there is any value matching the key;
    - `.delete(k: KT) -> None`
        - Delete the value matching the key.
    - Implementation notes
        - *The original implementation is using `lmdb` engine (`lulalib.storage.LMDBStorage`);*
        - *Scheduler component is using `SchedulerLMDBStorage` TTL storage with custom type adapters applied.*
- `ITypeAdapter[T]` enables serlialization and deserialzation of custom types on the go with no effort.
    - `.serialize(v: T) -> bytes`
        - Get the binary format repsenetation of the custom type value
    - `.deserialize(v: bytes) -> T`
        - Construct the custom type from the binary data
    - Implementation notes
        - `dict` (via `messagepack`), `bytes`, `UUID` and `TaskResult` are supported out of the box.

### Traits
`lulalib.traits` features traits/mixins for the compoentents, preserving their functioning and original purpose.

- `SupportsKVTypeAdapters[KT, VT]` is designed to be used by a *storage*. This traits enables usage of two *type adapters* both for key and value respectively.
    - `.serialize_key(data: KT) -> bytes`
    - `.deserialize_key(data: bytes) -> KT`
    - `.serialize_value(data: VT) -> bytes`
    - `.deserialize_value(data: bytes) -> VT`

### Models
All models are presented in `lulalib.models`
- `TaskResult[T]` represents a task result in the database.
    - Representation
        - Header in binary struct format: `>QQQIdb`
        - Header in C laguage:
            ```c
            typedef struct TaskResult
            {
                unsigned long long idl;
                unsigned long long idh;
                unsigned long long type_id;
                unsigned int sz;
                double exp_at;
                char state;
            }
            ```
    - Constructors
        - `TaskResult.from_buffer(observer: TaskResultObserver, buf: Buffer) -> TaskResult`
            - Construct a new object from readable buffer
    - Properties
        - `.hdr -> bytes`
            - Get object's binary header
        - `.state -> int`
            - Procedure state
        - `.result -> T`
            - Get object's result value if available

    - Methods
        - `.__bytes__() -> bytes`
            - Get object's binary representation like `obj_b = bytes(obj)`
        - `.__await__() -> T`
            - `await` on object to get the task result as soon as available like `result = await obj`
        - `.notify() -> None`
            - Should always be invoked by an observer. 

### Observers
All observers are presented in `lulalib.observers`
- `TaskResultObserver` is observing `TaskResult` *(following: object)*.
    - **Responsibility**
        - Managing (CRUD operations) related to the object, features internal object pool;
        - Events emission during object management.
    - `.set_state(result: TaskResult) -> None`
        - Update the object state and emit the event
    - `.set_result(result: TaskResult) -> None`
        - Update the object result (value returned from the procedure exection)
    - `.set_callback(fut: asyncio.Future[Any], result: TaskResult[Any]) -> None`
        - Modify object's state and result value upon procedure finalization.
    - `.get_task_result(task_id: uuid.UUID, exp_at: float, _typ_ad: int) -> TaskResult[Any]`
        - Either retrieve object from the pool or create a new instance
    - `.task_result_from_buffer(buf: Buffer,raise_on_done=True) -> TaskResult[Any]`
        - Either retrieve object from the pool or construct a new instance from buffer
