from typing import List, Self
from ._component import Component, ComponentRegistry


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
