import sys

import pygame as pg

WINDOW_SIZE = [1200, 800]

ABSOLUTE_GRAVITY = 0.6

colors = {
    "gray": [100, 100, 100],
    "white": [255, 255, 255],
    "black": [0, 0, 0],
    'light_pink': [252, 204, 204],
    'light_blue': [204, 206, 252]
}


def invertWorld():
    global colors, ABSOLUTE_GRAVITY
    for i in colors:
        array = colors[i]
        array[0] = 255 - array[0]
        array[1] = 255 - array[1]
        array[2] = 255 - array[2]

    ABSOLUTE_GRAVITY *= -1


class PhysicsBody:
    def __init__(self, x, y, mass):
        self.gravity = ABSOLUTE_GRAVITY
        self.x = x
        self.y = y
        self.mass = mass
        self.NewtonForce = self.gravity * self.mass

        self.slowCoefficient = 1

        self.Velocity2D = [0, 0]
        self.needReplace = False


class Circle(PhysicsBody):
    def __init__(self, x, y, mass, radius):
        super().__init__(x, y, mass)
        self.radius = radius

    def draw(self, screen):
        pg.draw.circle(screen, colors['black'], (self.x, self.y), self.radius)

    def update(self, screen):
        self.move()
        self.draw(screen)

    def velocityYCalculation(self):
        self.Velocity2D[1] += self.gravity

    def move(self):
        self.velocityYCalculation()
        self.y += (self.Velocity2D[1] * self.slowCoefficient)

        if self.y - self.radius + 20 >= WINDOW_SIZE[1]:
            self.needDelete = True


class Floor:
    def __init__(self):
        self.enabled = False
        self.y = WINDOW_SIZE[1]

        self.EnergyConsumeCoefficient = 0.1

    def setFloor(self, status):
        self.enabled = status

    def checkCollisions(self, el: Circle):
        if self.y <= el.y + el.radius:
            el.Velocity2D[1] *= -(1 - self.EnergyConsumeCoefficient)
            if abs(el.Velocity2D[1]) <= 0.4:
                el.Velocity2D[1] = 0

            if el.y + el.radius >= WINDOW_SIZE[1]:
                el.y = WINDOW_SIZE[1] - el.radius

        if 0 >= el.y - el.radius:
            el.Velocity2D[1] *= -(1 - self.EnergyConsumeCoefficient)
            if abs(el.Velocity2D[1]) <= 0.4:
                el.Velocity2D[1] = 0

            if el.y - el.radius < 0:
                el.y = el.radius


class GravityResonator:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.reversed = 1
        
    def draw(self, screen):
        if self.reversed < 0:
            pg.draw.circle(screen, colors['light_blue'], (self.x, self.y), self.radius)
        else:
            pg.draw.circle(screen, colors['light_pink'], (self.x, self.y), self.radius)
        pg.draw.circle(screen, colors['gray'], (self.x, self.y), 20)
        pg.draw.circle(screen, colors['gray'], (self.x, self.y), self.radius, 1)

    def update(self, screen):
        self.draw(screen)

    def checkInteractions(self, el: Circle):
        distance = ((el.x - self.x) ** 2 + (el.y - self.y) ** 2) ** 0.5
        if self.radius >= distance - el.radius:
            decreaseCoefficient = self.reversed * (self.radius - distance) / (self.radius+1)
            el.slowCoefficient = (1 - decreaseCoefficient) ** 8
            el.gravity = ABSOLUTE_GRAVITY * (1 - decreaseCoefficient) ** 8
        else:
            el.gravity = ABSOLUTE_GRAVITY


class Game:
    def __init__(self):
        self.window = pg.display.set_mode((WINDOW_SIZE[0], WINDOW_SIZE[1]))
        self.running = True
        self.FPS = 60

        self.Floor = Floor()
        self.Floor.setFloor(True)

        self.Clock = pg.time.Clock()

    def run(self):
        array = []
        GR = GravityResonator(400, 400, 200)
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    sys.exit()
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_pos = pg.mouse.get_pos()
                    array.append(Circle(mouse_pos[0], mouse_pos[1], 1, 20))

                if event.type == pg.KEYDOWN:
                    keys = pg.key.get_pressed()
                    if keys[pg.K_o]:
                        invertWorld()
                    if keys[pg.K_i]:
                        GR.reversed = -GR.reversed

            keys = pg.key.get_pressed()
            if keys[pg.K_LEFT]:
                GR.radius -= 2
            if keys[pg.K_RIGHT]:
                GR.radius += 2

            if keys[pg.K_a]:
                GR.x -= 4
            if keys[pg.K_d]:
                GR.x += 4
            if keys[pg.K_w]:
                GR.y -= 4
            if keys[pg.K_s]:
                GR.y += 4

            self.window.fill(colors['white'])
            GR.update(self.window)
            for i in array:
                i.update(self.window)
                self.Floor.checkCollisions(i)
                GR.checkInteractions(i)
                if i.needReplace:
                    i.y = WINDOW_SIZE[1] - i.radius
            pg.display.update()
            self.Clock.tick(self.FPS)


app = Game()
app.run()
