import random
import tkinter as tk
from tkinter import ttk

# Each row starts with the question and its correct answer.
QUESTIONS = [
    ("What is the capital of India?", "New Delhi", "Chennai", "Mumbai", "Kolkata"),
    ("What is 1 + (−2)?", "−1", "1", "0", "−2"),
    (
        "Which ancient wonder is in Egypt?",
        "Great Pyramid of Giza",
        "Colosseum",
        "Taj Mahal",
        "Petra",
    ),
    ("How many faces does a cube have?", "6", "4", "8", "12"),
    ("Which Python type stores key–value pairs?", "dict", "list", "tuple", "set"),
    ("How many bits are in a byte?", "8", "2", "4", "16"),
    ("Which colour combines red and blue light?", "Magenta", "Yellow", "Cyan", "Green"),
    (
        "What number follows 1, 1, 2, 3, 5 in the Fibonacci sequence?",
        "8",
        "7",
        "9",
        "10",
    ),
]


def main():
    root = tk.Tk()
    root.title("Quizstar")
    panel = ttk.Frame(root, padding=20)
    panel.pack()
    questions = []
    score = 0

    def start():
        nonlocal score
        questions[:] = random.sample(QUESTIONS, 5)
        score = 0
        show()

    def show():
        for widget in panel.winfo_children():
            widget.destroy()
        if not questions:
            ttk.Label(panel, text=f"Final score: {score} / 25").pack()
            ttk.Button(panel, text="Play again", command=start).pack()
            return
        question, correct, *others = questions.pop()
        ttk.Label(
            panel, text=f"Question {5-len(questions)} of 5 · {score} points"
        ).pack()
        ttk.Label(panel, text=question, wraplength=380).pack(pady=8)

        def choose(value):
            nonlocal score
            if value == correct:
                score += 5
            show()

        options = [correct, *others]
        random.shuffle(options)
        for value in options:
            ttk.Button(panel, text=value, command=lambda v=value: choose(v)).pack(
                fill="x"
            )

    start()
    root.mainloop()


if __name__ == "__main__":
    main()
