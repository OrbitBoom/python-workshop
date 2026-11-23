"""Steer with the arrows and fire with Space. Hit red enemies, spare blue allies."""

import random
import turtle

wn = turtle.Screen()
wn.setup(680, 700)
wn.title("Space War | Arrows to steer and change speed | Space to fire")
wn.bgcolor("black")
wn.tracer(0)


class Sprite(turtle.Turtle):
    def __init__(self, spriteshape, color, startx, starty):
        turtle.Turtle.__init__(self, shape=spriteshape)
        self.speed(0)
        self.penup()
        self.color(color)
        self.fd(0)
        self.goto(startx, starty)
        self.velocity = 1

    def move(self):
        self.fd(self.velocity)

        if self.xcor() > 290:
            self.setx(290)
            self.rt(100)
        if self.xcor() < -290:
            self.setx(-290)
            self.rt(60)
        if self.ycor() > 290:
            self.sety(290)
            self.rt(60)
        if self.ycor() < -290:
            self.sety(-290)
            self.rt(60)

    def is_collision(self, other):
        if (
            (self.xcor() >= (other.xcor() - 20))
            and (self.xcor() <= (other.xcor() + 20))
            and (self.ycor() >= (other.ycor() - 20))
            and (self.ycor() <= (other.ycor() + 20))
        ):
            return True
        else:
            return False


class Player(Sprite):
    def __init__(self, spriteshape, color, startx, starty):
        Sprite.__init__(self, spriteshape, color, startx, starty)
        self.shapesize(stretch_wid=0.6, stretch_len=1.1, outline=None)
        self.velocity = 2

    def turn_left(self):
        self.lt(25)

    def turn_right(self):
        self.rt(25)

    def accelerate(self):
        self.velocity = min(8, self.velocity + 0.5)

    def decelerate(self):
        self.velocity = max(0, self.velocity - 0.5)


class Enemy(Sprite):
    def __init__(self, spriteshape, color, startx, starty):
        Sprite.__init__(self, spriteshape, color, startx, starty)
        self.velocity = 1.8
        self.setheading(random.randint(0, 360))


class Ally(Sprite):
    def __init__(self, spriteshape, color, startx, starty):
        Sprite.__init__(self, spriteshape, color, startx, starty)
        self.velocity = 1.5
        self.setheading(random.randint(0, 360))


class Missile(Sprite):
    def __init__(self, spriteshape, color, startx, starty):
        Sprite.__init__(self, spriteshape, color, startx, starty)
        self.shapesize(stretch_wid=0.2, stretch_len=0.4, outline=None)
        self.velocity = 10
        self.status = "ready"
        self.goto(-1000, 1000)

    def fire(self):
        if self.status == "ready" and game.lives:
            self.goto(player.xcor(), player.ycor())
            self.setheading(player.heading())
            self.status = "firing"

    def move(self):
        if self.status == "ready":
            self.goto(-1000, 1000)

        if self.status == "firing":
            self.fd(self.velocity)

        if (
            self.xcor() < -290
            or self.xcor() > 290
            or self.ycor() < -290
            or self.ycor() > 290
        ):
            self.goto(-1000, 1000)
            self.status = "ready"


class Particle(Sprite):
    def __init__(self, spriteshape, color, startx, starty):
        Sprite.__init__(self, spriteshape, color, startx, starty)
        self.shapesize(stretch_wid=0.1, stretch_len=0.1, outline=None)
        self.goto(-1000, -1000)
        self.frame = 0

    def explode(self, startx, starty):
        self.goto(startx, starty)
        self.setheading(random.randint(0, 360))
        self.frame = 1

    def move(self):
        if self.frame > 0:
            self.fd(10)
            self.frame += 1

        if self.frame > 15:
            self.frame = 0
            self.goto(-1000, -1000)


class Game:
    def __init__(self):
        self.score = 0
        self.pen = turtle.Turtle()
        self.hud = turtle.Turtle(visible=False)
        self.hud.penup()
        self.hud.color("white")
        self.lives = 3

    def draw_border(self):
        self.pen.speed(0)
        self.pen.color("white")
        self.pen.pensize(4)
        self.pen.penup()
        self.pen.goto(-300, 300)
        self.pen.pendown()
        for side in range(4):
            self.pen.fd(600)
            self.pen.rt(90)
        self.pen.penup()
        self.pen.ht()
        self.pen.pendown()

    def show_status(self):
        self.hud.clear()
        msg = f"Score: {self.score}    Lives: {self.lives}"
        self.pen.penup()
        self.hud.goto(-300, 310)
        self.hud.write(msg, font=("courier", 16, "normal"))


game = Game()
game.draw_border()
game.show_status()

player = Player("triangle", "white", 0, 0)

missile = Missile("triangle", "yellow", 0, 0)


enemies = []
for i in range(6):
    enemies.append(Enemy("circle", "red", -100, 0))

allies = []
for i in range(6):
    allies.append(Ally("square", "blue", 100, 0))

particles = []
for i in range(20):
    particles.append(Particle("circle", "orange", 0, 0))
# keybinds
turtle.listen()
turtle.onkey(player.turn_left, "Left")
turtle.onkey(player.turn_right, "Right")
turtle.onkey(player.accelerate, "Up")
turtle.onkey(player.decelerate, "Down")
turtle.onkey(missile.fire, "space")


def tick():
    player.move()
    missile.move()

    for enemy in enemies:
        enemy.move()
        if player.is_collision(enemy):
            x = random.randint(-250, 250)
            y = random.randint(-250, 250)
            enemy.goto(x, y)
            game.lives -= 1
            game.score -= 100
            game.show_status()
            if game.lives == 0:
                game.hud.goto(0, 0)
                game.hud.write(
                    "Game over · press R to replay",
                    align="center",
                    font=("Courier", 20),
                )
                wn.update()
                return
        if missile.status == "firing" and missile.is_collision(enemy):
            x = random.randint(-250, 250)
            y = random.randint(-250, 250)
            enemy.goto(x, y)
            missile.status = "ready"
            game.score += 100
            game.show_status()
            for particle in particles:
                particle.explode(missile.xcor(), missile.ycor())

    for ally in allies:
        ally.move()
        if missile.status == "firing" and missile.is_collision(ally):
            x = random.randint(-250, 250)
            y = random.randint(-250, 250)
            ally.goto(x, y)
            missile.status = "ready"
            game.score -= 50
            game.show_status()

    for particle in particles:
        particle.move()
    wn.update()
    wn.ontimer(tick, 16)


def restart():
    if game.lives:
        return
    game.lives, game.score = 3, 0
    game.show_status()
    player.goto(0, 0)
    player.setheading(0)
    player.velocity = 2
    missile.status = "ready"
    for sprite in enemies + allies:
        sprite.goto(random.choice((-170, 170)), random.randint(-250, 250))
    tick()


wn.onkey(restart, "r")
tick()
wn.mainloop()
