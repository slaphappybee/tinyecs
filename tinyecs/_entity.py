from typing import List, Self, TypeVar, Type
from ._component import Component, ComponentRegistry


C1 = TypeVar("C1", bound=Component)

class Entity(Component):
    def __init__(self, cr: ComponentRegistry):
        cr.registry.setdefault(Entity.__name__, dict())
        cr.registry[Entity.__name__][id(self)] = self
        self.components: List[Component] = list()
        self.name = f"entity-{id(self)}"

    def register(self, cr: ComponentRegistry, component: Component) -> None:
        classname = component.__class__.__name__
        cr.registry.setdefault(classname, dict())
        cr.registry[classname][id(self)] = component
        self.components.append(component)


    def get(self, component: Type[C1]) -> C1:
        return [c for c in self.components if type(c) == component][0]

    @classmethod
    def create(cls, cr: ComponentRegistry, *args: Component) -> Self:
        entity = cls(cr)
        for component in args:
            entity.register(cr, component)
        return entity

    @classmethod
    def create_named(cls, cr: ComponentRegistry, name: str, *args: Component) -> Self:
        entity = cls.create(cr, *args)
        entity.name = name
        return entity
