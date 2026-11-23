"""Local account and notes practice app. Note contents are stored as plain text."""

import hashlib
import hmac
import secrets
import tkinter as tk
from tkinter import ttk
from records import database, editor


def digest(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600000)


def main():
    root = tk.Tk()
    root.title("Notebook sign-in")
    db = database()
    db.execute(
        "CREATE TABLE IF NOT EXISTS accounts (name TEXT PRIMARY KEY, salt BLOB, digest BLOB)"
    )
    login = ttk.Frame(root, padding=12)
    login.pack()
    ttk.Label(login, text="Username").pack()
    username = ttk.Entry(login)
    username.pack()
    ttk.Label(login, text="Password").pack()
    password = ttk.Entry(login, show="*")
    password.pack()
    status = ttk.Label(login)
    status.pack()

    def enter(register):
        name, secret = username.get().strip(), password.get()
        if not name or not secret:
            status.config(text="Enter a username and password.")
            return
        if register:
            salt = secrets.token_bytes(16)
            with db:
                result = db.execute(
                    "INSERT OR IGNORE INTO accounts VALUES(?,?,?)",
                    (name, salt, digest(secret, salt)),
                )
            if not result.rowcount:
                status.config(text="Username already registered.")
                return
        else:
            row = db.execute(
                "SELECT salt, digest FROM accounts WHERE name=?", (name,)
            ).fetchone()
            if not row or not hmac.compare_digest(digest(secret, row[0]), row[1]):
                status.config(text="Check your username and password.")
                return
        password.delete(0, "end")
        login.pack_forget()
        panel = editor(root, db, "Notebook", ["Title", "Body"], owner=name)

        def logout():
            panel.destroy()
            status.config(text="")
            root.title("Notebook sign-in")
            login.pack()

        ttk.Button(panel, text="Sign out", command=logout).pack()

    ttk.Button(login, text="Register", command=lambda: enter(True)).pack()
    ttk.Button(login, text="Sign in", command=lambda: enter(False)).pack()
    try:
        root.mainloop()
    finally:
        db.close()


if __name__ == "__main__":
    main()
