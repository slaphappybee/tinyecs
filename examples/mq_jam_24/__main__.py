import os
import pygame
import tinyecs as ecs
import tinyecs.physics as ephy
import tinyecs.pygame as epyg
from typing import Dict
from pygame import Vector2
from dataclasses import dataclass
import numpy

# pygame setup
pygame.init()

clock = pygame.time.Clock()
running = True

SCREEN_HEIGHT = 950
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

pygame.mixer.init()
assets.snd("music").play(-1)

cr = ecs.ComponentRegistry()

def pygame_register_viewport(cr: ecs.ComponentRegistry) -> None:
    size = (SCREEN_WIDTH, SCREEN_HEIGHT)
    screen = pygame.display.set_mode(size, vsync=1)
    return screen

screen = pygame_register_viewport(cr)

@dataclass
class BreadCollisionFlag(ecs.Component):
    name: str


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
        colliders = list(cr.query3((BreadCollisionFlag, epyg.Mask2D, ephy.Position2D)))

        for c_bread, c_phy, c_mask, c_pos in cr.query4((BreadControl, ephy.Physics2D, epyg.Mask2D, ephy.Position2D)):
            if keys[pygame.K_SPACE] and c_bread.wing_timeout_state == 0.0:
                if c_phy.velocity.y > -1 * c_bread.max_y_velocity:
                    c_phy.velocity -= Vector2(0, c_bread.jump_force)
                    c_bread.wing_timeout_state = c_bread.wing_timeout
                    c_phy.velocity.y = max(c_phy.velocity.y, -1 * c_bread.max_y_velocity)
            
            c_bread.wing_timeout_state = max(0.0, c_bread.wing_timeout_state - delta)

            if keys[pygame.K_LEFT] and c_phy.velocity.x > (-1 * c_bread.max_control_speed):
                c_phy.velocity.x -= c_bread.air_control * delta
            if keys[pygame.K_RIGHT] and c_phy.velocity.x < c_bread.max_control_speed:
                c_phy.velocity.x += c_bread.air_control * delta
            
            is_bouncing = False
            is_colliding_decor = False

            for c_flag, c_omask, c_opos in colliders:
                if c_mask.mask.overlap(c_omask.mask, c_opos.position - c_pos.position):
                    print(c_flag.name, c_pos)
                    if(c_flag.name == "vbounce"):
                        c_phy.velocity.y = - c_phy.velocity.y
                        # Minimum velocity
                        c_phy.velocity.y = numpy.sign(c_phy.velocity.y) * max(abs(c_phy.velocity.y), 100)
                        is_bouncing = True
                    if(c_flag.name == "decor"):
                        is_colliding_decor = True
            
            if is_colliding_decor and not is_bouncing:
                _, sprite = list(cr.query2((BreadControl, epyg.Sprite2D)))[0]
                sprite.surface = assets.img("splash")
                cr.query_unique(GameStateComponent).is_running = False


decor_mask = pygame.mask.from_surface(assets.img("level1"))
decor_vbounce_img = assets.img("level1").copy()
decor_vbounce_img.set_colorkey(pygame.Color(255, 0, 0))
vbounce_mask = pygame.mask.from_surface(decor_vbounce_img)
vbounce_mask.invert()


decor_sprite = decor_mask.to_surface(assets.img("decor"), setsurface=assets.img("decor"))
vbounce_mask.to_surface(decor_sprite, setcolor=pygame.Color(50, 0, 100), unsetcolor=None)


@dataclass
class GameStateComponent(ecs.Component):
    is_running: bool


def initialize_level() -> ecs.Entity:
    cr.reset()

    ecs.Entity.create_named(
        cr,
        "viewport",
        epyg.ScreenHandle(screen),
        ecs.ViewportProperties(size=pygame.Vector2(SCREEN_WIDTH, SCREEN_HEIGHT))
    )

    ecs.Entity.create_named(
        cr,
        "background",
        ephy.Position2D(Vector2(-200, 0), Vector2(assets.img("background").get_size())),
        ephy.Transform2D(hflip=False),
        epyg.Sprite2D(assets.img("background")),
        epyg.CameraFlags(scrollRatio=0.5)
    )

    ecs.Entity.create_named(
        cr,
        "decor",
        ephy.Position2D(Vector2(0, 0), Vector2(assets.img("bread").get_size())),
        ephy.Transform2D(hflip=False),
        epyg.Sprite2D(decor_sprite),
        epyg.Mask2D(decor_mask),
        BreadCollisionFlag("decor")
    )

    ecs.Entity.create_named(
        cr,
        "vbounce_zones",
        ephy.Position2D(Vector2(0, 0), Vector2(assets.img("bread").get_size())),
        ephy.Transform2D(hflip=False),
        epyg.Mask2D(vbounce_mask),
        BreadCollisionFlag("vbounce")
    )

    bread_mask = pygame.mask.from_surface(assets.img("bread"))

    ecs.Entity.create_named(
        cr, 
        "bread",
        ephy.Position2D(Vector2(300, 200), Vector2(assets.img("bread").get_size())),
        ephy.Physics2D(Vector2(0, 0)),
        ephy.Transform2D(hflip=False),
        epyg.Sprite2D(assets.img("bread")),
        epyg.Mask2D(bread_mask),
        BreadControl(0.4, 0, 1000, 500, 500, 300),
        ephy.Gravity2D(),
        epyg.CameraSubject(scrollTriggerDistance=600, followX=True),
    )

    ecs.Entity.create_named(
        cr,
        "camera",
        ephy.Position2D(Vector2(0, 0), Vector2(0, 0)),
        ephy.Physics2D(Vector2(0, 0)),
        epyg.Camera2D()
    )

    game_state = ecs.Entity.create_named(
        cr,
        "game_state",
        GameStateComponent(is_running=True)
    )

    return game_state


sr_running = ecs.SystemRegistry()
sr_running.registerAll(
    epyg.CanvasSystem(),
    ephy.PhyicsSystem(),
    ephy.GravitySystem(1000),
    BreadControlSystem(),
    epyg.CameraFollowSystem(),
)

sr_lost = ecs.SystemRegistry()
sr_lost.registerAll(
    epyg.CanvasSystem()
)

dt = 0.0


game_state = initialize_level()
gsc = game_state.get(GameStateComponent)


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    dt = clock.tick(50) / 1000.0

    if gsc.is_running:
        sr_running.onFrame(cr, dt)
    else:
        sr_lost.onFrame(cr, dt)
        clock.tick(3)
        game_state = initialize_level()
        gsc = game_state.get(GameStateComponent)


pygame.quit()
