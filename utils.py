import tkinter
from typing import Callable, Any, Iterable, TypeVar, Union
from rich import print


def handle(
    method: Callable[[int, int], Any],
    x: int,
    y: int,
    _: tkinter.Event,
) -> Any:
    """
    Used to bind events with tkinter's .bind()
    Usage:
    ```python
    <thing>.bind('<mapping>', partial(self.handle, self.<method to bind>, x, y)) ```
    """
    return method(x, y)


K, V, H = TypeVar("K"), TypeVar("T"), TypeVar("Hashable_V")


def dict_reciprocal(o: dict[K, V], key: Callable[[V], H] = lambda x: x) -> dict[V, H]:
    return {key(v): k for k, v in o.items()}


def doublerange(outer, inner=None):
    """
    inner defaults to outer's value
    """
    if inner is None:
        inner = outer
    for a in range(outer):
        for b in range(inner):
            yield a, b


def d(text: str, *args, **kwargs):
    print("[dim]\[debug][/] " + text, *args, **kwargs)


def french_join(elements: Union[list, tuple]) -> str:
    return ", ".join(map(str, elements[:-1])) + " et " + str(elements[-1])
