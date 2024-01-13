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
class Transform2D(Component):
    hflip: bool


@dataclass
class Sprite2D(Component):
    surface: pygame.Surface


@dataclass
class Tileframe2D(Component):
    tileset: Dict[int, pygame.Surface]
    grid: List[List[int]]


@dataclass
class Camera2D(Component):
    pass


@dataclass
class CameraSubject(Component):
    scrollTriggerDistance: float
    followX: bool


@dataclass
class ScreenHandle(Component):
    screen: pygame.Surface


class CameraFollowSystem(System):
    def onFrame(self, cr: ComponentRegistry, delta: float) -> None:
        screen = cr.query_unique(ScreenHandle).screen
        subj, c_sub_pos = list(cr.query2((CameraSubject, Position2D)))[0]
        _cam, c_cam_pos = list(cr.query2((Camera2D, Position2D)))[0]

        canvas_pos = c_sub_pos.position - c_cam_pos.position
        print(canvas_pos)
        if subj.followX and canvas_pos.x < subj.scrollTriggerDistance:
            c_cam_pos.position.x += canvas_pos.x - subj.scrollTriggerDistance
        if subj.followX and canvas_pos.x > screen.get_width() - subj.scrollTriggerDistance:
            c_cam_pos.position.x -= (screen.get_width() - subj.scrollTriggerDistance - canvas_pos.x)


class CanvasSystem(System):
    def onFrame(self, cr: ComponentRegistry, delta: float) -> None:
        screen = cr.query_unique(ScreenHandle).screen
        _cam, c_cam_pos = list(cr.query2((Camera2D, Position2D)))[0]

        camera_off = c_cam_pos.position

        screen.fill("skyblue")

        for c_tileset, c_position in cr.query2((Tileframe2D, Position2D)):
            tile_size = pygame.Vector2(*c_tileset.tileset[0].get_size())
            position = c_position.position - camera_off
            for yi in range(0, len(c_tileset.grid)):
                for xi in range(0, len(c_tileset.grid[0])):
                    tile = c_tileset.grid[yi][xi]
                    target = pygame.Rect(
                        position + pygame.Vector2(tile_size.x * xi, tile_size.y * yi), tile_size)
                    screen.blit(c_tileset.tileset[tile], target)

        for c_shape, c_position in cr.query2((Shape2D, Position2D)):
            position = c_position.position - camera_off
            if c_shape.shape == 'circle':
                pygame.draw.circle(screen, c_shape.color, position, c_position.size.x)
            if c_shape.shape == 'rectangle':
                pygame.draw.rect(screen, c_shape.color, pygame.Rect(position, c_position.size))

        for c_sprite, c_position, c_transform in cr.query3((Sprite2D, Position2D, Transform2D)):
            position = c_position.position - camera_off
            screen.blit(
                pygame.transform.flip(c_sprite.surface, c_transform.hflip, False),
                pygame.Rect(position, c_position.size)
            )

        pygame.display.flip()
