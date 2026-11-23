import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


def main():
    root = tk.Tk()
    root.title("Music player")
    tracks = []
    songs = tk.Listbox(root, width=60, exportselection=False)
    songs.pack(fill="both", expand=True)
    status = ttk.Label(root, text="Add MP3 or WAV files to your playlist.")
    status.pack()
    paused = False
    current = None
    mixer = None

    def add():
        for name in filedialog.askopenfilenames(
            filetypes=[("Audio", "*.mp3 *.wav"), ("All files", "*")]
        ):
            tracks.append(name)
            songs.insert("end", Path(name).name)

    def play(offset=0):
        nonlocal paused, current, mixer
        if not tracks:
            return
        selected = songs.curselection()
        index = (
            current
            if offset and current is not None
            else selected[0]
            if selected
            else 0
        )
        index = (index + offset) % len(tracks)
        try:
            from pygame import mixer as audio

            if not audio.get_init():
                audio.init()
            mixer = audio
            mixer.music.load(tracks[index])
            mixer.music.play()
        except ImportError:
            messagebox.showinfo(
                "Audio dependency", "Install pygame with python -m pip install pygame."
            )
            return
        except (OSError, RuntimeError) as error:
            status.config(text=str(error))
            return
        current, paused = index, False
        songs.selection_clear(0, "end")
        songs.selection_set(index)
        songs.see(index)
        status.config(text="Playing " + Path(tracks[index]).name)

    def pause():
        nonlocal paused
        if mixer and current is not None:
            if paused:
                mixer.music.unpause()
            else:
                mixer.music.pause()
            paused = not paused
            status.config(
                text="Paused" if paused else "Playing " + Path(tracks[current]).name
            )

    def stop():
        nonlocal current
        if mixer:
            mixer.music.stop()
        current = None
        status.config(text="Stopped")

    bar = ttk.Frame(root)
    bar.pack()
    for label, callback in [
        ("Add", add),
        ("Previous", lambda: play(-1)),
        ("Play", play),
        ("Pause / resume", pause),
        ("Stop", stop),
        ("Next", lambda: play(1)),
    ]:
        ttk.Button(bar, text=label, command=callback).pack(side="left")
    root.mainloop()
    if mixer:
        mixer.quit()


if __name__ == "__main__":
    main()
