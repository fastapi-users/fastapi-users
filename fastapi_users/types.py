from typing import (
    AsyncGenerator,
    AsyncIterator,
    Callable,
    Coroutine,
    Generator,
    TypeVar,
    Union,
)

RETURN_TYPE = TypeVar("RETURN_TYPE")

DependencyCallable = Callable[
    ...,
    Union[
        RETURN_TYPE,
        Coroutine[None, None, RETURN_TYPE],
        AsyncGenerator[RETURN_TYPE, None],
        Generator[RETURN_TYPE, None, None],
        AsyncIterator[RETURN_TYPE],
    ],
]
