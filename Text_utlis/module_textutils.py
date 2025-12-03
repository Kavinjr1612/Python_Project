# module_textutils.py
import customtkinter as ctk
import tkinter as tk
import re
import tkinter.messagebox as mb
from ui_theme import CARD_BG, TEXTBOX_BG, PRIMARY, PRIMARY_HOVER, TEXT_COLOR, apply_theme


apply_theme()


def create_textutils_screen(parent, go_back_callback):
    frame = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=12)
    # Title bar
    top = ctk.CTkFrame(frame, fg_color="transparent")
    top.pack(fill="x", pady=(8,8), padx=12)
    ctk.CTkLabel(top, text="Text Utilities Toolkit", font=("Segoe UI", 18, "bold"), text_color=TEXT_COLOR).pack(side="left")
    ctk.CTkButton(top, text="Back", width=90, fg_color=PRIMARY, hover_color=PRIMARY_HOVER, command=go_back_callback).pack(side="right")

    # Layout frames
    content = ctk.CTkFrame(frame, fg_color="transparent")
    content.pack(fill="both", expand=True, padx=12, pady=8)

    left = ctk.CTkFrame(content, fg_color="transparent")
    left.grid(row=0, column=0, sticky="nsew", padx=(0,10))
    right = ctk.CTkFrame(content, fg_color="transparent")
    right.grid(row=0, column=1, sticky="nsew")

    content.grid_columnconfigure(0, weight=3)
    content.grid_columnconfigure(1, weight=2)

    # Original text
    ctk.CTkLabel(left, text="Original Text", anchor="w", font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=6, pady=(6,4))
    original = ctk.CTkTextbox(left, height=160, fg_color=TEXTBOX_BG, wrap="word", corner_radius=8)
    original.pack(fill="x", padx=6, pady=(0,10))
    original.configure(state="disabled")

    # Tools
    tools_card = ctk.CTkFrame(left, fg_color=CARD_BG, corner_radius=10)
    tools_card.pack(fill="both", padx=6, pady=6)
    ctk.CTkLabel(tools_card, text="Tools", font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=8, pady=(8,4))

    # Output area
    ctk.CTkLabel(right, text="Output", anchor="w", font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=6, pady=(6,4))
    output = ctk.CTkTextbox(right, height=300, fg_color=TEXTBOX_BG, wrap="word", corner_radius=8)
    output.pack(fill="both", padx=6, pady=(0,10))
    output.configure(state="disabled")

    # Info cards
    info = ctk.CTkFrame(right, fg_color="transparent")
    info.pack(fill="x", padx=6, pady=(4,10))
    def create_info_label(parent, text):
        lbl = ctk.CTkLabel(parent, text=text, width=130, height=70, fg_color=TEXTBOX_BG, corner_radius=8, font=("Segoe UI", 11))
        lbl.pack(side="left", padx=6)
        return lbl
    words_card = create_info_label(info, "Words\n0")
    chars_card = create_info_label(info, "Characters\n0")
    unique_card = create_info_label(info, "Unique\n0")
    lines_card = create_info_label(info, "Lines\n0")

    # Helper functions
    def get_original_text():
        return original.get("1.0", "end-1c")

    def set_output_text(txt):
        output.configure(state="normal")
        output.delete("1.0", "end")
        output.insert("1.0", txt)
        output.configure(state="disabled")

    def update_info(txt):
        words = re.findall(r"\S+", txt)
        lines = [l for l in txt.splitlines() if l.strip()]
        unique = len(set(w.lower() for w in words))
        words_card.configure(text=f"Words\n{len(words)}")
        chars_card.configure(text=f"Characters\n{len(txt)}")
        unique_card.configure(text=f"Unique\n{unique}")
        lines_card.configure(text=f"Lines\n{len(lines)}")

    # Actions
    def uppercase():
        txt = get_original_text()
        set_output_text(txt.upper())
        update_info(txt.upper())

    def lowercase():
        txt = get_original_text()
        set_output_text(txt.lower())
        update_info(txt.lower())

    def titlecase():
        txt = get_original_text()
        set_output_text(txt.title())
        update_info(txt.title())

    def wordcount():
        txt = get_original_text()
        words = re.findall(r"\S+", txt)
        unique = len(set(w.lower() for w in words))
        lines = len([l for l in txt.splitlines() if l.strip()])
        res = f"Words: {len(words)}\nCharacters: {len(txt)}\nUnique words: {unique}\nLines: {lines}"
        set_output_text(res)

    def removedups():
        txt = get_original_text()
        words = re.findall(r"\S+", txt)
        seen=set(); out=[]
        for w in words:
            if w.lower() not in seen:
                seen.add(w.lower()); out.append(w)
        res = " ".join(out)
        set_output_text(res); update_info(res)

    def extract_emails():
        txt = get_original_text()
        emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}", txt)
        set_output_text("\n".join(emails) if emails else "No emails found.")

    def extract_phones():
        txt = get_original_text()
        phones = re.findall(r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}", txt)
        phones = [p for p in phones if len(re.sub(r"\D","",p))>=7]
        set_output_text("\n".join(phones) if phones else "No phone numbers found.")

    def summarize():
        txt = get_original_text().strip()
        sentences = re.split(r'(?<=[.!?]) +', txt)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences)<=2:
            summary = txt
        else:
            # simple ranking by unique non-stopword count
            stop = {'the','is','in','and','to','a','of','it','for','on','with','as','that','this','are','was','be','by','an','or'}
            scores={}
            for s in sentences:
                words = re.findall(r'\w+', s.lower())
                imp = [w for w in words if w not in stop and len(w)>2]
                scores[s]=len(set(imp))
            ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
            top = set([ranked[0][0], ranked[1][0]])
            ordered = [s for s in sentences if s in top]
            summary = " ".join(ordered)
        set_output_text("Summary:\n" + summary)
        update_info(summary)

    # Buttons grid
    grid = ctk.CTkFrame(tools_card, fg_color="transparent")
    grid.pack(padx=8, pady=8)
    btn_opts = dict(width=180, height=40, corner_radius=8, fg_color=PRIMARY, hover_color=PRIMARY_HOVER)
    ctk.CTkButton(grid, text="Uppercase", command=uppercase, **btn_opts).grid(row=0, column=0, padx=8, pady=8)
    ctk.CTkButton(grid, text="Lowercase", command=lowercase, **btn_opts).grid(row=0, column=1, padx=8, pady=8)
    ctk.CTkButton(grid, text="Title Case", command=titlecase, **btn_opts).grid(row=0, column=2, padx=8, pady=8)

    ctk.CTkButton(grid, text="Word Count", command=wordcount, **btn_opts).grid(row=1, column=0, padx=8, pady=8)
    ctk.CTkButton(grid, text="Remove Duplicates", command=removedups, **btn_opts).grid(row=1, column=1, padx=8, pady=8)
    ctk.CTkButton(grid, text="Extract Emails", command=extract_emails, **btn_opts).grid(row=1, column=2, padx=8, pady=8)

    ctk.CTkButton(grid, text="Extract Phones", command=extract_phones, **btn_opts).grid(row=2, column=0, padx=8, pady=8)
    ctk.CTkButton(grid, text="Summarize", command=summarize, **btn_opts).grid(row=2, column=1, padx=8, pady=8)

    # A small control row under left: populate original text from clipboard or clear
    ctl = ctk.CTkFrame(left, fg_color="transparent")
    ctl.pack(fill="x", padx=6, pady=(6,6))
    def paste_clipboard():
        try:
            txt = frame.clipboard_get()
            original.configure(state="normal")
            original.delete("1.0","end")
            original.insert("1.0", txt)
            original.configure(state="disabled")
            update_info(txt)
        except Exception:
            mb.showinfo("Clipboard", "No text on clipboard.")

    def clear_original():
        original.configure(state="normal"); original.delete("1.0","end"); original.configure(state="disabled")
        set_output_text(""); update_info("")

    ctk.CTkButton(ctl, text="Paste Clipboard", width=140, command=paste_clipboard, fg_color="#6B7280").pack(side="left", padx=6)
    ctk.CTkButton(ctl, text="Clear All", width=120, command=clear_original, fg_color="#EF4444").pack(side="right", padx=6)

    # expose inner controls for parent if needed (not necessary)
    frame._original_widget = original
    frame._output_widget = output
    return frame