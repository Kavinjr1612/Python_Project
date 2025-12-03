import customtkinter as ctk
from module_dataanalysis import create_dataanalysis_screen
from ui_theme import apply_theme

apply_theme()

root = ctk.CTk()
root.title("Data Analysis Toolkit")
root.geometry("1200x750")

def go_home():
    root.destroy()

create_dataanalysis_screen(root, go_home)

root.mainloop()
