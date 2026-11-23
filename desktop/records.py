"""SQLite-backed list editor for contacts, parts, tasks and account-scoped notes."""

import os
import sqlite3
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from decimal import Decimal, InvalidOperation
import json
import random


def database():
    folder = Path(
        os.environ.get("PYTHON_WORKSHOP_DATA", Path.home() / ".python-workshop")
    )
    folder.mkdir(mode=0o700, exist_ok=True, parents=True)
    db = sqlite3.connect(folder / "records.sqlite3")
    db.execute(
        "CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY, kind TEXT, owner TEXT, fields TEXT)"
    )
    return db


def editor(root, db, kind, fields, owner=""):
    root.title(kind)
    panel = ttk.Frame(root, padding=12)
    panel.pack(fill="both", expand=True)
    inputs = []
    for label in fields:
        ttk.Label(panel, text=label).pack(anchor="w")
        entry = (
            tk.Text(panel, height=5) if label == "Body" else ttk.Entry(panel, width=48)
        )
        entry.pack(fill="x")
        inputs.append(entry)
    items = tk.Listbox(panel, exportselection=False, width=60)
    items.pack(fill="both", expand=True, pady=8)
    records = []
    deleted = []

    def refresh(sort=False):
        records[:] = [
            (key, json.loads(raw))
            for key, raw in db.execute(
                "SELECT id, fields FROM records WHERE kind=? AND owner=? ORDER BY id",
                (kind, owner),
            )
        ]
        if sort:
            records.sort(key=lambda row: row[1][0].casefold(), reverse=sort == "desc")
        items.delete(0, "end")
        for _, values in records:
            items.insert("end", "  ·  ".join(value.split("\n")[0] for value in values))

    def clear():
        items.selection_clear(0, "end")
        for entry in inputs:
            entry.delete("1.0" if isinstance(entry, tk.Text) else 0, "end")

    def select(event=None):
        if items.curselection():
            _, values = records[items.curselection()[0]]
            for entry, value in zip(inputs, values):
                start = "1.0" if isinstance(entry, tk.Text) else 0
                entry.delete(start, "end")
                entry.insert(start, value)

    def change(action):
        selection = items.curselection()
        if action in ("Update", "Delete") and not selection:
            messagebox.showinfo(kind, "Choose an item first.")
            return
        values = [
            e.get("1.0", "end-1c") if isinstance(e, tk.Text) else e.get().strip()
            for e in inputs
        ]
        if action in ("Add", "Update"):
            if not all(values):
                messagebox.showinfo(kind, "Fill in each field.")
                return
            if "Price" in fields:
                try:
                    price = Decimal(values[fields.index("Price")])
                    if not price.is_finite() or price < 0:
                        raise InvalidOperation
                except InvalidOperation:
                    messagebox.showinfo(kind, "Enter a nonnegative price.")
                    return
        with db:
            if action == "Add":
                db.execute(
                    "INSERT INTO records(kind, owner, fields) VALUES(?,?,?)",
                    (kind, owner, json.dumps(values)),
                )
            elif action == "Update":
                db.execute(
                    "UPDATE records SET fields=? WHERE id=?",
                    (json.dumps(values), records[selection[0]][0]),
                )
            elif action == "Delete":
                row = records[selection[0]]
                db.execute("DELETE FROM records WHERE id=?", (row[0],))
                deleted.append([row[1]])
            elif (
                action == "Delete all"
                and records
                and messagebox.askyesno(kind, "Delete all tasks?")
            ):
                db.execute(
                    "DELETE FROM records WHERE kind=? AND owner=?", (kind, owner)
                )
                deleted.append([values for _, values in records])
            elif action == "Restore" and deleted:
                db.executemany(
                    "INSERT INTO records(kind, owner, fields) VALUES(?,?,?)",
                    [(kind, owner, json.dumps(row)) for row in deleted.pop()],
                )
        clear()
        refresh()

    def choose():
        if records:
            items.selection_clear(0, "end")
            index = random.randrange(len(records))
            items.selection_set(index)
            items.see(index)
            select()

    items.bind("<<ListboxSelect>>", select)
    bar = ttk.Frame(panel)
    bar.pack()
    actions = ["Add", "Update", "Delete"]
    for name in actions:
        ttk.Button(bar, text=name, command=lambda n=name: change(n)).pack(side="left")
    ttk.Button(bar, text="Clear form", command=clear).pack(side="left")
    if kind == "Tasks":
        extra = ttk.Frame(panel)
        extra.pack()
        for label, command in [
            ("A–Z", lambda: refresh("asc")),
            ("Z–A", lambda: refresh("desc")),
            ("Pick one", choose),
            ("Count", lambda: messagebox.showinfo(kind, str(len(records)))),
            ("Delete all", lambda: change("Delete all")),
            ("Restore", lambda: change("Restore")),
        ]:
            ttk.Button(extra, text=label, command=command).pack(side="left")
    refresh()
    return panel


def start(kind, fields):
    root = tk.Tk()
    db = database()
    try:
        editor(root, db, kind, fields)
        root.mainloop()
    finally:
        db.close()
