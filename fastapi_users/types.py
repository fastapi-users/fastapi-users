from typing import Callable, Coroutine, TypeVar, Union

RETURN_TYPE = TypeVar("RETURN_TYPE")

DependencyCallable = Callable[
    ..., Union[RETURN_TYPE, Coroutine[None, None, RETURN_TYPE]]
]
