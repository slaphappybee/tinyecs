from ._component import ComponentRegistry
from typing import Dict, Type


class System:
    def onFrame(self, cr: ComponentRegistry, delta: float):
        raise NotImplementedError()


class SystemRegistry:
    def __init__(self):
        self.systems: Dict[Type, System] = dict()
    
    def register(self, system: System):
        self.systems[type(system)] = system
    
    def onFrame(self, cr: ComponentRegistry, dt: float) -> None:
        for s in self.systems.values():
            s.onFrame(cr, dt)

    def registerAll(self, *systems: System):
        for s in systems:
            self.register(s)
