"""Regression tests using real Tk widgets and isolated data."""

import sqlite3
import sys
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from tkinter import ttk
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "desktop"))
from records import editor, database
from textpad import Textpad


def descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from descendants(child)


class DesktopTests(unittest.TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.root.withdraw()
        self.addCleanup(self.root.destroy)

    def test_textpad_cancel_save_and_reopen(self):
        app = Textpad(self.root)
        app.my_text.insert("1.0", "first draft")
        self.root.update()
        with patch("textpad.messagebox.askyesnocancel", return_value=None):
            app.new_file()
        self.assertEqual(app.my_text.get("1.0", "end-1c"), "first draft")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.txt"
            with patch("textpad.filedialog.asksaveasfilename", return_value=str(path)):
                self.assertTrue(app.save_as_file())
            self.assertEqual(path.read_text(), "first draft")
            app.new_file()
            self.assertEqual(app.my_text.get("1.0", "end-1c"), "")
            with patch("textpad.filedialog.askopenfilename", return_value=str(path)):
                app.open_file()
            self.assertEqual(app.my_text.get("1.0", "end-1c"), "first draft")
            self.assertFalse(app.dirty)

    def test_task_lifecycle(self):
        with (
            tempfile.TemporaryDirectory() as folder,
            patch.dict("os.environ", PYTHON_WORKSHOP_DATA=folder),
        ):
            db = database()
            self.addCleanup(db.close)
            panel = editor(self.root, db, "Tasks", ["Task"])
            widgets = list(descendants(panel))
            buttons = {b["text"]: b for b in widgets if isinstance(b, ttk.Button)}
            entry = next(e for e in widgets if isinstance(e, ttk.Entry))
            items = next(e for e in widgets if isinstance(e, tk.Listbox))
            entry.insert(0, "draw sprite")
            buttons["Add"].invoke()
            items.selection_set(0)
            entry.insert(0, "finish sprite")
            buttons["Update"].invoke()
            self.assertEqual(items.get(0), "finish sprite")
            items.selection_set(0)
            buttons["Delete"].invoke()
            self.assertEqual(items.size(), 0)
            buttons["Restore"].invoke()
            self.assertEqual(items.get(0), "finish sprite")
            with sqlite3.connect(Path(folder) / "records.sqlite3") as reopened:
                self.assertEqual(
                    reopened.execute("SELECT count(*) FROM records").fetchone()[0], 1
                )
