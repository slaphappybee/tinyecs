from dataclasses import dataclass
from typing import Dict, Tuple, Iterator, cast, Type, TypeVar
from pygame import Vector2


@dataclass
class Component:
    pass


C1 = TypeVar("C1", bound=Component)
C2 = TypeVar("C2", bound=Component)


class ComponentRegistry:
    def __init__(self) -> None:
        self._registry: Dict[str, Dict[int, Component]] = dict()

    def _gen_query(self, mask: Tuple[Type[Component], ...]) -> Iterator[Tuple[Component, ...]]:
        names = [mask_item.__name__ for mask_item in mask]
        entities = self._registry.get(names[0], dict()).keys()
        for e in entities:
            yield tuple(self._registry[name][e] for name in names)

    def query_single(self, ctype: Type[C1]) -> Iterator[C1]:
        for c, in self._gen_query((ctype, )):
            yield cast(C1, c)

    def query2(self, mask: Tuple[Type[C1], Type[C2]]) -> Iterator[Tuple[C1, C2]]:
        return cast(Iterator[Tuple[C1, C2]], self._gen_query(mask))

    @property
    def registry(self) -> Dict[str, Dict[int, Component]]:
        return self._registry


@dataclass
class ViewportProperties(Component):
    size: Vector2
