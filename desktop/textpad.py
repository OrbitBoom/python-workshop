from tkinter import *
from tkinter import filedialog, font, colorchooser, messagebox, simpledialog
import os

# --------------------------------------------------------------------------
# Themes
# --------------------------------------------------------------------------
THEMES = {
    "light": {
        "bg": "#f3f3f3",
        "toolbar_bg": "#e8e8ec",
        "button_bg": "#ffffff",
        "button_fg": "#1f1f1f",
        "button_active": "#dfe4ff",
        "text_bg": "#ffffff",
        "text_fg": "#1f1f1f",
        "select_bg": "#cfe0ff",
        "linenum_bg": "#eaeaee",
        "linenum_fg": "#8a8a94",
        "status_bg": "#e8e8ec",
        "status_fg": "#444444",
        "accent": "#4b6bfb",
        "menu_bg": "#ffffff",
        "menu_fg": "#1f1f1f",
    },
    "dark": {
        "bg": "#1e1e2e",
        "toolbar_bg": "#181825",
        "button_bg": "#282838",
        "button_fg": "#cdd6f4",
        "button_active": "#3a3a52",
        "text_bg": "#1e1e2e",
        "text_fg": "#cdd6f4",
        "select_bg": "#45475a",
        "linenum_bg": "#181825",
        "linenum_fg": "#6c7086",
        "status_bg": "#181825",
        "status_fg": "#a6adc8",
        "accent": "#89b4fa",
        "menu_bg": "#181825",
        "menu_fg": "#cdd6f4",
    },
}


class Textpad:
    def __init__(self, root):
        self.root = root
        self.root.title("Untitled - Textpad")
        self.root.geometry("1200x720")
        self.root.minsize(640, 400)

        self.filepath = None
        self.dirty = False
        self.theme_name = "light"
        self.font_family = (
            "Consolas" if "Consolas" in font.families() else "Courier New"
        )
        self.font_size = 13
        self.format_fonts = {}
        self.word_wrap = True

        self._set_icon()
        self._build_ui()
        self._apply_theme()
        self._bind_shortcuts()
        self._update_status()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------
    def _set_icon(self):
        # The old version hardcoded a path on someone's personal desktop.
        # Try a local icon if one happens to exist next to this script;
        # otherwise just skip it quietly instead of crashing.
        try:
            here = os.path.dirname(os.path.abspath(__file__))
            candidate = os.path.join(here, "pen.ico")
            if os.path.exists(candidate):
                self.root.iconbitmap(candidate)
        except Exception:
            pass

    def _build_ui(self):
        self.main_font = font.Font(family=self.font_family, size=self.font_size)

        # ---- Toolbar -----------------------------------------------------
        self.toolbar = Frame(self.root, bd=0)
        self.toolbar.pack(fill=X)

        def tb_btn(parent, text, command, width=4):
            b = Button(
                parent,
                text=text,
                command=command,
                relief=FLAT,
                font=("Segoe UI", 11),
                width=width,
                cursor="hand2",
                bd=0,
                padx=6,
                pady=4,
            )
            b.pack(side=LEFT, padx=2, pady=4)
            return b

        self.tb_new = tb_btn(self.toolbar, "🗎 New", self.new_file, width=7)
        self.tb_open = tb_btn(self.toolbar, "📂 Open", self.open_file, width=7)
        self.tb_save = tb_btn(self.toolbar, "💾 Save", self.save_file, width=7)
        self._sep(self.toolbar)
        self.tb_bold = tb_btn(self.toolbar, "B", self.toggle_bold, width=3)
        self.tb_italic = tb_btn(self.toolbar, "I", self.toggle_italic, width=3)
        self.tb_underline = tb_btn(self.toolbar, "U", self.toggle_underline, width=3)
        self._sep(self.toolbar)
        self.tb_color = tb_btn(self.toolbar, "🎨 Color", self.text_color, width=8)
        self.tb_highlight = tb_btn(
            self.toolbar, "🖍 Highlight", self.highlight_color, width=10
        )
        self._sep(self.toolbar)
        self.tb_zoom_out = tb_btn(self.toolbar, "A−", self.zoom_out, width=4)
        self.tb_zoom_in = tb_btn(self.toolbar, "A+", self.zoom_in, width=4)
        self._sep(self.toolbar)
        self.tb_find = tb_btn(self.toolbar, "🔍 Find", self.open_find, width=7)
        self.tb_theme = tb_btn(self.toolbar, "🌙 Theme", self.toggle_theme, width=8)

        # ---- Editor area (line numbers + text + scrollbars) --------------
        editor_frame = Frame(self.root)
        editor_frame.pack(fill=BOTH, expand=True, padx=(0, 0))

        self.linenumbers = Text(
            editor_frame,
            width=5,
            padx=6,
            takefocus=0,
            border=0,
            state=DISABLED,
            wrap=NONE,
        )
        self.linenumbers.pack(side=LEFT, fill=Y)

        text_container = Frame(editor_frame)
        text_container.pack(side=LEFT, fill=BOTH, expand=True)

        self.v_scroll = Scrollbar(text_container, orient=VERTICAL)
        self.v_scroll.pack(side=RIGHT, fill=Y)
        self.h_scroll = Scrollbar(text_container, orient=HORIZONTAL)
        self.h_scroll.pack(side=BOTTOM, fill=X)

        self.my_text = Text(
            text_container,
            undo=True,
            wrap=NONE,
            font=self.main_font,
            border=0,
            yscrollcommand=self._on_text_scroll,
            xscrollcommand=self.h_scroll.set,
        )
        self.my_text.pack(side=LEFT, fill=BOTH, expand=True)

        self.v_scroll.config(command=self._on_vscroll)
        self.h_scroll.config(command=self.my_text.xview)

        self.set_word_wrap(self.word_wrap)

        # ---- Status bar ----------------------------------------------------
        self.status_bar = Frame(self.root)
        self.status_bar.pack(fill=X, side=BOTTOM)

        self.status_left = Label(self.status_bar, text="New file", anchor=W)
        self.status_left.pack(side=LEFT, padx=10, pady=4)

        self.status_right = Label(self.status_bar, text="Ln 1, Col 1", anchor=E)
        self.status_right.pack(side=RIGHT, padx=10, pady=4)

        # ---- Menu ----------------------------------------------------------
        self._build_menu()

        # ---- Events ----------------------------------------------------------
        self.my_text.bind("<<Modified>>", self._on_modified)
        self.my_text.bind("<KeyRelease>", lambda e: self._update_status())
        self.my_text.bind("<ButtonRelease>", lambda e: self._update_status())
        self.my_text.bind("<Control-MouseWheel>", self._on_ctrl_wheel)

    def _sep(self, parent):
        Frame(parent, width=1, bg="#c0c0c8").pack(side=LEFT, fill=Y, padx=6, pady=6)

    def _build_menu(self):
        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.file_menu = Menu(self.menu_bar, tearoff=False)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New            Ctrl+N", command=self.new_file)
        self.file_menu.add_command(
            label="Open           Ctrl+O", command=self.open_file
        )
        self.file_menu.add_command(
            label="Save            Ctrl+S", command=self.save_file
        )
        self.file_menu.add_command(
            label="Save As   Ctrl+Shift+S", command=self.save_as_file
        )
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.on_close)

        self.edit_menu = Menu(self.menu_bar, tearoff=False)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(
            label="Undo            Ctrl+Z",
            command=lambda: self.my_text.event_generate("<<Undo>>"),
        )
        self.edit_menu.add_command(
            label="Redo            Ctrl+Y",
            command=lambda: self.my_text.event_generate("<<Redo>>"),
        )
        self.edit_menu.add_separator()
        self.edit_menu.add_command(
            label="Cut              Ctrl+X",
            command=lambda: self.my_text.event_generate("<<Cut>>"),
        )
        self.edit_menu.add_command(
            label="Copy            Ctrl+C",
            command=lambda: self.my_text.event_generate("<<Copy>>"),
        )
        self.edit_menu.add_command(
            label="Paste            Ctrl+V",
            command=lambda: self.my_text.event_generate("<<Paste>>"),
        )
        self.edit_menu.add_separator()
        self.edit_menu.add_command(
            label="Select All       Ctrl+A", command=self.select_all
        )
        self.edit_menu.add_command(label="Clear All", command=self.clear_all)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(
            label="Find & Replace   Ctrl+F", command=self.open_find
        )

        self.format_menu = Menu(self.menu_bar, tearoff=False)
        self.menu_bar.add_cascade(label="Format", menu=self.format_menu)
        self.format_menu.add_command(label="Bold", command=self.toggle_bold)
        self.format_menu.add_command(label="Italic", command=self.toggle_italic)
        self.format_menu.add_command(label="Underline", command=self.toggle_underline)
        self.format_menu.add_separator()
        self.format_menu.add_command(
            label="Text Color (selection)", command=self.text_color
        )
        self.format_menu.add_command(
            label="Highlight Color (selection)", command=self.highlight_color
        )
        self.format_menu.add_command(
            label="All Text Color", command=self.all_text_color
        )
        self.format_menu.add_command(
            label="Background Color", command=self.bg_color_pick
        )

        self.view_menu = Menu(self.menu_bar, tearoff=False)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Zoom In     Ctrl++", command=self.zoom_in)
        self.view_menu.add_command(label="Zoom Out   Ctrl+-", command=self.zoom_out)
        self.view_menu.add_separator()
        self.wrap_var = BooleanVar(value=self.word_wrap)
        self.view_menu.add_checkbutton(
            label="Word Wrap",
            variable=self.wrap_var,
            command=lambda: self.set_word_wrap(self.wrap_var.get()),
        )
        self.view_menu.add_separator()
        self.view_menu.add_command(
            label="Toggle Dark / Light Mode", command=self.toggle_theme
        )

    # ------------------------------------------------------------------
    # File operations
    # ------------------------------------------------------------------
    def _confirm_discard(self):
        if self.dirty or self.my_text.edit_modified():
            choice = messagebox.askyesnocancel(
                "Unsaved changes", "You have unsaved changes. Save before continuing?"
            )
            if choice is None:
                return False
            if choice:
                return self.save_file()
        return True

    def new_file(self):
        if not self._confirm_discard():
            return
        self.my_text.delete("1.0", END)
        self.filepath = None
        self.root.title("Untitled - Textpad")
        self.status_left.config(text="New file")
        self.dirty = False
        self.my_text.edit_modified(False)
        self.my_text.edit_reset()
        self._update_status()
        self._update_linenumbers()

    def open_file(self):
        if not self._confirm_discard():
            return
        path = filedialog.askopenfilename(
            title="Open file",
            filetypes=(
                ("Text Files", "*.txt"),
                ("Python Files", "*.py"),
                ("HTML Files", "*.html"),
                ("Markdown", "*.md"),
                ("All Files", "*.*"),
            ),
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            messagebox.showerror("Error opening file", str(e))
            return

        self.my_text.delete("1.0", END)
        self.my_text.insert(END, content)
        self.filepath = path
        self.root.title(f"{os.path.basename(path)} - Textpad")
        self.status_left.config(text=path)
        self.dirty = False
        self.my_text.edit_modified(False)
        self.my_text.edit_reset()
        self._update_status()
        self._update_linenumbers()

    def save_file(self):
        if self.filepath:
            try:
                with open(self.filepath, "w", encoding="utf-8") as f:
                    f.write(self.my_text.get(1.0, "end-1c"))
            except Exception as e:
                messagebox.showerror("Error saving file", str(e))
                return False
            self.status_left.config(text=f"Saved: {self.filepath}")
            self.dirty = False
            self.my_text.edit_modified(False)
            self.root.title(f"{os.path.basename(self.filepath)} - Textpad")
            return True
        else:
            return self.save_as_file()

    def save_as_file(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            title="Save File",
            filetypes=(
                ("Text Files", "*.txt"),
                ("Python Files", "*.py"),
                ("HTML Files", "*.html"),
                ("Markdown", "*.md"),
                ("All Files", "*.*"),
            ),
        )
        if not path:
            return False
        previous = self.filepath
        self.filepath = path
        if self.save_file():
            return True
        self.filepath = previous
        return False

    def on_close(self):
        if self._confirm_discard():
            self.root.destroy()

    # ------------------------------------------------------------------
    # Edit helpers
    # ------------------------------------------------------------------
    def select_all(self, event=None):
        self.my_text.tag_add("sel", "1.0", "end")
        return "break"

    def clear_all(self):
        if messagebox.askyesno("Clear all", "Clear all text? This cannot be undone."):
            self.my_text.delete(1.0, END)

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------
    def _toggle_tag(self, tag_name, **font_opts):
        try:
            if not self.my_text.tag_ranges("sel"):
                return
        except TclError:
            return
        f = font.Font(font=self.main_font)
        f.configure(**font_opts)
        self.format_fonts[tag_name] = f
        self.my_text.tag_configure(tag_name, font=f)
        current = self.my_text.tag_names("sel.first")
        if tag_name in current:
            self.my_text.tag_remove(tag_name, "sel.first", "sel.last")
        else:
            self.my_text.tag_add(tag_name, "sel.first", "sel.last")

    def toggle_bold(self):
        self._toggle_tag("bold", weight="bold")

    def toggle_italic(self):
        self._toggle_tag("italic", slant="italic")

    def toggle_underline(self):
        self._toggle_tag("underline", underline=1)

    def text_color(self):
        color = colorchooser.askcolor(title="Text color")[1]
        if color and self.my_text.tag_ranges("sel"):
            tag = f"color_{color}"
            self.my_text.tag_configure(tag, foreground=color)
            self.my_text.tag_add(tag, "sel.first", "sel.last")

    def highlight_color(self):
        color = colorchooser.askcolor(title="Highlight color")[1]
        if color and self.my_text.tag_ranges("sel"):
            tag = f"bg_{color}"
            self.my_text.tag_configure(tag, background=color)
            self.my_text.tag_add(tag, "sel.first", "sel.last")

    def all_text_color(self):
        color = colorchooser.askcolor(title="All text color")[1]
        if color:
            self.my_text.config(fg=color)

    def bg_color_pick(self):
        color = colorchooser.askcolor(title="Background color")[1]
        if color:
            self.my_text.config(bg=color)

    def zoom_in(self, event=None):
        self.font_size = min(self.font_size + 1, 60)
        self._apply_font()
        return "break"

    def zoom_out(self, event=None):
        self.font_size = max(self.font_size - 1, 6)
        self._apply_font()
        return "break"

    def _apply_font(self):
        self.main_font.configure(size=self.font_size)
        self._update_linenumbers()

    def _on_ctrl_wheel(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()
        return "break"

    def set_word_wrap(self, on):
        self.word_wrap = on
        self.my_text.config(wrap=WORD if on else NONE)
        self.h_scroll.pack_forget() if on else self.h_scroll.pack(side=BOTTOM, fill=X)

    # ------------------------------------------------------------------
    # Line numbers + scrolling sync
    # ------------------------------------------------------------------
    def _on_text_scroll(self, *args):
        self.v_scroll.set(*args)
        self._sync_linenumbers()

    def _on_vscroll(self, *args):
        self.my_text.yview(*args)
        self.linenumbers.yview(*args)

    def _sync_linenumbers(self):
        self.linenumbers.yview_moveto(self.my_text.yview()[0])

    def _update_linenumbers(self):
        line_count = int(self.my_text.index("end-1c").split(".")[0])
        text = "\n".join(str(i) for i in range(1, line_count + 1))
        self.linenumbers.config(state=NORMAL, font=self.main_font)
        self.linenumbers.delete("1.0", END)
        self.linenumbers.insert("1.0", text)
        self.linenumbers.config(state=DISABLED)
        self._sync_linenumbers()

    def _on_modified(self, event=None):
        if not self.my_text.edit_modified():
            return
        self.dirty = True
        self.my_text.edit_modified(False)
        self._update_linenumbers()
        self._update_status()
        if not self.root.title().startswith("*"):
            self.root.title("*" + self.root.title())

    # ------------------------------------------------------------------
    # Status bar
    # ------------------------------------------------------------------
    def _update_status(self):
        index = self.my_text.index(INSERT)
        line, col = index.split(".")
        content = self.my_text.get("1.0", "end-1c")
        words = len(content.split())
        chars = len(content)
        self.status_right.config(
            text=f"Ln {line}, Col {int(col) + 1}   |   {words} words   |   {chars} chars"
        )

    # ------------------------------------------------------------------
    # Find & Replace
    # ------------------------------------------------------------------
    def open_find(self, event=None):
        win = Toplevel(self.root)
        win.title("Find & Replace")
        win.geometry("360x140")
        win.resizable(False, False)
        win.transient(self.root)

        Label(win, text="Find:").grid(row=0, column=0, sticky=E, padx=6, pady=6)
        find_entry = Entry(win, width=30)
        find_entry.grid(row=0, column=1, columnspan=2, pady=6)
        find_entry.focus_set()

        Label(win, text="Replace:").grid(row=1, column=0, sticky=E, padx=6, pady=6)
        replace_entry = Entry(win, width=30)
        replace_entry.grid(row=1, column=1, columnspan=2, pady=6)

        def find_next():
            self.my_text.tag_remove("found", "1.0", END)
            target = find_entry.get()
            if not target:
                return
            start = self.my_text.index(INSERT)
            pos = self.my_text.search(target, start, stopindex=END)
            if not pos:
                pos = self.my_text.search(target, "1.0", stopindex=END)
                if not pos:
                    messagebox.showinfo("Find", f'"{target}" not found.')
                    return
            end = f"{pos}+{len(target)}c"
            self.my_text.tag_add("found", pos, end)
            self.my_text.tag_config("found", background="#ffd54a", foreground="#000000")
            self.my_text.mark_set(INSERT, end)
            self.my_text.see(pos)

        def replace_one():
            target = find_entry.get()
            repl = replace_entry.get()
            if self.my_text.tag_ranges("found"):
                self.my_text.delete("found.first", "found.last")
                self.my_text.insert(INSERT, repl)
            find_next()

        def replace_all():
            target = find_entry.get()
            repl = replace_entry.get()
            if not target:
                return
            content = self.my_text.get("1.0", "end-1c")
            count = content.count(target)
            new_content = content.replace(target, repl)
            self.my_text.delete("1.0", END)
            self.my_text.insert("1.0", new_content)
            messagebox.showinfo("Replace All", f"Replaced {count} occurrence(s).")

        btn_frame = Frame(win)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=8)
        Button(btn_frame, text="Find Next", command=find_next).pack(side=LEFT, padx=4)
        Button(btn_frame, text="Replace", command=replace_one).pack(side=LEFT, padx=4)
        Button(btn_frame, text="Replace All", command=replace_all).pack(
            side=LEFT, padx=4
        )

    # ------------------------------------------------------------------
    # Theme
    # ------------------------------------------------------------------
    def toggle_theme(self):
        self.theme_name = "dark" if self.theme_name == "light" else "light"
        self._apply_theme()

    def _apply_theme(self):
        t = THEMES[self.theme_name]
        self.root.config(bg=t["bg"])
        self.toolbar.config(bg=t["toolbar_bg"])
        self.status_bar.config(bg=t["status_bg"])
        self.status_left.config(bg=t["status_bg"], fg=t["status_fg"])
        self.status_right.config(bg=t["status_bg"], fg=t["status_fg"])

        self.my_text.config(
            bg=t["text_bg"],
            fg=t["text_fg"],
            insertbackground=t["text_fg"],
            selectbackground=t["select_bg"],
            selectforeground=t["text_fg"],
        )
        self.linenumbers.config(bg=t["linenum_bg"], fg=t["linenum_fg"])

        for b in (
            self.tb_new,
            self.tb_open,
            self.tb_save,
            self.tb_bold,
            self.tb_italic,
            self.tb_underline,
            self.tb_color,
            self.tb_highlight,
            self.tb_zoom_out,
            self.tb_zoom_in,
            self.tb_find,
            self.tb_theme,
        ):
            b.config(
                bg=t["button_bg"],
                fg=t["button_fg"],
                activebackground=t["button_active"],
                activeforeground=t["button_fg"],
            )

        self.tb_theme.config(
            text="☀ Theme" if self.theme_name == "dark" else "🌙 Theme"
        )

        for m in (
            self.file_menu,
            self.edit_menu,
            self.format_menu,
            self.view_menu,
            self.menu_bar,
        ):
            try:
                m.config(bg=t["menu_bg"], fg=t["menu_fg"])
            except TclError:
                pass

    # ------------------------------------------------------------------
    # Shortcuts
    # ------------------------------------------------------------------
    def _bind_shortcuts(self):
        self.root.bind("<Control-n>", lambda e: self.new_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-S>", lambda e: self.save_as_file())
        self.root.bind("<Control-Shift-S>", lambda e: self.save_as_file())
        self.root.bind("<Control-f>", self.open_find)
        self.root.bind("<Control-a>", self.select_all)
        self.root.bind("<Control-A>", self.select_all)
        self.root.bind("<Control-plus>", self.zoom_in)
        self.root.bind("<Control-equal>", self.zoom_in)
        self.root.bind("<Control-minus>", self.zoom_out)
        self.root.bind("<Control-b>", lambda e: self.toggle_bold())
        self.root.bind("<Control-i>", lambda e: self.toggle_italic())
        self.root.bind("<Control-u>", lambda e: self.toggle_underline())


if __name__ == "__main__":
    root = Tk()
    app = Textpad(root)
    root.mainloop()
