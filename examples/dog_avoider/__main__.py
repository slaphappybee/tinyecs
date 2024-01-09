import os
import pygame
import tinyecs as ecs
import tinyecs.physics as ephy
import tinyecs.pygame as epyg
from typing import Dict
from pygame import Vector2

# pygame setup
pygame.init()

clock = pygame.time.Clock()
running = True

SCREEN_HEIGHT = 720


cr = ecs.ComponentRegistry()


class DogAvoiderAssetLibrary:
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
        surface = pygame.transform.scale_by(pygame.image.load(path), 4)
        self.images[name] = surface

    def _load_sound(self, name: str) -> None:
        path = os.path.join(self.root_path, name + ".mp3")
        sound = pygame.mixer.Sound(path)
        self.sounds[name] = sound

    def img(self, name: str) -> pygame.Surface:
        return self.images[name]

    def snd(self, name: str) -> pygame.mixer.Sound:
        return self.sounds[name]


assets = DogAvoiderAssetLibrary("examples/dog_avoider")
assets.load()


player = ecs.Entity.create_named(
    cr,
    "player",
    epyg.Position2D(pygame.Vector2(300, 400), pygame.Vector2(40, 108)),
    ephy.Physics2D(pygame.Vector2(0, 0)),
    ephy.Gravity2D(),
    epyg.Sprite2D(assets.img("hat_man")),
    epyg.Transform2D(hflip=False),
    ephy.PlatformControl2D(400, 1600, 200, 600, 600),
)


class DogFlag(ecs.Component):
    pass


class DogScript(ecs.System):
    def onFrame(self, cr: ecs.ComponentRegistry, delta: float) -> None:
        for _dog, xform, phy in cr.query3((DogFlag, epyg.Transform2D, ephy.Physics2D)):
            if phy.velocity.x > 0:
                xform.hflip = True
            else:
                xform.hflip = False


dog = ecs.Entity.create_named(
    cr,
    "dog",
    epyg.Position2D(pygame.Vector2(600, 600), pygame.Vector2(27, 15)),
    epyg.Sprite2D(assets.img("dog")),
    epyg.Transform2D(hflip=False),
    ephy.Physics2D(Vector2(300, 0)),
    ephy.WaypointControl2D([Vector2(40, 600), Vector2(1150, 600)], 0),
    DogFlag(),
)

wall_sprite = assets.img("background")
walls = ecs.Entity.create_named(
    cr,
    "walls",
    epyg.Position2D(
        position=pygame.Vector2(0, SCREEN_HEIGHT - wall_sprite.get_height()),
        size=pygame.Vector2(wall_sprite.get_width() * 8, wall_sprite.get_height())
    ),
    epyg.Tileframe2D({0: wall_sprite}, [[0] * 8])
)

tree_sprite = assets.img("trees")
trees = ecs.Entity.create_named(
    cr,
    "trees",
    epyg.Position2D(
        position=pygame.Vector2(0, SCREEN_HEIGHT - tree_sprite.get_height() * 2),
        size=pygame.Vector2(tree_sprite.get_width() * 8, tree_sprite.get_height())
    ),
    epyg.Tileframe2D({0: tree_sprite}, [[0] * 8])
)


def pygame_register_viewport() -> None:
    size = (1280, SCREEN_HEIGHT)
    screen = pygame.display.set_mode(size, vsync=1)
    ecs.Entity.create_named(
        cr,
        "viewport",
        epyg.ScreenHandle(screen),
        ecs.ViewportProperties(size=pygame.Vector2(*size))
    )


pygame_register_viewport()

pygame.mixer.init()
assets.snd("music").play(-1)

sr = ecs.SystemRegistry()
sr.registerAll(
    epyg.CanvasSystem(),
    ephy.GravitySystem(1200),
    ephy.PhyicsSystem(),
    ephy.PlatformControlSystem(),
    ephy.WaypointControlSystem(),
    DogScript()
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
