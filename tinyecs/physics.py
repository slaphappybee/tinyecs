from ._component import Component, ComponentRegistry, ViewportProperties
from ._system import System
from ._utils import clamp
from .pygame import Position2D, Transform2D
from dataclasses import dataclass
from typing import List
import pygame
import numpy


@dataclass
class Physics2D(Component):
    velocity: pygame.Vector2


@dataclass
class Gravity2D(Component):
    pass


@dataclass
class PlatformControl2D(Component):
    hrztl_accel: float
    hrztl_decel: float
    hrztl_min_speed: float
    hrztl_max_speed: float
    jump_force: float


@dataclass
class WaypointControl2D(Component):
    waypoints: List[pygame.Vector2]
    current: int


class PlatformControlSystem(System):
    def onFrame(self, cr: ComponentRegistry, delta: float) -> None:
        keys = pygame.key.get_pressed()

        for c_pla, c_phy, c_tra in cr.query3((PlatformControl2D, Physics2D, Transform2D)):
            if keys[pygame.K_a]:
                c_phy.velocity.x = clamp(
                    max_value=-1 * c_pla.hrztl_min_speed,
                    min_value=-1 * c_pla.hrztl_max_speed,
                    value=c_phy.velocity.x + -1 * c_pla.hrztl_accel * delta
                )
                c_tra.hflip = True
            elif keys[pygame.K_d]:
                c_phy.velocity.x = clamp(
                    min_value=1 * c_pla.hrztl_min_speed,
                    max_value=1 * c_pla.hrztl_max_speed,
                    value=c_phy.velocity.x + 1 * c_pla.hrztl_accel * delta
                )
                c_tra.hflip = False
            else:
                decel = numpy.sign(c_phy.velocity.x) * c_pla.hrztl_decel * delta
                new_velocity_x = c_phy.velocity.x - decel
                if numpy.sign(new_velocity_x) != numpy.sign(c_phy.velocity.x):
                    c_phy.velocity.x = 0
                else:
                    c_phy.velocity.x = new_velocity_x

            if keys[pygame.K_s] and c_phy.velocity.y == 0:
                c_phy.velocity.y = -1 * c_pla.jump_force


class WaypointControlSystem(System):
    def onFrame(self, cr: ComponentRegistry, delta: float) -> None:
        for c_way, c_phy, c_pos in cr.query3((WaypointControl2D, Physics2D, Position2D)):
            target = c_way.waypoints[c_way.current]

            # TODO hack: should adjust position as well
            if (target - c_pos.position).length() < (c_phy.velocity.length() * delta):
                c_way.current = (c_way.current + 1) % len(c_way.waypoints)
                target = c_way.waypoints[c_way.current]

            c_phy.velocity = c_phy.velocity.length() * (target - c_pos.position).normalize()


class PhyicsSystem(System):
    def onFrame(self, cr: ComponentRegistry, delta: float) -> None:
        for c_physics, c_position in cr.query2((Physics2D, Position2D)):
            c_position.position = c_position.position + c_physics.velocity * delta


class GravitySystem(System):
    def __init__(self, strength: float):
        self.strength = strength

    def onFrame(self, cr: ComponentRegistry, delta: float) -> None:
        viewport_size = list(cr.query_single(ViewportProperties))[0].size

        for _gra, physics, c_position in cr.query3((Gravity2D, Physics2D, Position2D)):
            physics.velocity = physics.velocity + pygame.Vector2(0, self.strength) * delta

            # y_limit = viewport_size.y - 60
            # if c_position.position.y + c_position.size.y > y_limit:
            #     c_position.position.y = y_limit - c_position.size.y
            #     physics.velocity.y = 0
