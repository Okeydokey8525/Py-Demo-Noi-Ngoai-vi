import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.external_fragmentation import first_fit, best_fit, worst_fit, ALGORITHMS

# ─────────────────────── Light-theme Palette ───────────────────────
BG          = "#f5f7fa"
WHITE       = "#ffffff"
SURFACE2    = "#f1f5f9"
BORDER      = "#e2e8f0"
BORDER2     = "#cbd5e1"

ACCENT      = "#6366f1"       # indigo – primary buttons / highlights
ACCENT_DARK = "#4f46e5"
ACCENT_BG   = "#eef2ff"
ACCENT_TXT  = "#4338ca"

ORANGE      = "#f97316"       # reset button
ORANGE_DARK = "#ea6c00"

GREEN       = "#16a34a"
GREEN_BG    = "#f0fdf4"
YELLOW      = "#d97706"
RED         = "#dc2626"
RED_BG      = "#fff1f2"

TEXT        = "#1e293b"
TEXT_MUTED  = "#64748b"
TEXT_LIGHT  = "#94a3b8"

FONT_MONO   = ("Consolas", 9)
FONT_HEAD   = ("Segoe UI", 10, "bold")
FONT_BODY   = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 8)
FONT_TITLE  = ("Segoe UI", 11, "bold")

# Màu accent riêng cho từng thuật toán (light-friendly)
ALGO_ACCENT = {
    "First Fit":  ACCENT,        # indigo
    "Best Fit":   "#16a34a",     # xanh lá
    "Worst Fit":  ORANGE,        # cam
}
ALGO_ACCENT_BG = {
    "First Fit":  ACCENT_BG,
    "Best Fit":   "#f0fdf4",
    "Worst Fit":  "#fff7ed",
}
ALGO_ACCENT_TXT = {
    "First Fit":  ACCENT_TXT,
    "Best Fit":   "#166534",
    "Worst Fit":  "#c2410c",
}

ALGO_DESC = {
    "First Fit":  "Tiến trình được cấp vào khối đầu tiên đủ lớn.",
    "Best Fit":   "Tiến trình được cấp vào khối nhỏ nhất phù hợp.",
    "Worst Fit":  "Tiến trình được cấp vào khối lớn nhất có thể.",
}

BLOCK_COLORS = [
    "#818cf8", "#34d399", "#fb923c", "#c084fc",
    "#60a5fa", "#4ade80", "#fbbf24", "#e879f9",
]


class ExternalFragTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._blocks: list    = []
        self._processes: list = []
        self._results: list   = []
        self._empty: list     = []
        self._algo_var        = tk.StringVar(value="First Fit")

        self._init_style()
        self._build_ui()

    # ──────────────────── Style ────────────────────
    def _init_style(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Light.TFrame",  background=BG)
        s.configure("White.TFrame",  background=WHITE)
        # Treeview
        s.configure("Treeview",
                    background=WHITE, fieldbackground=WHITE,
                    foreground=TEXT, font=FONT_BODY, rowheight=28,
                    borderwidth=0, relief="flat")
        s.configure("Treeview.Heading",
                    background=SURFACE2, foreground=TEXT_MUTED,
                    font=("Segoe UI", 9, "bold"), relief="flat")
        s.map("Treeview",
              background=[("selected", ACCENT_BG)],
              foreground=[("selected", ACCENT)])
        # Combobox
        s.configure("TCombobox", fieldbackground=WHITE, background=WHITE,
                    foreground=TEXT, selectbackground=ACCENT_BG,
                    selectforeground=ACCENT)
        self.configure(style="Light.TFrame")

    # ──────────────────── Outer scroll wrapper ────────────────────
    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        outer = tk.Frame(self, bg=BG)
        outer.grid(row=0, column=0, sticky="nsew")
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)

        cv = tk.Canvas(outer, bg=BG, highlightthickness=0)
        vbar = ttk.Scrollbar(outer, orient="vertical", command=cv.yview)
        cv.configure(yscrollcommand=vbar.set)
        cv.grid(row=0, column=0, sticky="nsew")
        vbar.grid(row=0, column=1, sticky="ns")

        self._sf = tk.Frame(cv, bg=BG)
        self._sf.columnconfigure(0, weight=1)
        cw = cv.create_window((0, 0), window=self._sf, anchor="nw")

        self._sf.bind("<Configure>",
                      lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>",
                lambda e: cv.itemconfig(cw, width=e.width))
        cv.bind_all("<MouseWheel>",
                    lambda e: cv.yview_scroll(-1*(e.delta//120), "units"))

        self._build_content(self._sf)

    # ──────────────────── Content sections ────────────────────
    def _build_content(self, p):
        self._build_banner(p)
        self._build_input(p)
        self._build_ram_map(p)
        self._build_stat_cards(p)
        self._build_detail_stats(p)
        self._build_table_log(p)
        self._build_chart(p)

    # ── 1. Info banner ──
    def _build_banner(self, p):
        algo = self._algo_var.get()
        abg  = ALGO_ACCENT_BG[algo]
        atxt = ALGO_ACCENT_TXT[algo]
        ac   = ALGO_ACCENT[algo]

        self._banner_wrap = tk.Frame(p, bg=abg,
                                     highlightbackground="#c7d2fe",
                                     highlightthickness=1)
        self._banner_wrap.pack(fill="x", padx=16, pady=(14, 0))
        self._banner_stripe = tk.Frame(self._banner_wrap, bg=ac, width=4)
        self._banner_stripe.pack(side="left", fill="y")
        row = tk.Frame(self._banner_wrap, bg=abg)
        row.pack(side="left", fill="x", padx=10, pady=8)
        tk.Label(row, text="Phân mảnh ngoại: ", bg=abg, fg=TEXT,
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Label(row, text="Thuật toán: ", bg=abg, fg=TEXT_MUTED,
                 font=("Segoe UI", 10)).pack(side="left")
        self._banner_algo = tk.Label(row, text=algo, bg=abg,
                                      fg=atxt, font=("Segoe UI", 10, "bold"))
        self._banner_algo.pack(side="left")
        self._banner_desc = tk.Label(row,
                 text=". " + ALGO_DESC[algo],
                 bg=abg, fg=TEXT_MUTED, font=("Segoe UI", 10))
        self._banner_desc.pack(side="left")

    # ── 2. Input controls ──
    def _build_input(self, p):
        card = self._card(p, pady=6)
        r = tk.Frame(card, bg=WHITE)
        r.pack(fill="x", padx=16, pady=12)

        # ── Dòng nhãn ──
        lbl_row = tk.Frame(r, bg=WHITE)
        lbl_row.pack(fill="x", pady=(0, 4))
        self._lbl(lbl_row, "Kích thước khối nhớ (KB)",  width=24, side="left")
        self._lbl(lbl_row, "Kích thước tiến trình (KB)", width=24, side="left", padx=(24, 0))

        # ── Dòng entry ──
        ctl = tk.Frame(r, bg=WHITE)
        ctl.pack(fill="x")

        self.ent_blocks = self._entry_e(ctl, "100, 500, 200, 300, 600", width=22)
        self.ent_blocks.pack(side="left", ipady=5)

        tk.Frame(ctl, bg=BG, width=24).pack(side="left")

        self.ent_procs = self._entry_e(ctl, "212, 417, 112, 426", width=22)
        self.ent_procs.pack(side="left", ipady=5)

        # ── Chọn thuật toán ──
        algo_row = tk.Frame(r, bg=WHITE)
        algo_row.pack(fill="x", pady=(12, 0))
        self._lbl(algo_row, "Thuật toán:", side="left")
        tk.Frame(algo_row, bg=BG, width=10).pack(side="left")

        self._algo_btns = {}
        for algo in ["First Fit", "Best Fit", "Worst Fit"]:
            btn = tk.Button(
                algo_row, text=algo,
                bg=SURFACE2, fg=TEXT_MUTED,
                activebackground=ALGO_ACCENT[algo], activeforeground=WHITE,
                font=("Segoe UI", 9, "bold"), bd=0, relief="flat",
                cursor="hand2", padx=14, pady=5,
                command=lambda a=algo: self._select_algo(a)
            )
            btn.pack(side="left", padx=(0, 6))
            self._algo_btns[algo] = btn
        self._select_algo("First Fit")

        # ── Nút Run / Reset ──
        tk.Frame(r, bg=BORDER, height=1).pack(fill="x", pady=(12, 0))
        btn_row = tk.Frame(r, bg=WHITE)
        btn_row.pack(fill="x", pady=(10, 0))

        tk.Button(btn_row, text="▶  Chạy mô phỏng",
                  bg=ACCENT, fg=WHITE,
                  activebackground=ACCENT_DARK, activeforeground=WHITE,
                  font=("Segoe UI", 10, "bold"), bd=0, relief="flat",
                  cursor="hand2", padx=20, pady=7,
                  command=self._on_run).pack(side="left")

        tk.Frame(btn_row, bg=BG, width=10).pack(side="left")

        tk.Button(btn_row, text="↺  Reset",
                  bg=ORANGE, fg=WHITE,
                  activebackground=ORANGE_DARK, activeforeground=WHITE,
                  font=("Segoe UI", 10, "bold"), bd=0, relief="flat",
                  cursor="hand2", padx=20, pady=7,
                  command=self._on_reset).pack(side="left")

    # ── 3. Memory map ──
    def _build_ram_map(self, p):
        card = self._card(p, pady=6)

        hdr = tk.Frame(card, bg=WHITE)
        hdr.pack(fill="x", padx=16, pady=(10, 6))
        tk.Label(hdr, text="RAM — Phân mảnh ngoại",
                 bg=WHITE, fg=TEXT, font=FONT_HEAD).pack(side="left")
        self.algo_badge = tk.Label(
            hdr, text="First Fit",
            bg=ACCENT_BG, fg=ACCENT_TXT,
            font=("Segoe UI", 8, "bold"), padx=8, pady=2
        )
        self.algo_badge.pack(side="right")

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=16)

        self.canvas = tk.Canvas(card, bg=WHITE, height=130,
                                 highlightthickness=0, bd=0)
        self.canvas.pack(fill="x", padx=16, pady=10)
        self.canvas.bind("<Configure>", lambda e: self._draw_memory_map())

    # ── 4. Big stat cards ──
    def _build_stat_cards(self, p):
        row = tk.Frame(p, bg=BG)
        row.pack(fill="x", padx=16, pady=(0, 6))
        row.columnconfigure(0, weight=1)
        row.columnconfigure(1, weight=1)
        row.columnconfigure(2, weight=1)

        self._sc_total  = self._big_card(row, col=0, label="TỔNG BỘ NHỚ",
                                          value="— KB", color=TEXT)
        self._sc_alloc  = self._big_card(row, col=1, label="ĐÃ CẤP PHÁT",
                                          value="0 KB",  color=ACCENT)
        self._sc_remain = self._big_card(row, col=2, label="CÒN TRỐNG",
                                          value="— KB",  color=GREEN)

    # ── 5. Detailed stats ──
    def _build_detail_stats(self, p):
        card = self._card(p, pady=6)

        hdr = tk.Frame(card, bg=WHITE)
        hdr.pack(fill="x", padx=16, pady=(10, 6))
        tk.Label(hdr, text="📊  Chi tiết thống kê",
                 bg=WHITE, fg=TEXT, font=FONT_HEAD).pack(side="left")
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=16)

        grid = tk.Frame(card, bg=WHITE)
        grid.pack(fill="x", padx=16, pady=10)

        stats_defs = [
            ("algo",         "Thuật toán"),
            ("blocks",       "Số khối nhớ"),
            ("procs",        "Số tiến trình"),
            ("total_mem",    "Tổng bộ nhớ"),
            ("total_alloc",  "Đã cấp phát"),
            ("total_remain", "Còn lại (tổng)"),
            ("unalloc",      "Không cấp được"),
        ]
        self._stat_labels = {}
        cols = 4
        for i, (key, label) in enumerate(stats_defs):
            c     = i % cols
            r_row = i // cols
            cell = tk.Frame(grid, bg=SURFACE2,
                             highlightbackground=BORDER, highlightthickness=1)
            cell.grid(row=r_row, column=c, sticky="ew",
                      padx=(0 if c == 0 else 4, 0),
                      pady=(0 if r_row == 0 else 4, 0))
            grid.columnconfigure(c, weight=1)
            inner = tk.Frame(cell, bg=SURFACE2, pady=6, padx=10)
            inner.pack(fill="both")
            tk.Label(inner, text=label, bg=SURFACE2, fg=TEXT_MUTED,
                     font=FONT_SMALL, anchor="w").pack(fill="x")
            val = tk.Label(inner, text="—", bg=SURFACE2, fg=ACCENT,
                           font=("Segoe UI", 13, "bold"), anchor="w")
            val.pack(fill="x")
            self._stat_labels[key] = val

    # ── 6. Table + Log ──
    def _build_table_log(self, p):
        wrap = tk.Frame(p, bg=BG)
        wrap.pack(fill="both", expand=True, padx=16, pady=(0, 6))
        wrap.columnconfigure(0, weight=3)
        wrap.columnconfigure(1, weight=2)
        wrap.rowconfigure(0, weight=1)

        # Table
        tbl_card = tk.Frame(wrap, bg=WHITE,
                             highlightbackground=BORDER, highlightthickness=1)
        tbl_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        tk.Label(tbl_card, text="📋  Kết quả cấp phát",
                 bg=WHITE, fg=TEXT, font=FONT_HEAD,
                 padx=14, pady=9, anchor="w").pack(fill="x")
        tk.Frame(tbl_card, bg=BORDER, height=1).pack(fill="x")

        cols = ("TT", "T.Trình", "Y/cầu(KB)", "Khối số", "Còn lại(KB)", "Tình trạng")
        self.tree = ttk.Treeview(tbl_card, columns=cols, show="headings", height=8)
        for col, w in zip(cols, [32, 72, 76, 64, 80, 90]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center", stretch=True)
        self.tree.tag_configure("ok",   background=GREEN_BG, foreground=GREEN)
        self.tree.tag_configure("fail", background=RED_BG,   foreground=RED)
        sb = ttk.Scrollbar(tbl_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=8)
        sb.pack(side="right", fill="y", pady=8, padx=(0, 4))

        # Log
        log_card = tk.Frame(wrap, bg=WHITE,
                             highlightbackground=BORDER, highlightthickness=1)
        log_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        tk.Label(log_card, text="📜  Quá trình chạy",
                 bg=WHITE, fg=TEXT, font=FONT_HEAD,
                 padx=14, pady=9, anchor="w").pack(fill="x")
        tk.Frame(log_card, bg=BORDER, height=1).pack(fill="x")
        self.log_box = scrolledtext.ScrolledText(
            log_card, bg=SURFACE2, fg=TEXT, font=FONT_MONO,
            insertbackground=TEXT, borderwidth=0, wrap=tk.WORD,
            state="disabled", height=10
        )
        self.log_box.pack(fill="both", expand=True, padx=8, pady=8)
        for tag, color in [
            ("ok",   GREEN),
            ("fail", RED),
            ("info", TEXT_MUTED),
            ("head", ACCENT_TXT),
            ("sep",  BORDER2),
            ("ff",   ALGO_ACCENT["First Fit"]),
            ("bf",   ALGO_ACCENT["Best Fit"]),
            ("wf",   ALGO_ACCENT["Worst Fit"]),
        ]:
            self.log_box.tag_config(tag, foreground=color)

    # ── 7. Chart ──
    def _build_chart(self, p):
        card = tk.Frame(p, bg=WHITE,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", padx=16, pady=(0, 18))
        tk.Label(card, text="📈  Biểu đồ phân bổ bộ nhớ (KB)",
                 bg=WHITE, fg=TEXT, font=FONT_HEAD,
                 padx=14, pady=9, anchor="w").pack(fill="x")
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x")
        self.chart_canvas = tk.Canvas(card, bg=WHITE, height=160,
                                       highlightthickness=0, bd=0)
        self.chart_canvas.pack(fill="x", padx=14, pady=10)
        self.chart_canvas.bind("<Configure>", lambda e: self._draw_chart())

    # ──────────────────── Helpers ────────────────────
    def _card(self, parent, pady=8):
        f = tk.Frame(parent, bg=WHITE,
                     highlightbackground=BORDER, highlightthickness=1)
        f.pack(fill="x", padx=16, pady=(0, pady))
        return f

    def _big_card(self, parent, col, label, value, color):
        pad_l = 0 if col == 0 else 5
        pad_r = 5 if col < 2 else 0
        f = tk.Frame(parent, bg=WHITE,
                     highlightbackground=BORDER, highlightthickness=1)
        f.grid(row=0, column=col, sticky="ew", padx=(pad_l, pad_r), pady=2)
        inner = tk.Frame(f, bg=WHITE, pady=16, padx=20)
        inner.pack(fill="both", expand=True)
        val_lbl = tk.Label(inner, text=value, bg=WHITE, fg=color,
                           font=("Segoe UI", 22, "bold"))
        val_lbl.pack()
        tk.Label(inner, text=label, bg=WHITE, fg=TEXT_MUTED,
                 font=("Segoe UI", 8, "bold")).pack()
        return val_lbl

    def _lbl(self, parent, text, width=None, side="left", padx=(0, 0)):
        tk.Label(parent, text=text, bg=WHITE, fg=TEXT_MUTED,
                 font=FONT_SMALL, width=width, anchor="w").pack(
            side=side, padx=padx)

    def _entry_e(self, parent, placeholder="", width=20):
        """Entry với placeholder text, dùng cho ô nhập tự do."""
        e = tk.Entry(parent, bg=WHITE, fg=TEXT, insertbackground=TEXT,
                     font=FONT_BODY, bd=1, relief="solid",
                     highlightbackground=BORDER, highlightcolor=ACCENT,
                     highlightthickness=1, width=width)
        e.insert(0, placeholder)
        return e

    def _log(self, msg, tag="info"):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n", tag)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _pcolor(self, idx: int) -> str:
        return BLOCK_COLORS[idx % len(BLOCK_COLORS)]

    def _select_algo(self, algo: str):
        self._algo_var.set(algo)
        ac = ALGO_ACCENT[algo]
        for name, btn in self._algo_btns.items():
            if name == algo:
                btn.configure(bg=ac, fg=WHITE)
            else:
                btn.configure(bg=SURFACE2, fg=TEXT_MUTED)
        self._update_banner()

    def _update_banner(self):
        algo = self._algo_var.get()
        abg  = ALGO_ACCENT_BG[algo]
        atxt = ALGO_ACCENT_TXT[algo]
        ac   = ALGO_ACCENT[algo]
        self._banner_wrap.configure(bg=abg)
        self._banner_stripe.configure(bg=ac)
        for w in self._banner_wrap.winfo_children():
            if isinstance(w, tk.Frame) and w != self._banner_stripe:
                w.configure(bg=abg)
                for lbl in w.winfo_children():
                    if isinstance(lbl, tk.Label):
                        lbl.configure(bg=abg)
        self._banner_algo.configure(text=algo, bg=abg, fg=atxt)
        self._banner_desc.configure(text=". " + ALGO_DESC[algo], bg=abg)
      
        if hasattr(self, "algo_badge"):
            self.algo_badge.configure(
                text=algo,
                bg=ALGO_ACCENT_BG[algo],
                fg=ALGO_ACCENT_TXT[algo]
            )

    # ──────────────────── Actions ────────────────────
    def _parse_list(self, raw: str) -> list:
        return [int(x.strip()) for x in raw.split(",") if x.strip()]

    def _on_run(self):
        try:
            blocks = self._parse_list(self.ent_blocks.get())
            procs  = self._parse_list(self.ent_procs.get())
            if not blocks or not procs:
                raise ValueError
            if any(v <= 0 for v in blocks + procs):
                raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi nhập liệu",
                "Vui lòng nhập danh sách số nguyên dương, cách nhau dấu phẩy.")
            return

        algo_name = self._algo_var.get()
        algo_fn   = ALGORITHMS[algo_name]
        results, empty_space = algo_fn(blocks, procs)

        self._blocks    = blocks
        self._processes = procs
        self._results   = results
        self._empty     = empty_space

        self._update_banner()

        # Log
        tag_map = {"First Fit": "ff", "Best Fit": "bf", "Worst Fit": "wf"}
        atag    = tag_map[algo_name]

        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

        self._log("══════════════════════════", "sep")
        self._log(f"  Thuật toán : {algo_name}", atag)
        self._log(f"  Khối nhớ  : {blocks}", "head")
        self._log(f"  Tiến trình: {procs}", "head")
        self._log("══════════════════════════", "sep")

        for r in results:
            pid  = r["process"]
            size = r["size"]
            if r["block"] is not None:
                self._log(
                    f"  ✔ P{pid} ({size}KB) → Khối {r['block']} | còn = {r['remain']}KB",
                    "ok")
            else:
                self._log(
                    f"  ✘ P{pid} ({size}KB) → Không tìm được khối phù hợp",
                    "fail")

        self._log("──────────────────────────", "sep")
        self._log(f"  Không gian còn lại: {empty_space}", "info")
        self._log("══════════════════════════", "sep")

        self._refresh()

    def _on_reset(self):
        self._blocks    = []
        self._processes = []
        self._results   = []
        self._empty     = []
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")
        self._log("↺ Đã reset. Nhập dữ liệu mới và nhấn ▶ Chạy.", "head")
        self._refresh()

    # ──────────────────── Refresh ────────────────────
    def _refresh(self):
        self._update_table()
        self._update_stats()
        self._draw_memory_map()
        self._draw_chart()

    def _update_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for r in self._results:
            ok  = r["block"] is not None
            tag = "ok" if ok else "fail"
            self.tree.insert("", "end", tags=(tag,), values=(
                r["process"],
                f"P{r['process']}",
                f"{r['size']} KB",
                str(r["block"]) if ok else "—",
                f"{r['remain']} KB" if ok else "—",
                "✔ Cấp phát" if ok else "✘ Thất bại",
            ))

    def _update_stats(self):
        if not self._results:
            for lbl in self._stat_labels.values():
                lbl.configure(text="—", fg=ACCENT)
            self._sc_total.configure( text="— KB",  fg=TEXT)
            self._sc_alloc.configure( text="0 KB",   fg=ACCENT)
            self._sc_remain.configure(text="— KB",  fg=GREEN)
            return

        algo_name    = self._algo_var.get()
        alloc        = [r for r in self._results if r["block"] is not None]
        ua           = [r for r in self._results if r["block"] is None]
        total_mem    = sum(self._blocks)
        total_alloc  = sum(r["size"] for r in alloc)
        total_remain = sum(self._empty)

        # Big cards
        self._sc_total.configure( text=f"{total_mem} KB",    fg=TEXT)
        self._sc_alloc.configure( text=f"{total_alloc} KB",  fg=ACCENT)
        rc = GREEN if total_remain < total_mem * 0.3 else (YELLOW if total_remain < total_mem * 0.6 else RED)
        self._sc_remain.configure(text=f"{total_remain} KB", fg=rc)

        # Detail stats
        ac = ALGO_ACCENT[algo_name]
        self._stat_labels["algo"].configure(       text=algo_name,           fg=ac)
        self._stat_labels["blocks"].configure(     text=str(len(self._blocks)),   fg=TEXT)
        self._stat_labels["procs"].configure(      text=str(len(self._processes)),fg=TEXT)
        self._stat_labels["total_mem"].configure(  text=f"{total_mem} KB",        fg=TEXT)
        self._stat_labels["total_alloc"].configure(text=f"{total_alloc} KB",      fg=TEXT)
        self._stat_labels["total_remain"].configure(text=f"{total_remain} KB",    fg=rc)
        uc = GREEN if not ua else RED
        self._stat_labels["unalloc"].configure(    text=str(len(ua)),             fg=uc)

    def _draw_memory_map(self):
        self.canvas.delete("all")
        if not self._blocks:
            self.canvas.create_text(
                300, 55,
                text="Chưa có dữ liệu. Nhập dữ liệu và nhấn ▶ Chạy.",
                fill=TEXT_LIGHT, font=FONT_BODY)
            return

        total   = sum(self._blocks)
        w       = self.canvas.winfo_width() or 700
        H       = 125
        mx, my0, my1 = 14, 14, 88
        usable  = w - 2 * mx

        block_state = {}
        for r in self._results:
            if r["block"] is not None:
                bidx = r["block"] - 1
                block_state.setdefault(bidx, []).append(r)

        x = mx
        for i, orig in enumerate(self._blocks):
            bw     = max(int(orig / total * usable), 6)
            remain = self._empty[i] if self._empty else orig
            used   = orig - remain

            if used > 0:
                processes_in = block_state.get(i, [])
                slot_x = x
                for pr in processes_in:
                    pw    = max(int(pr["size"] / orig * bw), 2)
                    color = self._pcolor(pr["process"] - 1)
                    self.canvas.create_rectangle(slot_x, my0, slot_x + pw, my1,
                                                 fill=color, outline="")
                    if pw > 22:
                        self.canvas.create_text(
                            slot_x + pw // 2, (my0 + my1) // 2,
                            text=f"P{pr['process']}", fill=WHITE,
                            font=("Segoe UI", 8, "bold"))
                    slot_x += pw

                if remain > 0:
                    rw = bw - (slot_x - x)
                    if rw > 0:
                        self.canvas.create_rectangle(slot_x, my0, slot_x + rw, my1,
                                                     fill=SURFACE2, outline="")
                        if rw > 22:
                            self.canvas.create_text(
                                slot_x + rw // 2, (my0 + my1) // 2,
                                text=f"{remain}", fill=TEXT_MUTED,
                                font=FONT_SMALL)
                self.canvas.create_rectangle(x, my0, x + bw, my1,
                                             fill="", outline=BORDER2, width=1)
            else:
                self.canvas.create_rectangle(x, my0, x + bw, my1,
                                             fill=SURFACE2, outline=BORDER2, width=1)
                if bw > 28:
                    self.canvas.create_text(
                        x + bw // 2, (my0 + my1) // 2,
                        text=f"FREE\n{orig}KB",
                        fill=TEXT_LIGHT, font=FONT_SMALL)

            self.canvas.create_text(
                x + bw // 2, my1 + 9,
                text=str(orig), fill=TEXT_MUTED, font=FONT_SMALL)
            x += bw

        # Legend
        lx, ly = mx, my1 + 26
        for color, label in [
            (BLOCK_COLORS[0], "Đã cấp phát"),
            (SURFACE2,        "Còn trống"),
        ]:
            self.canvas.create_rectangle(
                lx, ly - 6, lx + 10, ly + 2,
                fill=color, outline=BORDER2)
            self.canvas.create_text(
                lx + 13, ly - 2, text=label,
                fill=TEXT_MUTED, font=FONT_SMALL, anchor="w")
            lx += 100

    def _draw_chart(self):
        self.chart_canvas.delete("all")
        data = [r for r in self._results if r["block"] is not None]
        if not data:
            self.chart_canvas.create_text(
                300, 75,
                text="Chưa có dữ liệu để vẽ biểu đồ.",
                fill=TEXT_LIGHT, font=FONT_BODY)
            return

        w   = self.chart_canvas.winfo_width() or 700
        H   = 155
        ml, mr, mb, mt = 52, 16, 30, 22
        cw  = w - ml - mr
        ch  = H - mb - mt
        n   = len(data)
        sp  = cw / n
        bw  = max(min(int(sp * 0.35), 48), 8)
        remain_vals = [r["remain"] for r in data if r["remain"] is not None]
        mx_ = max(
            max(r["size"] for r in data),
            max(remain_vals) if remain_vals else 1,
            1
        )

        # Axes
        self.chart_canvas.create_line(ml, mt, ml, H - mb, fill=BORDER2, width=1)
        self.chart_canvas.create_line(ml, H - mb, w - mr, H - mb, fill=BORDER2, width=1)

        # Grid + Y labels
        for i in range(5):
            val = int(mx_ * i / 4)
            y   = H - mb - int(ch * i / 4)
            self.chart_canvas.create_line(
                ml, y, w - mr, y, fill=BORDER, dash=(2, 4), width=1)
            self.chart_canvas.create_text(
                ml - 4, y, text=str(val),
                fill=TEXT_MUTED, font=("Segoe UI", 7), anchor="e")

        for idx, r in enumerate(data):
            cx    = ml + int(sp * (idx + 0.5))
            color = self._pcolor(r["process"] - 1)

            # Bar: size requested
            ah = max(int(ch * r["size"] / mx_), 2)
            self.chart_canvas.create_rectangle(
                cx - bw, H - mb - ah, cx, H - mb,
                fill=color, outline="")
            self.chart_canvas.create_text(
                cx - bw // 2, H - mb - ah - 6,
                text=str(r["size"]), fill=color, font=("Segoe UI", 7))

            # Bar: remain
            if r["remain"] is not None and r["remain"] > 0:
                rh = max(int(ch * r["remain"] / mx_), 1)
                self.chart_canvas.create_rectangle(
                    cx + 2, H - mb - rh, cx + bw + 2, H - mb,
                    fill=YELLOW, outline="")
                self.chart_canvas.create_text(
                    cx + bw // 2 + 2, H - mb - rh - 6,
                    text=str(r["remain"]), fill=YELLOW, font=("Segoe UI", 7))

            self.chart_canvas.create_text(
                cx, H - mb + 10, text=f"P{r['process']}",
                fill=TEXT_MUTED, font=("Segoe UI", 7))

        # Legend
        lx, ly = ml, mt - 6
        self.chart_canvas.create_rectangle(lx, ly, lx + 8, ly + 8,
                                            fill=ACCENT, outline="")
        self.chart_canvas.create_text(lx + 11, ly + 4, text="Y/cầu (KB)",
                                       fill=TEXT_MUTED, font=("Segoe UI", 7),
                                       anchor="w")
        lx += 85
        self.chart_canvas.create_rectangle(lx, ly, lx + 8, ly + 8,
                                            fill=YELLOW, outline="")
        self.chart_canvas.create_text(lx + 11, ly + 4,
                                       text="Còn lại trong khối (KB)",
                                       fill=TEXT_MUTED, font=("Segoe UI", 7),
                                       anchor="w")