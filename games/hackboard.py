"""Guess the components of a colour, or recover the missing number in an XOR puzzle."""

import random
import tkinter as tk
from tkinter import ttk

MODES = ("Hexadecimal", "Binary", "Decimal", "Symmetric XOR")


def main():
    root = tk.Tk()
    root.title("Hackboard")
    panel = ttk.Frame(root, padding=18)
    panel.pack()
    mode = ttk.Combobox(panel, values=MODES, state="readonly")
    mode.current(0)
    mode.pack()
    difficulty = ttk.Combobox(
        panel, values=("Easy", "Medium", "Hard"), state="readonly"
    )
    difficulty.current(0)
    difficulty.pack()
    swatch = tk.Label(panel, width=40, height=5)
    swatch.pack(pady=8)
    prompt = ttk.Label(panel, wraplength=430)
    prompt.pack()
    entry = ttk.Entry(panel)
    entry.pack()
    status = ttk.Label(panel)
    status.pack()
    answer = []
    attempts = base = 0

    def new(event=None):
        nonlocal answer, attempts, base
        entry.delete(0, "end")
        submit.state(["!disabled"])
        level = difficulty.current()
        attempts = (10, 6, 3)[level]
        rgb = random.choices(range(256), k=3)
        swatch.configure(bg="#%02x%02x%02x" % tuple(rgb))
        base = (16, 2, 10, 10)[mode.current()]
        if mode.get() == "Symmetric XOR":
            value, key = rgb[:2]
            answer = [value]
            prompt.config(
                text=f"A byte XOR {key} equals {value ^ key}. Enter the original byte in decimal."
            )
        else:
            answer = rgb
            hints = [f"{name} = {value}" for name, value in zip("RGB", rgb)]
            hint = ", ".join(random.sample(hints, 2 - level))
            prompt.config(
                text=f"Estimate R G B in base {base}, separated by spaces. Within 8 counts wins. {hint}"
            )
        status.config(text=f"{attempts} guesses left.")
        entry.focus_set()

    def guess():
        nonlocal attempts
        if submit.instate(["disabled"]):
            return
        try:
            values = [int(x, base) for x in entry.get().split()]
            if len(values) != len(answer) or any(not 0 <= x <= 255 for x in values):
                raise ValueError
        except ValueError:
            status.config(text=f"Enter {len(answer)} byte value(s) in base {base}.")
            return
        attempts -= 1
        tolerance = 0 if len(answer) == 1 else 8
        deltas = [target - value for target, value in zip(answer, values)]
        if all(abs(d) <= tolerance for d in deltas):
            status.config(text="Solved!")
        elif attempts == 0:
            fmt = {2: "08b", 10: "d", 16: "02x"}[base]
            status.config(text="Answer: " + " ".join(format(x, fmt) for x in answer))
        else:
            clues = [
                "higher" if d > tolerance else "lower" if d < -tolerance else "correct"
                for d in deltas
            ]
            status.config(text=f"{', '.join(clues)} · {attempts} guesses left")
            return
        submit.state(["disabled"])

    submit = ttk.Button(panel, text="Check guess", command=guess)
    submit.pack()
    ttk.Button(panel, text="New puzzle", command=new).pack()
    for selector in (mode, difficulty):
        selector.bind("<<ComboboxSelected>>", new)
    root.bind("<Return>", lambda event: guess())
    new()
    root.mainloop()


if __name__ == "__main__":
    main()
