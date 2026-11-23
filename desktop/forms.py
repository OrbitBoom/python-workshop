"""Small forms shared by the desktop utilities."""

import tkinter as tk
from tkinter import ttk
from concurrent.futures import ThreadPoolExecutor


def form(title, fields, actions, *, threaded=False, refresh=None):
    root = tk.Tk()
    root.title(title)
    panel = ttk.Frame(root, padding=16)
    panel.pack(fill="both", expand=True)
    entries = []
    for label, default in fields:
        ttk.Label(panel, text=label).pack(anchor="w")
        if isinstance(default, tuple):
            entry = ttk.Combobox(panel, values=default, state="readonly")
            entry.current(0)
        else:
            entry = ttk.Entry(
                panel, width=48, show="*" if label == "App password" else ""
            )
            entry.insert(0, default)
        entry.pack(fill="x", pady=(0, 8))
        entries.append(entry)
    buttons = ttk.Frame(panel)
    buttons.pack(fill="x")
    output = tk.Text(panel, height=8, width=50, wrap="word", state="disabled")
    output.pack(fill="both", expand=True, pady=(8, 0))
    worker = ThreadPoolExecutor(max_workers=1) if threaded else None
    timer = None

    def display(value):
        output.configure(state="normal")
        output.delete("1.0", "end")
        output.insert("1.0", value)
        output.configure(state="disabled")

    def run(action):
        nonlocal timer
        if timer is not None:
            root.after_cancel(timer)
            timer = None
        values = [entry.get() for entry in entries]

        def finish(future=None):
            nonlocal timer
            if future and not future.done():
                root.after(80, finish, future)
                return
            try:
                display(future.result() if future else action(*values))
            except Exception as error:
                display(str(error) or type(error).__name__)
            for button in buttons.winfo_children():
                button.state(["!disabled"])
            if refresh:
                timer = root.after(refresh, run, action)

        if worker:
            for button in buttons.winfo_children():
                button.state(["disabled"])
            display("Working…")
            root.after(80, finish, worker.submit(action, *values))
        else:
            finish()

    for label, action in actions.items():
        ttk.Button(buttons, text=label, command=lambda fn=action: run(fn)).pack(
            side="left"
        )
    if refresh:
        root.after_idle(run, next(iter(actions.values())))
    try:
        root.mainloop()
    finally:
        if worker:
            worker.shutdown(wait=False, cancel_futures=True)
