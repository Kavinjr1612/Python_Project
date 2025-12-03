# ----------------------------------------------
# module_dataanalysis.py  (FINAL FULL VERSION)
# Polished UI + Date Filter Panel + Auto Recommend
# ----------------------------------------------

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

from ui_theme import CARD_BG, TEXTBOX_BG, PRIMARY, PRIMARY_HOVER, TEXT_COLOR, apply_theme

apply_theme()

# Safe matplotlib style
try:
    plt.style.use("seaborn-v0_8-darkgrid")
except:
    try:
        plt.style.use("seaborn-darkgrid")
    except:
        plt.style.use("ggplot")


# ==========================================================
# MAIN FUNCTION
# ==========================================================
def create_dataanalysis_screen(root, go_back_callback):

    # Scroll container to avoid clipping
    scroll = ctk.CTkScrollableFrame(root, fg_color="transparent")
    scroll.pack(fill="both", expand=True)

    frame = ctk.CTkFrame(scroll, fg_color="transparent")
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    frame._df = None
    frame._history = []
    frame._canvas = None

    # ==========================================================
    # Utility Functions
    # ==========================================================
    def clear_plot_area():
        if frame._canvas:
            try:
                frame._canvas.get_tk_widget().destroy()
            except:
                pass
        frame._canvas = None

    def update_preview():
        preview_box.configure(state="normal")
        preview_box.delete("1.0", "end")
        if frame._df is None:
            preview_box.insert("end", "No dataset loaded.")
        else:
            try:
                preview_box.insert("end", frame._df.head(60).to_string())
            except:
                preview_box.insert("end", str(frame._df.head(60)))
        preview_box.configure(state="disabled")

    def update_info():
        if frame._df is None:
            info_label.configure(text="Rows: 0\nColumns: 0\nMissing: 0")
            return
        df = frame._df
        missing = df.isna().sum().sum()
        info_label.configure(text=(
            f"Rows: {len(df)}\n"
            f"Columns: {len(df.columns)}\n"
            f"Missing: {missing}"
        ))

    def refresh_selectors():
        if frame._df is None:
            column_select.configure(values=[])
            group_select.configure(values=["None"])
            return
        cols = list(frame._df.columns.astype(str))
        column_select.configure(values=cols)
        group_select.configure(values=["None"] + cols)

    def push_history():
        if frame._df is not None:
            try:
                frame._history.append(frame._df.copy())
                if len(frame._history) > 15:
                    frame._history.pop(0)
            except:
                pass

    def undo_last():
        if not frame._history:
            messagebox.showinfo("Undo", "Nothing to undo.")
            return
        frame._df = frame._history.pop()
        update_preview()
        update_info()
        refresh_selectors()

    # ==========================================================
    # Load / Export
    # ==========================================================
    def load_csv():
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not path:
            return
        try:
            df = pd.read_csv(path)
            frame._df = df
            update_preview()
            update_info()
            refresh_selectors()
        except Exception as e:
            messagebox.showerror("Error loading CSV", str(e))

    def load_excel():
        path = filedialog.askopenfilename(filetypes=[("Excel", "*.xlsx;*.xls")])
        if not path:
            return
        try:
            df = pd.read_excel(path)
            frame._df = df
            update_preview()
            update_info()
            refresh_selectors()
        except Exception as e:
            messagebox.showerror("Error loading Excel", str(e))

    def export_csv():
        if frame._df is None:
            messagebox.showinfo("Export", "No dataset loaded.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV", "*.csv")])
        if not path:
            return
        try:
            frame._df.to_csv(path, index=False)
            messagebox.showinfo("Export", f"Saved to {path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    # ==========================================================
    # Cleaning Tools
    # ==========================================================
    def remove_empty_rows():
        if frame._df is None: return
        push_history()
        frame._df = frame._df.dropna(how="all").reset_index(drop=True)
        update_preview(); update_info()

    def remove_empty_columns():
        if frame._df is None: return
        push_history()
        frame._df = frame._df.dropna(axis=1, how="all")
        update_preview(); update_info(); refresh_selectors()

    def drop_rows_na():
        if frame._df is None: return
        push_history()
        frame._df = frame._df.dropna().reset_index(drop=True)
        update_preview(); update_info()

    def fill_na():
        if frame._df is None: return
        val = simpledialog.askstring("Fill NA", "Enter replacement value:")
        if val is None: return
        push_history()
        frame._df = frame._df.fillna(val)
        update_preview(); update_info()

    def remove_duplicates():
        if frame._df is None: return
        push_history()
        frame._df = frame._df.drop_duplicates().reset_index(drop=True)
        update_preview(); update_info()

    def trim_text():
        if frame._df is None: return
        push_history()
        for col in frame._df.select_dtypes(include="object"):
            frame._df[col] = frame._df[col].astype(str).str.strip()
        update_preview(); update_info()

    def rename_column():
        if frame._df is None: return
        old = simpledialog.askstring("Rename Column", "Old name:")
        if not old or old not in frame._df.columns:
            return
        new = simpledialog.askstring("Rename Column", "New name:")
        if not new: return
        push_history()
        frame._df = frame._df.rename(columns={old: new})
        update_preview(); update_info(); refresh_selectors()

    def convert_type():
        if frame._df is None: return
        col = simpledialog.askstring("Convert Type", "Column name:")
        if not col or col not in frame._df.columns:
            return
        dtype = simpledialog.askstring("Data Type", "int, float, str, datetime:")
        if not dtype: return
        push_history()
        try:
            if dtype == "datetime":
                frame._df[col] = pd.to_datetime(frame._df[col], errors="coerce")
            else:
                frame._df[col] = frame._df[col].astype(dtype)
        except Exception as e:
            messagebox.showerror("Conversion Error", str(e))
        update_preview(); update_info()

    def filter_rows():
        if frame._df is None: return
        cond = simpledialog.askstring("Filter Rows", "Enter query (e.g., Age > 30):")
        if not cond: return
        push_history()
        try:
            frame._df = frame._df.query(cond).reset_index(drop=True)
            update_preview(); update_info(); refresh_selectors()
        except Exception as e:
            messagebox.showerror("Filter Error", str(e))

    # ==========================================================
    # Auto Recommend
    # ==========================================================
    def auto_recommend():
        if frame._df is None:
            messagebox.showinfo("No Data", "Load a dataset first.")
            return

        df = frame._df
        chart_type = chart_select.get()

        numeric = list(df.select_dtypes(include="number").columns)
        categorical = list(df.select_dtypes(include="object").columns)

        best_num = numeric[0] if numeric else None
        best_cat = categorical[0] if categorical else None

        if chart_type == "pie":
            if best_cat:
                column_select.set(best_cat)
                group_select.set("None")
                agg_select.set("count")
                messagebox.showinfo("Recommended", f"Pie → {best_cat}")
            else:
                messagebox.showinfo("Recommendation", "No categorical columns.")
            return

        if chart_type == "bar":
            if best_num and best_cat:
                column_select.set(best_num)
                group_select.set(best_cat)
                agg_select.set("mean")
                messagebox.showinfo("Recommended", f"Bar → {best_cat} vs {best_num}")
            return

        if chart_type == "line":
            if best_num:
                column_select.set(best_num)
                group_select.set("None")
                agg_select.set("sum")
                messagebox.showinfo("Recommended", f"Line → {best_num}")
            return

        if chart_type == "hist":
            if best_num:
                column_select.set(best_num)
                agg_select.set("count")
                messagebox.showinfo("Recommended", f"Histogram → {best_num}")
            return

        if chart_type == "box":
            if best_num:
                column_select.set(best_num)
                messagebox.showinfo("Recommended", f"Box → {best_num}")
            return

        if chart_type == "heatmap":
            if len(numeric) >= 2:
                messagebox.showinfo("Recommended", "Heatmap → numeric correlations")
            return

    # ==========================================================
    # Date Filter (UI-based)
    # ==========================================================
    def filter_by_date_panel():
        if frame._df is None:
            messagebox.showinfo("No Data", "Load a dataset first.")
            return
        if "Date" not in frame._df.columns:
            messagebox.showwarning("Missing Column", "Dataset must contain 'Date' column.")
            return

        start = start_date_entry.get().strip()
        end = end_date_entry.get().strip()

        if not start or not end:
            messagebox.showwarning("Invalid Input", "Enter both start and end date.")
            return

        try:
            push_history()
            frame._df["Date"] = pd.to_datetime(frame._df["Date"], errors="coerce")

            start_dt = pd.to_datetime(start)
            end_dt = pd.to_datetime(end)

            filtered = frame._df[(frame._df["Date"] >= start_dt) &
                                 (frame._df["Date"] <= end_dt)]
            frame._df = filtered.reset_index(drop=True)

            update_preview()
            update_info()
            refresh_selectors()

            messagebox.showinfo("Filtered", f"Filtered rows from {start_dt.date()} to {end_dt.date()}")

        except Exception as e:
            messagebox.showerror("Date Error", str(e))

    # ==========================================================
    # Chart Generation
    # ==========================================================
    def generate_chart():
        if frame._df is None:
            messagebox.showinfo("No Data", "Load a dataset first.")
            return

        df = frame._df
        ctype = chart_select.get()
        col = column_select.get()
        group = group_select.get()
        agg = agg_select.get()
        embed = embed_var.get()

        if group == "None":
            group = None

        clear_plot_area()
        fig, ax = plt.subplots(figsize=(10, 5))

        try:
            # PIE Chart
            if ctype == "pie":
                if not col:
                    messagebox.showinfo("Select Column", "Choose a column for Pie chart.")
                    plt.close(fig); return
                if pd.api.types.is_numeric_dtype(df[col]) and group:
                    grouped = getattr(df.groupby(group)[col], agg)()
                    ax.pie(grouped.values, labels=grouped.index, autopct="%1.1f%%")
                    ax.set_title(f"{agg.capitalize()} of {col} by {group}")
                else:
                    counts = df[col].value_counts()
                    ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%")
                    ax.set_title(f"Distribution of {col}")

            # BAR Chart
            elif ctype == "bar":
                if not col:
                    plt.close(fig); return
                if group:
                    grouped = getattr(df.groupby(group)[col], agg)()
                    ax.bar(grouped.index.astype(str), grouped.values)
                    plt.setp(ax.get_xticklabels(), rotation=40, ha="right")
                else:
                    counts = df[col].value_counts()
                    ax.bar(counts.index.astype(str), counts.values)
                    plt.setp(ax.get_xticklabels(), rotation=40, ha="right")
                ax.set_title(f"Bar Chart - {col}")

            # LINE Chart
            elif ctype == "line":
                if not col:
                    plt.close(fig); return
                if group:
                    grouped = getattr(df.groupby(group)[col], agg)()
                    ax.plot(grouped.index.astype(str), grouped.values, marker="o")
                    plt.setp(ax.get_xticklabels(), rotation=40, ha="right")
                    ax.set_title(f"{agg.capitalize()} of {col} by {group}")
                else:
                    ax.plot(df[col].dropna().values, marker="o")
                    ax.set_title(f"Line Chart - {col}")

            # HISTOGRAM
            elif ctype == "hist":
                if not col:
                    plt.close(fig); return
                ax.hist(df[col].dropna(), bins=20)
                ax.set_title(f"Histogram - {col}")

            # BOX Plot
            elif ctype == "box":
                if not col:
                    plt.close(fig); return
                ax.boxplot(df[col].dropna())
                ax.set_title(f"Box Plot - {col}")

            # HEATMAP
            elif ctype == "heatmap":
                num = df.select_dtypes(include="number")
                if num.shape[1] < 2:
                    plt.close(fig); return
                corr = num.corr()
                sns.heatmap(corr, annot=True, cmap="Blues", ax=ax)
                ax.set_title("Correlation Heatmap")

        except Exception as e:
            plt.close(fig)
            messagebox.showerror("Plot Error", str(e))
            return

        # Embed or popup
        if embed:
            canvas = FigureCanvasTkAgg(fig, master=plot_area)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            frame._canvas = canvas
        else:
            popup = tk.Toplevel(root)
            popup.geometry("1000x700")
            canvas = FigureCanvasTkAgg(fig, master=popup)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

    # ==========================================================
    # UI Layout
    # ==========================================================

    # Header
    header = ctk.CTkFrame(frame, fg_color="transparent")
    header.pack(fill="x", pady=(0, 10))

    ctk.CTkLabel(
        header, text="Data Analysis Toolkit", 
        font=("Segoe UI", 24, "bold")
    ).pack(side="left")

    ctk.CTkButton(
        header, text="Back", width=100,
        fg_color=PRIMARY, hover_color=PRIMARY_HOVER,
        command=lambda: [frame.destroy(), go_back_callback()]
    ).pack(side="right")

    # Body split
    body = ctk.CTkFrame(frame, fg_color="transparent")
    body.pack(fill="both", expand=True)

    # LEFT PANEL
    left = ctk.CTkFrame(body, fg_color="transparent")
    left.pack(side="left", fill="y", padx=10)

    # Preview
    preview_box = ctk.CTkTextbox(
        left, width=500, height=550,
        fg_color=TEXTBOX_BG, text_color=TEXT_COLOR,
        font=("Consolas", 12)
    )
    preview_box.pack(pady=5)

    # Load row
    load_row = ctk.CTkFrame(left, fg_color="transparent")
    load_row.pack(pady=10)

    ctk.CTkButton(load_row, text="Load CSV", width=120, command=load_csv).pack(side="left", padx=5)
    ctk.CTkButton(load_row, text="Load Excel", width=120, command=load_excel).pack(side="left", padx=5)
    ctk.CTkButton(load_row, text="Export CSV", width=120, command=export_csv).pack(side="left", padx=5)

    info_label = ctk.CTkLabel(left, text="Rows: 0\nColumns: 0\nMissing: 0")
    info_label.pack(pady=10)

    ctk.CTkLabel(left, text="Cleaning Tools", font=("Segoe UI", 16, "bold")).pack()

    clean_tools = [
        ("Remove Empty Rows", remove_empty_rows),
        ("Remove Empty Columns", remove_empty_columns),
        ("Drop Rows NA", drop_rows_na),
        ("Fill NA", fill_na),
        ("Remove Duplicates", remove_duplicates),
        ("Trim Text", trim_text),
        ("Rename Column", rename_column),
        ("Convert Type", convert_type),
        ("Filter Rows", filter_rows),
        ("Undo", undo_last)
    ]

    for name, fn in clean_tools:
        ctk.CTkButton(left, text=name, width=260, fg_color="#3C4153",
                      hover_color="#2D3140", command=fn).pack(pady=3)

    # RIGHT PANEL
    right = ctk.CTkFrame(body, fg_color="transparent")
    right.pack(side="left", fill="both", expand=True, padx=10)

    # Chart controls
    ctrl = ctk.CTkFrame(right, fg_color="transparent")
    ctrl.pack(fill="x", pady=(5, 5))

    chart_select = ctk.CTkComboBox(ctrl, values=["bar", "line", "pie", "hist", "box", "heatmap"], width=120)
    chart_select.set("bar")
    chart_select.pack(side="left", padx=5)

    ctk.CTkButton(ctrl, text="Auto Recommend", width=140,
                  fg_color="#4B7BE5", hover_color="#3860C4",
                  command=auto_recommend).pack(side="left", padx=5)

    column_select = ctk.CTkComboBox(ctrl, values=[], width=150)
    column_select.pack(side="left", padx=5)

    group_select = ctk.CTkComboBox(ctrl, values=["None"], width=150)
    group_select.set("None")
    group_select.pack(side="left", padx=5)

    agg_select = ctk.CTkComboBox(ctrl, values=["sum", "mean", "count"], width=100)
    agg_select.set("sum")
    agg_select.pack(side="left", padx=5)

    embed_var = tk.BooleanVar(value=True)
    ctk.CTkCheckBox(ctrl, text="Embed", variable=embed_var).pack(side="left", padx=5)

    ctk.CTkButton(ctrl, text="Generate", width=120,
                  fg_color=PRIMARY, hover_color=PRIMARY_HOVER,
                  command=generate_chart).pack(side="left", padx=5)

    # DATE FILTER PANEL
    date_panel = ctk.CTkFrame(right, fg_color="transparent")
    date_panel.pack(fill="x", pady=(5, 10))

    ctk.CTkLabel(date_panel, text="Start Date (YYYY-MM-DD):").pack(side="left", padx=5)
    start_date_entry = ctk.CTkEntry(date_panel, width=150)
    start_date_entry.pack(side="left", padx=5)

    ctk.CTkLabel(date_panel, text="End Date:").pack(side="left", padx=5)
    end_date_entry = ctk.CTkEntry(date_panel, width=150)
    end_date_entry.pack(side="left", padx=5)

    ctk.CTkButton(date_panel, text="Apply Date Filter", width=160,
                  fg_color="#4B7BE5", hover_color="#3860C4",
                  command=filter_by_date_panel).pack(side="left", padx=5)

    # Plot Area
    plot_area = ctk.CTkFrame(right, fg_color=CARD_BG)
    plot_area.pack(fill="both", expand=True, pady=5)

    return frame
