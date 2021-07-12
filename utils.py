import tkinter
from typing import Callable, Any, TypeVar


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
    <thing>.bind('<mapping>', partial(self.handle, self.<method to bind>, x, y))
    ```
    """
    return method(x, y)


K, V = TypeVar("K"), TypeVar("T")


def dict_reciprocal(o: dict[K, V]) -> dict[V, K]:
    return {v: k for k, v in o.items()}

def doublerange(outer, inner=None):
    if inner is None:
        inner = outer
    for a in range(outer):
        for b in range(inner):
            yield a, b
