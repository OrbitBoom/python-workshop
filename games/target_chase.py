import turtle
import math
import random

# set up the screen
window = turtle.Screen()
window.bgcolor("black")
window.setup(660, 690)
window.title("Target Chase | Left/right to steer, up to accelerate, down to brake")
window.tracer(0)


# register shapes


# Draw border
border_pen = turtle.Turtle()
border_pen.pencolor("white")
border_pen.penup()
border_pen.setposition(-300, -300)
border_pen.pendown()
border_pen.pensize(3)
for side in range(4):
    border_pen.forward(600)
    border_pen.left(90)
border_pen.hideturtle()

score_pen = turtle.Turtle()
score_pen.pencolor("white")
score_pen.penup()
score_pen.setposition(-280, 300)
score_pen.write("Score: 0", font=("courier", 14))


# create the bot
bot = turtle.Turtle()
bot.color("yellow")
bot.shape("triangle")
bot.penup()
bot.speed(0)

# score
score = 0

# Create my goals

maxgoals = 25
goals = []


for count in range(maxgoals):
    goals.append(turtle.Turtle())
    goals[count].color("red")
    goals[count].shape("circle")
    goals[count].speed(0)
    goals[count].penup()
    goals[count].setposition(random.randint(-290, 290), random.randint(-290, 290))

# set up the speed
speed = 8


# Define the functions
def turn_left():
    bot.left(30)


def turn_right():
    bot.right(30)


def increase_speed():
    global speed
    speed = min(16, speed + 1.5)


def stop():
    global speed
    speed = 5


def is_collision(t1, t2):
    d = math.sqrt(
        math.pow(t1.xcor() - t2.xcor(), 2) + math.pow(t1.ycor() - t2.ycor(), 2)
    )
    if d < 20:
        return True
    else:
        return False


# keyboard binds
turtle.listen()
turtle.onkey(turn_left, "Left")
turtle.onkey(turn_right, "Right")
turtle.onkey(increase_speed, "Up")
turtle.onkey(stop, "Down")

# win turtle
win_pen = turtle.Turtle()
win_pen.pencolor("lightblue")
win_pen.penup()
win_pen.setposition(-150, 0)
win_pen.ht()

# MAIN GAME


def tick():
    global score

    bot.forward(speed)

    if abs(bot.xcor()) > 290:
        bot.setx(max(-290, min(290, bot.xcor())))
        bot.setheading(180 - bot.heading())
    if abs(bot.ycor()) > 290:
        bot.sety(max(-290, min(290, bot.ycor())))
        bot.setheading(-bot.heading())

    # Move the goal
    for goal in goals[:]:
        goal.forward(1)

        # Boundry Check
        if goal.xcor() > 290 or goal.xcor() < -290:
            goal.right(180)

        if goal.ycor() > 290 or goal.ycor() < -290:
            goal.right(180)

        # collision check

        if is_collision(bot, goal):
            goal.hideturtle()
            goals.remove(goal)
            score += 1
            # draw the score on my screen

            score_pen.clear()
            score_pen.penup()
            score_pen.hideturtle()
            score_pen.setposition(-280, 310)
            scorestring = "Score: %s" % score
            score_pen.write(scorestring, False, align="left", font=("courier", 14))

    if not goals:
        win_pen.write("YOU WIN", font=("courier", 60, "bold"))
    else:
        window.ontimer(tick, 30)
    window.update()


tick()
window.mainloop()
