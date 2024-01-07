from ._component import ComponentRegistry
from typing import Dict, Type


class System:
    def onFrame(self, cr: ComponentRegistry, delta: float) -> None:
        raise NotImplementedError()


class SystemRegistry:
    def __init__(self) -> None:
        self.systems: Dict[Type[System], System] = dict()
    
    def register(self, system: System) -> None:
        self.systems[type(system)] = system
    
    def onFrame(self, cr: ComponentRegistry, dt: float) -> None:
        for s in self.systems.values():
            s.onFrame(cr, dt)

    def registerAll(self, *systems: System) -> None:
        for s in systems:
            self.register(s)
