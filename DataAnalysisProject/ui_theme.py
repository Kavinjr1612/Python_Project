# ui_theme.py
import customtkinter as ctk

# Global Theme Colors (Midnight Glass)
BG_TOP = "#0F0C29"
BG_MID = "#302B63"
BG_BOTTOM = "#24243E"

CARD_BG = "#1C1C2E"
TEXTBOX_BG = "#11111A"

PRIMARY = "#3B82F6"
PRIMARY_HOVER = "#2563EB"

TEXT_COLOR = "#E2E2EF"

def apply_theme():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    