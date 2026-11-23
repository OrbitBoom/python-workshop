import turtle


wn = turtle.Screen()
wn.bgcolor("black")
wn.title("Space invaders")
wn.setup(660, 680)
wn.tracer(0)

bot_pen = turtle.Turtle()
bot_pen.speed(0)
bot_pen.color("white")
bot_pen.penup()
bot_pen.setposition(-300, -300)
bot_pen.pendown()
bot_pen.pensize(3)

for side in range(4):
    bot_pen.fd(600)
    bot_pen.lt(90)
bot_pen.hideturtle()

score = 0

score_pen = turtle.Turtle()
score_pen.speed(0)
score_pen.color("white")
score_pen.penup()
score_pen.setposition(-290, 270)
scorestring = "Score: %s" % score
score_pen.write(scorestring, False, align="left", font=("Arial", 14))
score_pen.hideturtle()

# create the player turtle
bot = turtle.Turtle()
bot.color("blue")
bot.shape("triangle")
bot.penup()
bot.speed(0)
bot.setposition(0, -250)
bot.setheading(90)

botspeed = 0


enemyspeed = 2

number_of_enemies = 30
enemies = []

for i in range(number_of_enemies):
    enemies.append(turtle.Turtle())

enemy_start_x = -225
enemy_start_y = 250
enemy_number = 0


for enemy in enemies:
    enemy.color("red")
    enemy.shape("circle")
    enemy.penup()
    enemy.speed(0)
    x = enemy_start_x + (50 * enemy_number)
    y = enemy_start_y
    enemy.setposition(x, y)

    enemy_number += 1
    if enemy_number == 10:
        enemy_start_y -= 50
        enemy_number = 0


# create the player weapon

bullet = turtle.Turtle()
bullet.color("yellow")
bullet.shape("triangle")
bullet.penup()
bullet.speed(0)
bullet.setheading(90)
bullet.shapesize(0.5, 0.5)
bullet.hideturtle()

bulletspeed = 15

# define the bullet state
# ready - to fire
# fire - firing
bulletstate = "ready"
# move the bot left and right


def move_left():
    global botspeed
    botspeed = -4


def move_right():
    global botspeed
    botspeed = 4


def firebullet():
    global bulletstate
    if bulletstate == "ready":
        bulletstate = "fire"
        x = bot.xcor()
        y = bot.ycor() + 10
        bullet.setposition(x, y)
        bullet.showturtle()


def isCollision(t1, t2):
    return t1.distance(t2) < 15


# Create keybinds for the bot

wn.listen()
wn.onkey(move_left, "Left")
wn.onkey(move_right, "Right")
wn.onkey(firebullet, "space")

# main game loop


def finish(message):
    score_pen.goto(0, 0)
    score_pen.write(message, align="center", font=("Courier", 28, "bold"))
    wn.update()


def tick():
    global enemyspeed, bulletstate, score
    bot.setx(max(-270, min(270, bot.xcor() + botspeed)))
    if any(abs(enemy.xcor() + enemyspeed) > 280 for enemy in enemies):
        enemyspeed *= -1
        for enemy in enemies:
            enemy.sety(enemy.ycor() - 25)
    if bulletstate == "fire":
        bullet.forward(bulletspeed)
        if bullet.ycor() > 280:
            bullet.hideturtle()
            bulletstate = "ready"
    for enemy in enemies[:]:
        enemy.setx(enemy.xcor() + enemyspeed)
        if bulletstate == "fire" and isCollision(bullet, enemy):
            enemies.remove(enemy)
            enemy.hideturtle()
            bullet.hideturtle()
            bulletstate = "ready"
            score += 10
            score_pen.clear()
            score_pen.write(f"Score: {score}", font=("Arial", 14))
        elif enemy.ycor() <= -250 or isCollision(bot, enemy):
            return finish("Invasion complete")
    if not enemies:
        return finish("Earth defended!")
    wn.update()
    wn.ontimer(tick, 16)


tick()
wn.mainloop()
