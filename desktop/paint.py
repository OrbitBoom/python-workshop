"""Draw on a Tk canvas and export the actual strokes as a standalone SVG."""

import tkinter as tk
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox, ttk
from xml.etree import ElementTree as ET


def export(width, height, background, strokes):
    svg = ET.Element(
        "svg", xmlns="http://www.w3.org/2000/svg", width=str(width), height=str(height)
    )
    ET.SubElement(svg, "rect", width="100%", height="100%", fill=background)
    for colour, size, points in strokes:
        if len(points) == 1:
            x, y = points[0]
            ET.SubElement(
                svg, "circle", cx=str(x), cy=str(y), r=str(size / 2), fill=colour
            )
        else:
            ET.SubElement(
                svg,
                "polyline",
                fill="none",
                stroke=colour,
                points=" ".join(f"{x},{y}" for x, y in points),
                attrib={
                    "stroke-width": str(size),
                    "stroke-linejoin": "round",
                    "stroke-linecap": "round",
                },
            )
    return ET.tostring(svg, encoding="utf-8", xml_declaration=True)


def main():
    root = tk.Tk()
    root.title("Paint")
    tools = ttk.Frame(root, padding=6)
    tools.pack(fill="x")
    background, ink = "#ffffff", "#141414"
    strokes = []
    active = None
    size = tk.IntVar(value=4)
    canvas = tk.Canvas(root, bg=background, width=700, height=480, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    def begin(event):
        nonlocal active
        width = size.get()
        colour = ink or background
        active = (colour, width, [(event.x, event.y)])
        strokes.append(active)
        r = width / 2
        canvas.create_oval(
            event.x - r, event.y - r, event.x + r, event.y + r, fill=colour, outline=""
        )

    def move(event):
        if active is None:
            return
        colour, width, points = active
        x, y = points[-1]
        canvas.create_line(
            x, y, event.x, event.y, width=width, fill=colour, capstyle="round"
        )
        points.append((event.x, event.y))

    def brush():
        nonlocal ink
        choice = colorchooser.askcolor(initialcolor=ink or background)[1]
        if choice:
            ink = choice

    def erase():
        nonlocal ink
        ink = None

    def paper():
        nonlocal background
        choice = colorchooser.askcolor(initialcolor=background)[1]
        if choice:
            background = choice
            canvas.config(bg=choice)

    def clear():
        nonlocal active
        canvas.delete("all")
        strokes.clear()
        active = None

    def save():
        name = filedialog.asksaveasfilename(
            defaultextension=".svg",
            filetypes=[
                ("SVG drawing", "*.svg"),
                ("JPEG image", "*.jpg"),
                ("PNG image", "*.png"),
            ],
        )
        if name:
            try:
                if Path(name).suffix.lower() in {".jpg", ".jpeg", ".png"}:
                    from PIL import Image, ImageDraw

                    image = Image.new(
                        "RGB", (canvas.winfo_width(), canvas.winfo_height()), background
                    )
                    draw = ImageDraw.Draw(image)
                    for colour, width, points in strokes:
                        if len(points) > 1:
                            draw.line(points, fill=colour, width=width, joint="curve")
                        for x, y in (points[0], points[-1]):
                            r = width / 2
                            draw.ellipse((x - r, y - r, x + r, y + r), fill=colour)
                    image.save(name)
                    return
                Path(name).write_bytes(
                    export(
                        canvas.winfo_width(), canvas.winfo_height(), background, strokes
                    )
                )
            except ImportError:
                messagebox.showinfo("Raster export", "Install Pillow or select SVG.")
            except OSError as exc:
                messagebox.showerror("Save drawing", str(exc))

    for label, fn in [
        ("Brush colour", brush),
        ("Eraser", erase),
        ("Paper colour", paper),
        ("Clear", clear),
        ("Save drawing", save),
    ]:
        ttk.Button(tools, text=label, command=fn).pack(side="left")
    tk.Scale(
        tools, from_=1, to=50, orient="horizontal", variable=size, label="Brush width"
    ).pack(side="left")
    canvas.bind("<Button-1>", begin)
    canvas.bind("<B1-Motion>", move)
    root.mainloop()


if __name__ == "__main__":
    main()
