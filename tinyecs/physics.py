from ._component import Component, ComponentRegistry, ViewportProperties
from ._system import System
from ._utils import clamp
from .pygame import Position2D
from dataclasses import dataclass
import pygame
import numpy


@dataclass
class Physics2D(Component):
    velocity: pygame.Vector2


@dataclass
class PlatformControl2D(Component):
    hrztl_accel: float
    hrztl_decel: float
    hrztl_min_speed: float
    hrztl_max_speed: float
    jump_force: float


class PlatformControlSystem(System):
    def onFrame(self, cr: ComponentRegistry, delta: float) -> None:
        keys = pygame.key.get_pressed()

        for c_pla, c_phy in cr.query2((PlatformControl2D, Physics2D)):

            if keys[pygame.K_a]:
                c_phy.velocity.x = clamp(
                    max_value=-1 * c_pla.hrztl_min_speed,
                    min_value=-1 * c_pla.hrztl_max_speed,
                    value=c_phy.velocity.x + -1 * c_pla.hrztl_accel * delta
                )
            elif keys[pygame.K_d]:
                c_phy.velocity.x = clamp(
                    min_value=1 * c_pla.hrztl_min_speed,
                    max_value=1 * c_pla.hrztl_max_speed,
                    value=c_phy.velocity.x + 1 * c_pla.hrztl_accel * delta
                )
            else:
                decel = numpy.sign(c_phy.velocity.x) * c_pla.hrztl_decel * delta
                new_velocity_x = c_phy.velocity.x - decel
                if numpy.sign(new_velocity_x) != numpy.sign(c_phy.velocity.x):
                    c_phy.velocity.x = 0
                else:
                    c_phy.velocity.x = new_velocity_x

            if keys[pygame.K_s] and c_phy.velocity.y == 0:
                c_phy.velocity.y = -1 * c_pla.jump_force


class PhyicsSystem(System):
    def onFrame(self, cr: ComponentRegistry, delta: float) -> None:
        viewport_size = list(cr.query_single(ViewportProperties))[0].size

        for c_physics, c_position in cr.query2((Physics2D, Position2D)):
            c_position.position = c_position.position + c_physics.velocity * delta

            y_limit = viewport_size.y - 60
            if c_position.position.y + c_position.size.y > y_limit:
                c_position.position.y = y_limit - c_position.size.y
                c_physics.velocity.y = 0


class GravitySystem(System):
    def __init__(self, strength: float):
        self.strength = strength

    def onFrame(self, cr: ComponentRegistry, delta: float) -> None:
        for physics in cr.query_single(Physics2D):
            physics.velocity = physics.velocity + pygame.Vector2(0, self.strength) * delta
