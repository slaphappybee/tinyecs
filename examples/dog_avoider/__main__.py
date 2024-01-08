import pygame
import tinyecs as ecs
import tinyecs.physics as ephy
import tinyecs.pygame as epyg

# pygame setup
pygame.init()

clock = pygame.time.Clock()
running = True

SCREEN_HEIGHT = 720


def load_img(name: str) -> pygame.Surface:
    return pygame.transform.scale_by(pygame.image.load(name), 4)


cr = ecs.ComponentRegistry()


player = ecs.Entity.create_named(
    cr,
    "player",
    epyg.Position2D(pygame.Vector2(300, 400), pygame.Vector2(40, 108)),
    ephy.Physics2D(pygame.Vector2(0, 0)),
    epyg.Sprite2D(load_img("examples/dog_avoider/hat_man.png")),
    epyg.Transform2D(hflip=False),
    ephy.PlatformControl2D(400, 1600, 200, 600, 600),
)

wall_sprite = load_img("examples/dog_avoider/background.png")
walls = ecs.Entity.create_named(
    cr,
    "walls",
    epyg.Position2D(
        position=pygame.Vector2(0, SCREEN_HEIGHT - wall_sprite.get_height()),
        size=pygame.Vector2(wall_sprite.get_width() * 8, wall_sprite.get_height())
    ),
    epyg.Tileframe2D({0: wall_sprite}, [[0] * 8])
)

tree_sprite = load_img("examples/dog_avoider/trees.png")
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

sr = ecs.SystemRegistry()
sr.registerAll(
    epyg.CanvasSystem(),
    ephy.GravitySystem(1200),
    ephy.PhyicsSystem(),
    ephy.PlatformControlSystem(),
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
