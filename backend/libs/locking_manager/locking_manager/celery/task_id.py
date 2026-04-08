"""Deterministic task ID generation for Celery tasks.

This module provides utilities for generating deterministic task IDs
based on task name and arguments, preventing duplicate task queueing.
"""

import hashlib
import json
from typing import Any

MAX_READABLE_LENGTH = 200


def _serialize_arg(value: Any) -> str:
    """Serialize an argument value for inclusion in task ID.

    Simple types are converted directly to string.
    Complex types are hashed for a compact representation.
    """
    if isinstance(value, str | int | float | bool | type(None)):
        return str(value)
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()[:8]


def generate_task_id(task_name: str, args: tuple[Any, ...] = (), kwargs: dict[str, Any] | None = None) -> str:
    """Generate a deterministic task ID from task name and arguments.

    The generated ID is deterministic - the same task name and arguments
    will always produce the same ID. This prevents duplicate task queueing.

    Format (short): task_name:0=val0,kwarg1=val1
    Format (long):  task_name:sha256hash

    Args:
        task_name: The name of the Celery task
        args: Positional arguments for the task
        kwargs: Keyword arguments for the task

    Returns:
        A deterministic task ID string
    """
    kwargs = kwargs or {}

    parts: list[str] = []
    for i, arg in enumerate(args):
        parts.append(f"{i}={_serialize_arg(arg)}")
    for key in sorted(kwargs.keys()):
        parts.append(f"{key}={_serialize_arg(kwargs[key])}")

    args_str = ",".join(parts)
    readable_id = f"{task_name}:{args_str}" if args_str else task_name

    if len(readable_id) <= MAX_READABLE_LENGTH:
        return readable_id

    hash_input = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    hash_value = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    return f"{task_name}:{hash_value}"
