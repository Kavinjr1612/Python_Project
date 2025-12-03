import customtkinter as ctk
from ui_theme import apply_theme
from module_textutils import create_textutils_screen

apply_theme()

root = ctk.CTk()
root.title("Text Utilities Toolkit")
root.geometry("1100x700")

# CREATE + DISPLAY TEXTUTILS UI
frame = create_textutils_screen(root, lambda: None)
frame.pack(fill="both", expand=True)

root.mainloop()
