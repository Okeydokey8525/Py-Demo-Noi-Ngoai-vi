import tkinter as tk
from tkinter import ttk
import sys, os
from tkinter.font import BOLD

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ui.compaction_tab import CompactionTab
from ui.external_tab import ExternalFragTab
from ui.internal_tab import InternalFragTab

BG      = "#ffffff"
SURFACE = "#1e2430"
ACCENT  = "#58a6ff"
TEXT    = "#e6edf3"


class MainMenu(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg = BG)
        self._build()

    def _build(self):
        # Header
        header = tk.Frame(self, bg=BG, height=52)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        tk.Label(header, text="  🧠 MÔ PHỎNG PHÂN MẢNH BỘ NHỚ - CƠ CHẾ DỒN DỊCH",
                 bg=BG, fg=ACCENT, font=("Segoe UI", 14, "bold"),
                 anchor="w", padx=16).pack(side="left", fill="y")
        tk.Frame(self, bg="#30363d", height=1).pack(fill="x")

        # Notebook
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook",     background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=BG, foreground=ACCENT,
                        font=("Segoe UI", 10, BOLD), padding=[16, 8])
        style.map("TNotebook.Tab",
                  background=[("selected", BG)],
                  foreground=[("selected", ACCENT)])

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        #Tab 
        tab1 = InternalFragTab(nb)
        nb.add(tab1, text="  Phân mảnh nội vi (Internal Fragmentation)  ")

        tab2 = ExternalFragTab(nb)
        nb.add(tab2, text="  Phân mảnh ngoại vi (External Fragmentation)  ")

        tab3 = CompactionTab(nb)
        nb.add(tab3, text="  Dồn dịch bộ nhớ (Compaction)  ")


        # Status bar
        status = tk.Frame(self, bg=SURFACE, height=28)
        status.pack(fill="x", side="bottom")
        status.pack_propagate(False)
        tk.Label(status, text="  ✔  Sẵn sàng",
                 bg=SURFACE, fg="#3fb950", font=("Segoe UI", 9),
                 anchor="w", padx=12).pack(side="left", fill="y")
        tk.Label(status, text="Python " + sys.version.split()[0] + "  |  Tkinter  ",
                 bg="#f1f5f9", fg="#8b949e", font=("Segoe UI", 8),
                 anchor="e", padx=12).pack(side="right", fill="y")


