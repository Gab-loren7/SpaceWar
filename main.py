from dataclasses import dataclass
from pathlib import Path
import math
import random

import pyxel


# ~~~~~~~~~~~~~~~~~
# CONFIGURAÇÕES DA JANELA
# ~~~~~~~~~~~~~~~~~

SCREEN_WIDTH = 300
SCREEN_HEIGHT = 300

RESOURCE_PATH = Path(__file__).resolve().parent / "my_resource.pyxres"


# ~~~~~~~~~~~~~~~~~
# CONFIGURAÇÕES DA NAVE
# ~~~~~~~~~~~~~~~~~

SHIP_RADIUS = 6
SHIP_SCALE = 1

SHIP_START_X = 50.0
SHIP_START_Y = 50.0

ROTATION_SPEED = 0.1
TOP_SPEED = 10.0

MAX_ACCELERATION = 1.0
ACCELERATION_DELTA = 0.28

ACCEL_RAMP_UP = 0.08
ACCEL_RAMP_DOWN = 0.12
ACCEL_BRAKE = 0.30

FRICTION = 0.992


# ~~~~~~~~~~~~~~~~~
# CONFIGURAÇÕES DA ESTRELA
# ~~~~~~~~~~~~~~~~~

STAR_POSITION = {
    "x": 150,
    "y": 150
}

STAR_SCALE = 2
STAR_RADIUS = 8 * STAR_SCALE

COLLISION_MARGIN = 6

GRAVITY_STRENGTH = 300.0
GRAVITY_MIN_DIST = 35.0


# ~~~~~~~~~~~~~~~~~
# CONFIGURAÇÕES DA PARTIDA
# ~~~~~~~~~~~~~~~~~

EXPLOSION_DURATION = 40
INVINCIBLE_DURATION = 80

COMBO_TIME = 180
MAX_COMBO = 10

MERCH_RADIUS = 2

POINTS = [
    10,
    20,
    -10,
    40,
    -30,
    80,
    -50
]

# Quanto maior o peso, maior a chance de aparecer.
# Os valores positivos aparecem com maior frequência.
WEIGHTS = [
    35,
    25,
    15,
    12,
    7,
    4,
    2
]

WEIGHT_BUDGET = 1000


# ~~~~~~~~~~~~~~~~~
# LISTAS GLOBAIS
# ~~~~~~~~~~~~~~~~~

MERCHS_IN_PLAY = []
EXPLOSION_PARTICLES = []

auditoria = {
    "dv": {}
}


# ~~~~~~~~~~~~~~~~~
# CLASSES
# ~~~~~~~~~~~~~~~~~

@dataclass
class Merch: # Itens Coletáveis
    x: int
    y: int
    points: int

    def get_color(self):
        colors = {
            10: pyxel.COLOR_CYAN,
            20: pyxel.COLOR_LIME,
            40: pyxel.COLOR_PINK,
            80: pyxel.COLOR_PEACH,
            -10: pyxel.COLOR_DARK_BLUE,
            -30: pyxel.COLOR_ORANGE,
            -50: pyxel.COLOR_RED
        }

        return colors.get(self.points, pyxel.COLOR_WHITE)


@dataclass
class Ship:
    x: float
    y: float

    rotation: float = 0.0
    rotation_dir: int = 0

    acceleration: float = 0.0

    exploded: bool = False

    points: int = 0
    lives: int = 5

    vx: float = 0.0
    vy: float = 0.0

    explosion_timer: int = 0
    invincible_timer: int = 0

    combo: int = 1
    combo_timer: int = 0
    combo_text_timer: int = 0

    difficulty: float = 1.0
    gravity_strength: float = GRAVITY_STRENGTH


@dataclass
class Particle:
    x: float
    y: float

    vx: float
    vy: float

    life: int
    color: int


# ~~~~~~~~~~~~~~~~~
# FUNÇÕES DA EXPLOSÃO
# ~~~~~~~~~~~~~~~~~

def spawn_explosion(x, y):
    EXPLOSION_PARTICLES.clear()

    colors = [
        pyxel.COLOR_RED,
        pyxel.COLOR_ORANGE,
        pyxel.COLOR_YELLOW,
        pyxel.COLOR_WHITE
    ]

    for _ in range(24):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(0.5, 3.0)

        particle = Particle(
            x=x,
            y=y,
            vx=math.cos(angle) * speed,
            vy=math.sin(angle) * speed,
            life=random.randint(15, EXPLOSION_DURATION),
            color=random.choice(colors)
        )

        EXPLOSION_PARTICLES.append(particle)


def update_particles():
    for particle in EXPLOSION_PARTICLES:
        particle.x += particle.vx
        particle.y += particle.vy

        particle.vx *= 0.95
        particle.vy *= 0.95

        particle.life -= 1

    EXPLOSION_PARTICLES[:] = [
        particle
        for particle in EXPLOSION_PARTICLES
        if particle.life > 0
    ]


# ~~~~~~~~~~~~~~~~~
# CORAÇÕES DAS VIDAS
# ~~~~~~~~~~~~~~~~~

HEART_MASK = [
    [0, 1, 1, 0, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0]
]


def draw_heart(x, y, color):
    for row_index, row in enumerate(HEART_MASK):
        for column_index, value in enumerate(row):
            if value == 1:
                pyxel.pset(
                    x + column_index,
                    y + row_index,
                    color
                )


def draw_lives(lives):
    for index in range(lives):
        heart_x = SCREEN_WIDTH - 8 - 9 * (index + 1)

        draw_heart(
            heart_x,
            5,
            pyxel.COLOR_RED
        )


# ~~~~~~~~~~~~~~~~~
# CONTROLE DA NAVE
# ~~~~~~~~~~~~~~~~~

def rotate_ship(ship):
    if ship.rotation_dir != 0:
        ship.rotation += ship.rotation_dir * ROTATION_SPEED


def set_acceleration(ship, magnitude):
    ship.acceleration += magnitude

    ship.acceleration = max(
        0.0,
        min(MAX_ACCELERATION, ship.acceleration)
    )


def apply_gravity(ship):
    dx = STAR_POSITION["x"] - ship.x
    dy = STAR_POSITION["y"] - ship.y

    real_distance = math.hypot(dx, dy)

    distance = max(
        real_distance,
        GRAVITY_MIN_DIST
    )

    force = ship.gravity_strength / (distance * distance)

    ship.vx += (dx / distance) * force
    ship.vy += (dy / distance) * force


def move_ship(ship):
    direction_vector = {
        "x": math.cos(ship.rotation),
        "y": math.sin(ship.rotation)
    }

    auditoria["dv"] = direction_vector

    ship.vx += (
        direction_vector["x"]
        * ship.acceleration
        * ACCELERATION_DELTA
    )

    ship.vy += (
        direction_vector["y"]
        * ship.acceleration
        * ACCELERATION_DELTA
    )

    # Atrito da nave
    ship.vx *= FRICTION
    ship.vy *= FRICTION

    speed = math.hypot(ship.vx, ship.vy)

    if speed > TOP_SPEED:
        ship.vx = (ship.vx / speed) * TOP_SPEED
        ship.vy = (ship.vy / speed) * TOP_SPEED

    # A nave reaparece no lado oposto da tela
    ship.x = (ship.x + ship.vx) % SCREEN_WIDTH
    ship.y = (ship.y + ship.vy) % SCREEN_HEIGHT


# ~~~~~~~~~~~~~~~~~
# COLISÃO COM A ESTRELA
# ~~~~~~~~~~~~~~~~~

def distance_to_star(ship):
    dx = ship.x - STAR_POSITION["x"]
    dy = ship.y - STAR_POSITION["y"]

    return math.hypot(dx, dy)


def check_star_collision(ship):
    distance = distance_to_star(ship)

    collision_distance = (
        STAR_RADIUS
        + SHIP_RADIUS
        + COLLISION_MARGIN
    )

    inside_star = distance < collision_distance

    if ship.invincible_timer > 0:
        ship.invincible_timer -= 1

        # Enquanto a nave ainda estiver sobre a estrela,
        # mantém alguns frames de invencibilidade.
        if inside_star:
            ship.invincible_timer = max(
                ship.invincible_timer,
                10
            )

        return False

    return inside_star


# ~~~~~~~~~~~~~~~~~
# RESPAWN DA NAVE
# ~~~~~~~~~~~~~~~~~

def respawn_ship(ship):
    ship.x = SHIP_START_X
    ship.y = SHIP_START_Y

    ship.vx = 0.0
    ship.vy = 0.0

    ship.rotation = 0.0
    ship.rotation_dir = 0

    ship.acceleration = 0.0

    ship.exploded = False
    ship.explosion_timer = 0

    ship.invincible_timer = INVINCIBLE_DURATION

    ship.gravity_strength = GRAVITY_STRENGTH
    ship.difficulty = 1.0

    ship.combo = 1
    ship.combo_timer = 0
    ship.combo_text_timer = 0

    EXPLOSION_PARTICLES.clear()


# ~~~~~~~~~~~~~~~~~
# GERAÇÃO DOS ITENS
# ~~~~~~~~~~~~~~~~~

def select_points():
    total_weight = sum(WEIGHTS)

    random_number = random.randint(
        1,
        total_weight
    )

    cursor = 0

    for index in range(len(WEIGHTS)):
        cursor += WEIGHTS[index]

        if cursor >= random_number:
            return POINTS[index], WEIGHTS[index]

    return -10, 15


def random_scrap_position():
    while True:
        x = random.randint(
            MERCH_RADIUS + 2,
            SCREEN_WIDTH - MERCH_RADIUS - 3
        )

        y = random.randint(
            MERCH_RADIUS + 2,
            SCREEN_HEIGHT - MERCH_RADIUS - 3
        )

        distance_from_star = math.hypot(
            x - STAR_POSITION["x"],
            y - STAR_POSITION["y"]
        )

        # Impede que um item nasça dentro da estrela
        if distance_from_star > STAR_RADIUS + 10:
            return x, y


def spawn_one_scrap(exclude_points=None):
    while True:
        points, weight = select_points()

        if points != exclude_points:
            break

    x, y = random_scrap_position()

    MERCHS_IN_PLAY.append(
        Merch(
            x=x,
            y=y,
            points=points
        )
    )


def spawn_scrap():
    budget = WEIGHT_BUDGET

    while budget > 0:
        points, weight = select_points()

        x, y = random_scrap_position()

        MERCHS_IN_PLAY.append(
            Merch(
                x=x,
                y=y,
                points=points
            )
        )

        budget -= weight


# ~~~~~~~~~~~~~~~~~
# COLISÃO COM OS ITENS
# ~~~~~~~~~~~~~~~~~

def check_scrap_collision(ship):
    if ship.exploded:
        return

    collected_scraps = []

    for scrap in MERCHS_IN_PLAY:
        distance = math.hypot(
            ship.x - scrap.x,
            ship.y - scrap.y
        )

        if distance < SHIP_RADIUS + MERCH_RADIUS + 2:
            collected_scraps.append(scrap)

    for scrap in collected_scraps:

        if scrap.points > 0:
            # Primeiro aplica o combo atual.
            ship.points += scrap.points * ship.combo

            # Depois aumenta o combo para o próximo item.
            ship.combo = min(
                ship.combo + 1,
                MAX_COMBO
            )

            ship.combo_timer = COMBO_TIME
            ship.combo_text_timer = 40

        else:
            ship.points += scrap.points

            ship.combo = 1
            ship.combo_timer = 0
            ship.combo_text_timer = 40

        MERCHS_IN_PLAY.remove(scrap)

        spawn_one_scrap(
            exclude_points=scrap.points
        )


# ~~~~~~~~~~~~~~~~~
# DIFICULDADE
# ~~~~~~~~~~~~~~~~~

def update_difficulty(ship):
    calculated_difficulty = 1 + ship.points / 500

    ship.difficulty = max(
        1.0,
        min(3.0, calculated_difficulty)
    )

    ship.gravity_strength = (
        GRAVITY_STRENGTH
        * ship.difficulty
    )


# ~~~~~~~~~~~~~~~~~
# CLASSE PRINCIPAL DO JOGO
# ~~~~~~~~~~~~~~~~~

class App:

    def __init__(self):
        if not RESOURCE_PATH.exists():
            raise FileNotFoundError(
                "\nO arquivo de recursos não foi encontrado.\n"
                f"Coloque o arquivo 'my_resource.pyxres' em:\n"
                f"{RESOURCE_PATH.parent}\n"
            )

        self.c_needle = Ship(
            SHIP_START_X,
            SHIP_START_Y
        )

        self.game_over = False

        pyxel.init(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            title="Jogo da Nave"
        )

        pyxel.load(str(RESOURCE_PATH))

        spawn_scrap()

        pyxel.run(
            self.update,
            self.draw
        )

    def restart_game(self):
        self.c_needle = Ship(
            SHIP_START_X,
            SHIP_START_Y
        )

        MERCHS_IN_PLAY.clear()
        EXPLOSION_PARTICLES.clear()

        spawn_scrap()

        self.game_over = False

    def processa_teclado(self):
        needle = self.c_needle

        if needle.exploded:
            return

        update_difficulty(needle)

        # Controle do timer do combo
        if needle.combo_timer > 0:
            needle.combo_timer -= 1

            if needle.combo_timer == 0:
                needle.combo = 1

        # Controle do texto do combo
        if needle.combo_text_timer > 0:
            needle.combo_text_timer -= 1

        # Aceleração
        if pyxel.btn(pyxel.KEY_W):
            set_acceleration(
                needle,
                ACCEL_RAMP_UP
            )

        elif pyxel.btn(pyxel.KEY_S):
            set_acceleration(
                needle,
                -ACCEL_BRAKE
            )

        else:
            set_acceleration(
                needle,
                -ACCEL_RAMP_DOWN
            )

        # Rotação
        pressing_left = pyxel.btn(pyxel.KEY_A)
        pressing_right = pyxel.btn(pyxel.KEY_D)

        if pressing_left and not pressing_right:
            needle.rotation_dir = -1

        elif pressing_right and not pressing_left:
            needle.rotation_dir = 1

        else:
            needle.rotation_dir = 0

    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_R):
                self.restart_game()

            return

        needle = self.c_needle

        # Atualização da explosão
        if needle.explosion_timer > 0:
            needle.explosion_timer -= 1

            update_particles()

            if needle.explosion_timer == 0:
                EXPLOSION_PARTICLES.clear()

                if needle.lives > 0:
                    respawn_ship(needle)

                else:
                    self.game_over = True

            return

        self.processa_teclado()

        rotate_ship(needle)
        apply_gravity(needle)
        move_ship(needle)

        check_scrap_collision(needle)

        if check_star_collision(needle):
            needle.lives -= 1
            needle.exploded = True
            needle.explosion_timer = EXPLOSION_DURATION

            spawn_explosion(
                needle.x,
                needle.y
            )

    def draw(self):
        pyxel.cls(pyxel.COLOR_BLACK)

        needle = self.c_needle

        if self.game_over:
            pyxel.text(
                SCREEN_WIDTH // 2 - 24,
                SCREEN_HEIGHT // 2 - 20,
                "GAME OVER",
                pyxel.COLOR_RED
            )

            pyxel.text(
                SCREEN_WIDTH // 2 - 40,
                SCREEN_HEIGHT // 2,
                f"Pontuacao final: {needle.points}",
                pyxel.COLOR_WHITE
            )

            pyxel.text(
                SCREEN_WIDTH // 2 - 48,
                SCREEN_HEIGHT // 2 + 12,
                "Pressione R para reiniciar",
                pyxel.COLOR_YELLOW
            )

            return

        # Desenha a estrela centralizada
        pyxel.blt(
            STAR_POSITION["x"] - 8,
            STAR_POSITION["y"] - 8,
            0,
            24,
            0,
            16,
            16,
            colkey=0,
            scale=STAR_SCALE
        )

        # Desenha as partículas da explosão
        for particle in EXPLOSION_PARTICLES:
            pyxel.pset(
                int(particle.x),
                int(particle.y),
                particle.color
            )

        # Desenha a nave
        if not needle.exploded:

            should_draw_ship = (
                needle.invincible_timer == 0
                or (needle.invincible_timer // 4) % 2 == 0
            )

            if should_draw_ship:
                pyxel.blt(
                    int(needle.x - 8),
                    int(needle.y - 8),
                    0,
                    8,
                    8,
                    16,
                    16,
                    colkey=0,
                    rotate=math.degrees(
                        needle.rotation
                    ) + 90,
                    scale=SHIP_SCALE
                )

        # Desenha os itens
        for scrap in MERCHS_IN_PLAY:
            pyxel.circ(
                scrap.x,
                scrap.y,
                MERCH_RADIUS,
                scrap.get_color()
            )

        # Informações da partida
        pyxel.text(
            10,
            5,
            f"Pontos: {needle.points}",
            pyxel.COLOR_WHITE
        )

        pyxel.text(
            10,
            13,
            f"Combo: x{needle.combo}",
            pyxel.COLOR_YELLOW
        )

        pyxel.text(
            10,
            36,
            f"Dificuldade: {needle.difficulty:.1f}x",
            pyxel.COLOR_ORANGE
        )

        draw_lives(needle.lives)

        # Texto do combo
        if needle.combo_text_timer > 0:

            if needle.combo > 1:
                pyxel.text(
                    115,
                    20,
                    f"COMBO x{needle.combo}",
                    pyxel.COLOR_LIME
                )

            else:
                pyxel.text(
                    110,
                    20,
                    "COMBO QUEBRADO",
                    pyxel.COLOR_RED
                )

        # Texto de invencibilidade
        if needle.invincible_timer > 0:
            pyxel.text(
                10,
                44,
                "INVENCIVEL!",
                pyxel.COLOR_YELLOW
            )


# ~~~~~~~~~~~~~~~~~
# INÍCIO DO JOGO
# ~~~~~~~~~~~~~~~~~

if __name__ == "__main__":
    App()