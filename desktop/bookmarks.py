from tkinter import *
import webbrowser

window = Tk()
window.title("Favourite Websites")


def website1():
    webbrowser.open_new_tab("https://www.youtube.com/")


def website2():
    webbrowser.open_new_tab("https://www.rubiks.com/solution-guides")


def website3():
    webbrowser.open_new_tab("https://classroom.google.com/")


button1 = Button(window, text="YouTube", command=website1)
button1.pack()
Label(text="").pack()

button1 = Button(window, text="Rubiks cube solution", command=website2)
button1.pack()
Label(text="").pack()

button1 = Button(window, text="Google Classroom", command=website3)
button1.pack()
Label(text="").pack()
window.mainloop()
