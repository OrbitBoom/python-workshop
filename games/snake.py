import turtle
import time
import random

delay = 0.1

score = 0
high_score = 0

# set up the screen
wn = turtle.Screen()
wn.title("Snake")
wn.bgcolor("green")
wn.setup(width=600, height=600)
wn.tracer(0)

# Snake head
head = turtle.Turtle()
head.speed(0)
head.shape("square")
head.color("black")
head.penup()
head.goto(0, 0)
head.direction = "stop"

# Snake food
food = turtle.Turtle()
food.speed(0)
food.shape("circle")
food.color("red")
food.penup()
food.goto(0, 100)

segments = []

pen = turtle.Turtle()
pen.speed(0)
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0, 260)
pen.write("Score: 0 High Score: 0", align="center", font=("courier", 24))


# Functions
def go_up():
    if head.direction != "down":
        head.direction = "up"


def go_down():
    if head.direction != "up":
        head.direction = "down"


def go_right():
    if head.direction != "left":
        head.direction = "right"


def go_left():
    if head.direction != "right":
        head.direction = "left"


def move():
    if head.direction == "up":
        y = head.ycor()
        head.sety(y + 20)
    if head.direction == "down":
        y = head.ycor()
        head.sety(y - 20)
    if head.direction == "left":
        x = head.xcor()
        head.setx(x - 20)
    if head.direction == "right":
        x = head.xcor()
        head.setx(x + 20)


# keybinds
wn.listen()
wn.onkey(go_up, "w")
wn.onkey(go_down, "s")
wn.onkey(go_left, "a")
wn.onkey(go_right, "d")


def status():
    pen.clear()
    pen.write(
        f"Score: {score}   High score: {high_score}",
        align="center",
        font=("Courier", 20),
    )


def reset():
    global score
    for segment in segments:
        segment.hideturtle()
    spare.extend(segments)
    segments.clear()
    head.goto(0, 0)
    head.direction = "stop"
    score = 0
    status()


def tick():
    global score, high_score
    if head.direction != "stop":
        previous = head.position()
        move()
        ate = head.distance(food) < 1
        for segment in segments:
            old = segment.position()
            segment.goto(previous)
            previous = old
        if ate:
            segment = spare.pop() if spare else turtle.Turtle("square")
            segment.penup()
            segment.color("grey")
            segment.goto(previous)
            segment.showturtle()
            segments.append(segment)
            score += 10
            high_score = max(score, high_score)
            status()
            occupied = {tuple(s.position()) for s in [head, *segments]}
            available = [
                (x, y)
                for x in range(-280, 281, 20)
                for y in range(-280, 281, 20)
                if (x, y) not in occupied
            ]
            if available:
                food.goto(random.choice(available))
            else:
                reset()
        if max(abs(head.xcor()), abs(head.ycor())) > 280 or any(
            head.distance(s) < 1 for s in segments
        ):
            reset()
    wn.update()
    wn.ontimer(tick, 100)


spare = []
tick()
wn.mainloop()
