from dataclasses import dataclass
from ._component import Component, ComponentRegistry
from ._system import System
from typing import Dict, List
import pygame


@dataclass
class Position2D(Component):
    position: pygame.Vector2
    size: pygame.Vector2

@dataclass
class Shape2D(Component):
    shape: str
    color: str

@dataclass
class Sprite2D(Component):
    surface: pygame.Surface


@dataclass
class Tileframe2D(Component):
    tileset: Dict[int, pygame.Surface]
    grid: List[List[int]]


@dataclass
class ScreenHandle(Component):
    screen: pygame.Surface


class CanvasSystem(System):
    def onFrame(self, cr: ComponentRegistry, delta: float):
        screen = list(cr.query_single(ScreenHandle))[0].screen
        screen.fill("skyblue")

        for c_tileset, c_position in cr.query2((Tileframe2D, Position2D)):
            tile_size = pygame.Vector2(*c_tileset.tileset[0].get_size())
            for yi in range(0, len(c_tileset.grid)):
                for xi in range(0, len(c_tileset.grid[0])):
                    tile = c_tileset.grid[yi][xi]
                    target = pygame.Rect(c_position.position + 
                        pygame.Vector2(tile_size.x * xi, tile_size.y * yi), tile_size)
                    screen.blit(c_tileset.tileset[tile], target)

        for c_shape, c_position in cr.query2((Shape2D, Position2D)):
            if c_shape.shape == 'circle':
                pygame.draw.circle(screen, c_shape.color, c_position.position, c_position.size.x)
            if c_shape.shape == 'rectangle':
                pygame.draw.rect(screen, c_shape.color, pygame.Rect(c_position.position, c_position.size))

        for c_sprite, c_position in cr.query2((Sprite2D, Position2D)):
            screen.blit(c_sprite.surface, pygame.Rect(c_position.position, c_position.size))

        pygame.display.flip()
