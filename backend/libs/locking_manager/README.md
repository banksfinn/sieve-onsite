# Locking Manager

Redis-based distributed locking and Celery task utilities.

## Features

- **Redis Client**: Simple Redis client wrapper with lazy initialization
- **Locking Client**: Generic distributed locking with context manager support
- **Celery Task Decorator**: `@locked_task` decorator for automatic Redis locking on Celery tasks

## Usage

### Locked Celery Tasks

```python
from locking_manager.celery.task import locked_task

@locked_task(time_limit=300)
def process_user_data(user_id: int) -> None:
    # Only one instance of this task with the same user_id can run at a time
    pass
```

### Generic Locking

```python
from locking_manager.clients.locking_client import locking_client

with locking_client.lock_context("my_lock_key", timeout=60) as lock:
    if lock:
        # Lock acquired, do work
        pass
    else:
        # Lock not acquired
        pass
```
