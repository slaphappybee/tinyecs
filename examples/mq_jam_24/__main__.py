import os
import pygame
import tinyecs as ecs
import tinyecs.physics as ephy
import tinyecs.pygame as epyg
from typing import Dict
from pygame import Vector2
from dataclasses import dataclass

# pygame setup
pygame.init()

clock = pygame.time.Clock()
running = True

SCREEN_HEIGHT = 800
SCREEN_WIDTH = 1600

class AssetLibrary:
    def __init__(self, root_path: str) -> None:
        self.root_path = root_path
        self.images: Dict[str, pygame.Surface] = dict()
        self.sounds: Dict[str, pygame.mixer.Sound] = dict()

    def load(self) -> None:
        for filename in os.listdir(self.root_path):
            if filename.endswith(".png"):
                self._load_image(filename.replace(".png", ""))
            if filename.endswith(".mp3"):
                self._load_sound(filename.replace(".mp3", ""))

    def _load_image(self, name: str) -> None:
        path = os.path.join(self.root_path, name + ".png")
        surface = pygame.transform.scale_by(pygame.image.load(path), 2)
        self.images[name] = surface

    def _load_sound(self, name: str) -> None:
        path = os.path.join(self.root_path, name + ".mp3")
        sound = pygame.mixer.Sound(path)
        self.sounds[name] = sound

    def img(self, name: str) -> pygame.Surface:
        return self.images[name]

    def snd(self, name: str) -> pygame.mixer.Sound:
        return self.sounds[name]


assets = AssetLibrary("examples/mq_jam_24")
assets.load()

cr = ecs.ComponentRegistry()
sr = ecs.SystemRegistry()

def pygame_register_viewport(cr: ecs.ComponentRegistry) -> None:
    size = (SCREEN_WIDTH, SCREEN_HEIGHT)
    screen = pygame.display.set_mode(size, vsync=1)
    ecs.Entity.create_named(
        cr,
        "viewport",
        epyg.ScreenHandle(screen),
        ecs.ViewportProperties(size=pygame.Vector2(*size))
    )

pygame_register_viewport(cr)

@dataclass
class BreadControl(ecs.Component):
    wing_timeout: float
    wing_timeout_state: float
    jump_force: float
    max_y_velocity: float
    air_control: float
    max_control_speed: float


class BreadControlSystem(ecs.System):
    def onFrame(self, cr: ecs.ComponentRegistry, delta: float) -> None:
        keys = pygame.key.get_pressed()

        for c_bread, c_phy in cr.query2((BreadControl, ephy.Physics2D)):
            if keys[pygame.K_SPACE] and c_bread.wing_timeout_state == 0.0:
                c_phy.velocity -= Vector2(0, c_bread.jump_force)
                c_bread.wing_timeout_state = c_bread.wing_timeout
                c_phy.velocity.y = max(c_phy.velocity.y, -1 * c_bread.max_y_velocity)
            
            c_bread.wing_timeout_state = max(0.0, c_bread.wing_timeout_state - delta)

            if keys[pygame.K_LEFT] and c_phy.velocity.x > (-1 * c_bread.max_control_speed):
                c_phy.velocity.x -= c_bread.air_control * delta
            if keys[pygame.K_RIGHT] and c_phy.velocity.x < c_bread.max_control_speed:
                c_phy.velocity.x += c_bread.air_control * delta


ecs.Entity.create_named(
    cr,
    "decor",
    ephy.Position2D(Vector2(0, 0), Vector2(assets.img("bread").get_size())),
    ephy.Transform2D(hflip=False),
    epyg.Sprite2D(assets.img("level1")),
)

ecs.Entity.create_named(
    cr, 
    "bread",
    ephy.Position2D(Vector2(200, 200), Vector2(assets.img("bread").get_size())),
    ephy.Physics2D(Vector2(0, 0)),
    ephy.Transform2D(hflip=False),
    epyg.Sprite2D(assets.img("bread")),
    ephy.Gravity2D(),
    epyg.CameraSubject(scrollTriggerDistance=500, followX=True),
    BreadControl(0.4, 0, 1000, 500, 500, 300),
)

ecs.Entity.create_named(
    cr,
    "camera",
    ephy.Position2D(Vector2(0, 0), Vector2(0, 0)),
    ephy.Physics2D(Vector2(0, 0)),
    epyg.Camera2D()
)


sr.registerAll(
    epyg.CanvasSystem(),
    ephy.PhyicsSystem(),
    ephy.GravitySystem(1000),
    BreadControlSystem(),
    epyg.CameraFollowSystem(),
)

dt = 0.0

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    dt = clock.tick(50) / 1000.0

    sr.onFrame(cr, dt)


pygame.quit()
