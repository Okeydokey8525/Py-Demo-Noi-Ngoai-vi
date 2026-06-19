import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.internal_fragmentation import internal_fragment

# ─────────────────────── Palette ───────────────────────
BG          = "#f5f7fa"
WHITE       = "#ffffff"
SURFACE2    = "#f1f5f9"
BORDER      = "#e2e8f0"
BORDER2     = "#cbd5e1"

ACCENT      = "#6366f1"       
ACCENT_DARK = "#4f46e5"
ACCENT_BG   = "#eef2ff"
ACCENT_TXT  = "#4338ca"

ORANGE      = "#f97316"       
ORANGE_DARK = "#ea6c00"

GREEN       = "#16a34a"
GREEN_BG    = "#f0fdf4"
YELLOW      = "#d97706"
RED         = "#dc2626"
RED_BG      = "#fff1f2"
RED_LIGHT   = "#fca5a5"

TEXT        = "#1e293b"
TEXT_MUTED  = "#64748b"
TEXT_LIGHT  = "#94a3b8"

FONT_MONO   = ("Consolas", 9)
FONT_HEAD   = ("Segoe UI", 10, "bold")
FONT_BODY   = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 8)
FONT_TITLE  = ("Segoe UI", 11, "bold")

BLOCK_COLORS = [
    "#818cf8", "#34d399", "#fb923c", "#c084fc",
    "#60a5fa", "#4ade80", "#fbbf24", "#e879f9",
]
BLOCK_SIZES = [16, 32, 64, 128, 256, 512]
NUM_BLOCKS  = 8


class InternalFragTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # State
        self._block_size_var  = tk.IntVar(value=64)
        self._proc_name_var   = tk.StringVar(value="P1")
        self._proc_size_var   = tk.StringVar(value="40")
        self._processes: list = []   # [(name, size), ...]
        self._results:   list = []
        self._total_frag: int = 0
        self._proc_counter    = 1

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
        wrap = tk.Frame(p, bg=ACCENT_BG,
                        highlightbackground="#c7d2fe", highlightthickness=1)
        wrap.pack(fill="x", padx=16, pady=(14, 0))
        # Left stripe
        tk.Frame(wrap, bg=ACCENT, width=4).pack(side="left", fill="y")
        row = tk.Frame(wrap, bg=ACCENT_BG)
        row.pack(side="left", fill="x", padx=10, pady=8)
        tk.Label(row, text="Phân vùng cố định: ", bg=ACCENT_BG, fg=TEXT,
                 font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Label(row, text="Mỗi ô = ", bg=ACCENT_BG, fg=TEXT_MUTED,
                 font=("Segoe UI", 10)).pack(side="left")
        self._banner_size = tk.Label(row, text="64 KB", bg=ACCENT_BG,
                                     fg=ACCENT_TXT, font=("Segoe UI", 10, "bold"))
        self._banner_size.pack(side="left")
        tk.Label(row, text=". Tiến trình được cấp nguyên ô dù không dùng hết.",
                 bg=ACCENT_BG, fg=TEXT_MUTED, font=("Segoe UI", 10)).pack(side="left")

    # ── 2. Input controls ──
    def _build_input(self, p):
        card = self._card(p, pady=6)
        r = tk.Frame(card, bg=WHITE)
        r.pack(fill="x", padx=16, pady=12)

        # Labels row
        lbl_row = tk.Frame(r, bg=WHITE)
        lbl_row.pack(fill="x", pady=(0, 4))
        self._lbl(lbl_row, "Kích thước ô (KB)", width=14, side="left")
        self._lbl(lbl_row, "Tên tiến trình",    width=16, side="left", padx=(24, 0))
        self._lbl(lbl_row, "Cần (KB)",           width=12, side="left", padx=(24, 0))

        # Inputs row
        ctl = tk.Frame(r, bg=WHITE)
        ctl.pack(fill="x")

        # Block size combo
        combo = ttk.Combobox(ctl, textvariable=self._block_size_var,
                              values=BLOCK_SIZES, state="readonly",
                              font=FONT_BODY, width=11)
        combo.pack(side="left", ipady=4)
        combo.bind("<<ComboboxSelected>>", self._on_block_size_change)

        tk.Frame(ctl, bg=BG, width=24).pack(side="left")

        # Process name
        ent_name = self._entry_w(ctl, self._proc_name_var, width=14)
        ent_name.pack(side="left", ipady=5)

        tk.Frame(ctl, bg=BG, width=24).pack(side="left")

        # Process size
        ent_size = self._entry_w(ctl, self._proc_size_var, width=12)
        ent_size.pack(side="left", ipady=5)

        tk.Frame(ctl, bg=BG, width=24).pack(side="left")

        # Add button
        tk.Button(ctl, text="Nạp tiến trình",
                  bg=ACCENT, fg=WHITE,
                  activebackground=ACCENT_DARK, activeforeground=WHITE,
                  font=("Segoe UI", 10, "bold"), bd=0, relief="flat",
                  cursor="hand2", padx=20, pady=7,
                  command=self._on_add).pack(side="left")

        tk.Frame(ctl, bg=BG, width=10).pack(side="left")

        # Reset button
        tk.Button(ctl, text="Reset",
                  bg=ORANGE, fg=WHITE,
                  activebackground=ORANGE_DARK, activeforeground=WHITE,
                  font=("Segoe UI", 10, "bold"), bd=0, relief="flat",
                  cursor="hand2", padx=20, pady=7,
                  command=self._on_reset).pack(side="left")

    # ── 3. RAM memory map ──
    def _build_ram_map(self, p):
        card = self._card(p, pady=6)

        hdr = tk.Frame(card, bg=WHITE)
        hdr.pack(fill="x", padx=16, pady=(10, 6))
        tk.Label(hdr, text="RAM — Phân vùng cố định",
                 bg=WHITE, fg=TEXT, font=FONT_HEAD).pack(side="left")
        self._ram_info = tk.Label(hdr,
                                   text=f"{NUM_BLOCKS} ô × 64 KB = {NUM_BLOCKS*64} KB",
                                   bg=WHITE, fg=TEXT_MUTED, font=FONT_SMALL)
        self._ram_info.pack(side="right")

        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=16)

        self.canvas = tk.Canvas(card, bg=WHITE, height=120,
                                 highlightthickness=0, bd=0)
        self.canvas.pack(fill="x", padx=16, pady=10)
        self.canvas.bind("<Configure>",
                         lambda e: self._draw_memory_map())

    # ── 4. Big stat cards ──
    def _build_stat_cards(self, p):
        row = tk.Frame(p, bg=BG)
        row.pack(fill="x", padx=16, pady=(0, 6))
        row.columnconfigure(0, weight=1)
        row.columnconfigure(1, weight=1)
        row.columnconfigure(2, weight=1)

        bsz   = self._block_size_var.get()
        total = NUM_BLOCKS * bsz

        self._sc_used = self._big_card(row, col=0, label="ĐANG DÙNG",
                                        value="0 KB",     color=TEXT)
        self._sc_frag = self._big_card(row, col=1, label="LÃNG PHÍ (NỘI VI)",
                                        value="0 KB",     color=RED)
        self._sc_free = self._big_card(row, col=2, label="CÒN TRỐNG",
                                        value=f"{total} KB", color=TEXT)

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
            ("blocks",      "Số ô nhớ"),
            ("procs",       "Số tiến trình"),
            ("total_mem",   "Tổng bộ nhớ"),
            ("total_alloc", "Đã cấp phát"),
            ("total_frag",  "Phân mảnh nội"),
            ("pct",         "Tỉ lệ phân mảnh"),
            ("unalloc",     "Không cấp được"),
        ]
        self._stat_labels = {}
        cols = 4
        for i, (key, label) in enumerate(stats_defs):
            c = i % cols
            r_row = i // cols
            cell = tk.Frame(grid, bg=SURFACE2,
                             highlightbackground=BORDER, highlightthickness=1)
            cell.grid(row=r_row, column=c, sticky="ew",
                      padx=(0 if c == 0 else 4, 0), pady=(0 if r_row == 0 else 4, 0))
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

        cols = ("TT", "Tiến trình", "Yêu cầu", "Ô số", "Ô(KB)", "Frag(KB)", "Tình trạng")
        self.tree = ttk.Treeview(tbl_card, columns=cols,
                                  show="headings", height=8)
        for col, w in zip(cols, [32, 90, 72, 56, 70, 72, 90]):
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
        ]:
            self.log_box.tag_config(tag, foreground=color)

    # ── 7. Fragmentation chart ──
    def _build_chart(self, p):
        card = tk.Frame(p, bg=WHITE,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", padx=16, pady=(0, 18))
        tk.Label(card, text="📈  Biểu đồ phân mảnh nội (KB)",
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
        """One of the three summary stat boxes."""
        pad_l = 0 if col == 0 else 5
        pad_r = 5 if col < 2 else 0
        f = tk.Frame(parent, bg=WHITE,
                     highlightbackground=BORDER, highlightthickness=1)
        f.grid(row=0, column=col, sticky="ew",
               padx=(pad_l, pad_r), pady=2)
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

    def _entry_w(self, parent, var, width=12):
        return tk.Entry(parent, textvariable=var,
                        bg=WHITE, fg=TEXT, insertbackground=TEXT,
                        font=FONT_BODY, bd=1, relief="solid",
                        highlightbackground=BORDER, highlightcolor=ACCENT,
                        highlightthickness=1, width=width)

    def _log(self, msg, tag="info"):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n", tag)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _pcolor(self, idx: int) -> str:
        return BLOCK_COLORS[idx % len(BLOCK_COLORS)]

    # ──────────────────── Actions ────────────────────
    def _on_block_size_change(self, *_):
        bsz   = self._block_size_var.get()
        total = NUM_BLOCKS * bsz
        self._banner_size.configure(text=f"{bsz} KB")
        self._ram_info.configure(
            text=f"{NUM_BLOCKS} ô × {bsz} KB = {total} KB")
        self._sc_free.configure(text=f"{total} KB")
        if self._processes:
            self._run_simulation()
        else:
            self._draw_memory_map()

    def _on_add(self):
        name = self._proc_name_var.get().strip() or f"P{self._proc_counter}"
        try:
            size = int(self._proc_size_var.get().strip())
            if size <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi nhập liệu",
                                  "Kích thước tiến trình phải là số nguyên dương.")
            return

        bsz = self._block_size_var.get()
        if size > bsz:
            messagebox.showwarning(
                "Cảnh báo",
                f"Tiến trình {name} ({size} KB) lớn hơn kích thước ô ({bsz} KB).\n"
                "Tiến trình này sẽ không được cấp phát.")

        self._processes.append((name, size))
        self._proc_counter += 1
        self._proc_name_var.set(f"P{self._proc_counter}")
        self._run_simulation()

    def _on_reset(self):
        self._processes    = []
        self._results      = []
        self._total_frag   = 0
        self._proc_counter = 1
        self._proc_name_var.set("P1")
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")
        self._log("↺ Đã reset. Nhập tiến trình mới và nhấn Nạp.", "head")
        self._refresh()

    def _run_simulation(self):
        bsz    = self._block_size_var.get()
        blocks = [bsz] * NUM_BLOCKS
        procs  = [s for _, s in self._processes]

        results, total_frag = internal_fragment(blocks, procs)
        self._results    = results
        self._total_frag = total_frag

        # Rebuild log
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

        self._log("══════════════════════════", "sep")
        self._log(f"  Ô nhớ    : {NUM_BLOCKS} × {bsz} KB", "head")
        self._log(f"  Tiến trình: {procs}", "head")
        self._log("══════════════════════════", "sep")

        pnames = [n for n, _ in self._processes]
        for i, r in enumerate(results):
            nm = pnames[i] if i < len(pnames) else f"P{r['process']}"
            if r["block"] is not None:
                self._log(
                    f"  ✔ {nm} ({r['size']}KB) → Ô {r['block']}"
                    f" ({r['block_size']}KB) | frag = {r['internal']}KB",
                    "ok")
            else:
                self._log(
                    f"  ✘ {nm} ({r['size']}KB) → Không tìm được ô phù hợp",
                    "fail")

        self._log("──────────────────────────", "sep")
        self._log(f"  Tổng phân mảnh nội: {total_frag} KB", "head")
        self._log("══════════════════════════", "sep")

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
        pnames = [n for n, _ in self._processes]
        for i, r in enumerate(self._results):
            ok   = r["block"] is not None
            tag  = "ok" if ok else "fail"
            nm   = pnames[i] if i < len(pnames) else f"P{r['process']}"
            self.tree.insert("", "end", tags=(tag,), values=(
                i + 1,
                nm,
                f"{r['size']} KB",
                str(r["block"]) if ok else "—",
                f"{r['block_size']} KB" if ok else "—",
                f"{r['internal']} KB" if ok else "—",
                "✔ Cấp phát" if ok else "✘ Thất bại",
            ))

    def _update_stats(self):
        bsz    = self._block_size_var.get()
        total  = NUM_BLOCKS * bsz
        alloc  = [r for r in self._results if r["block"] is not None]
        fail   = [r for r in self._results if r["block"] is None]
        used   = sum(r["block_size"] for r in alloc)
        alloc_ = sum(r["size"] for r in alloc)
        free   = total - used
        pct    = (self._total_frag / used * 100) if used else 0

        # Big cards
        self._sc_used.configure(text=f"{used} KB",    fg=ACCENT   if used > 0 else TEXT)
        fc = RED if self._total_frag > 0 else GREEN
        self._sc_frag.configure(text=f"{self._total_frag} KB", fg=fc)
        self._sc_free.configure(text=f"{free} KB",
                                 fg=TEXT_MUTED if free > 0 else RED)

        # Detail stats
        if not self._results:
            for lbl in self._stat_labels.values():
                lbl.configure(text="—", fg=ACCENT)
            return

        self._stat_labels["blocks"].configure(
            text=str(NUM_BLOCKS), fg=TEXT)
        self._stat_labels["procs"].configure(
            text=str(len(self._processes)), fg=TEXT)
        self._stat_labels["total_mem"].configure(
            text=f"{total} KB", fg=TEXT)
        self._stat_labels["total_alloc"].configure(
            text=f"{alloc_} KB", fg=TEXT)
        fc2 = GREEN if self._total_frag == 0 else (YELLOW if pct < 30 else RED)
        self._stat_labels["total_frag"].configure(
            text=f"{self._total_frag} KB", fg=fc2)
        pc = GREEN if pct < 15 else (YELLOW if pct < 35 else RED)
        self._stat_labels["pct"].configure(
            text=f"{pct:.1f}%", fg=pc)
        uc = GREEN if not fail else RED
        self._stat_labels["unalloc"].configure(
            text=str(len(fail)), fg=uc)

    def _draw_memory_map(self):
        self.canvas.delete("all")
        bsz  = self._block_size_var.get()
        w    = self.canvas.winfo_width() or 700
        H    = 86
        mx   = 14
        gap  = 5
        n    = NUM_BLOCKS
        cell = (w - 2 * mx - gap * (n - 1)) // n

        # Block-index → (result, pname)
        alloc_map = {}
        pnames = [nm for nm, _ in self._processes]
        for i, r in enumerate(self._results):
            if r["block"] is not None:
                idx = r["block"] - 1
                if idx not in alloc_map:
                    nm = pnames[i] if i < len(pnames) else f"P{r['process']}"
                    alloc_map[idx] = (r, nm)

        x = mx
        y0, y1 = 10, 68

        for i in range(n):
            x1, x2 = x, x + cell

            if i in alloc_map:
                r, nm    = alloc_map[i]
                color    = self._pcolor(r["process"] - 1)
                aw       = max(int(r["size"] / bsz * cell), 2)
                fw       = cell - aw
                # Used portion
                self.canvas.create_rectangle(
                    x1, y0, x1 + aw, y1, fill=color, outline="")
                # Fragment portion
                if fw > 0:
                    self.canvas.create_rectangle(
                        x1 + aw, y0, x2, y1,
                        fill=RED_LIGHT, outline="")
                # Border
                self.canvas.create_rectangle(
                    x1, y0, x2, y1,
                    fill="", outline=BORDER2, width=1)
                # Label
                if cell > 30:
                    self.canvas.create_text(
                        (x1 + x2) // 2, (y0 + y1) // 2,
                        text=nm, fill=WHITE,
                        font=("Segoe UI", 8, "bold"))
            else:
                # Free
                self.canvas.create_rectangle(
                    x1, y0, x2, y1,
                    fill=SURFACE2, outline=BORDER2, width=1)
                if cell > 28:
                    self.canvas.create_text(
                        (x1 + x2) // 2, (y0 + y1) // 2,
                        text=f"{bsz}KB",
                        fill=TEXT_LIGHT, font=FONT_SMALL)

            # Block number below
            self.canvas.create_text(
                (x1 + x2) // 2, y1 + 9,
                text=str(i + 1),
                fill=TEXT_MUTED, font=FONT_SMALL)
            x += cell + gap

        # Legend
        lx, ly = mx, y1 + 23
        for color, label in [
            (BLOCK_COLORS[0], "Cấp phát"),
            (RED_LIGHT,       "Phân mảnh nội"),
            (SURFACE2,        "Trống"),
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

        pnames = [nm for nm, _ in self._processes]

        w   = self.chart_canvas.winfo_width() or 700
        H   = 155
        ml, mr, mb, mt = 52, 16, 30, 22
        cw  = w - ml - mr
        ch  = H - mb - mt
        n   = len(data)
        sp  = cw / n
        bw  = max(min(int(sp * 0.35), 48), 8)
        mx_ = max(max(r["size"] for r in data),
                   max(r["internal"] for r in data), 1)

        # Axes
        self.chart_canvas.create_line(ml, mt, ml, H - mb,
                                       fill=BORDER2, width=1)
        self.chart_canvas.create_line(ml, H - mb, w - mr, H - mb,
                                       fill=BORDER2, width=1)

        # Grid lines + Y labels
        for i in range(5):
            val = int(mx_ * i / 4)
            y   = H - mb - int(ch * i / 4)
            self.chart_canvas.create_line(
                ml, y, w - mr, y,
                fill=BORDER, dash=(2, 4), width=1)
            self.chart_canvas.create_text(
                ml - 4, y, text=str(val),
                fill=TEXT_MUTED, font=("Segoe UI", 7), anchor="e")

        # Bars
        for idx, r in enumerate(data):
            cx    = ml + int(sp * (idx + 0.5))
            color = self._pcolor(r["process"] - 1)
            nm    = (pnames[r["process"] - 1]
                     if r["process"] - 1 < len(pnames)
                     else f"P{r['process']}")

            # Process size bar
            ah = max(int(ch * r["size"] / mx_), 2)
            self.chart_canvas.create_rectangle(
                cx - bw, H - mb - ah, cx, H - mb,
                fill=color, outline="")
            self.chart_canvas.create_text(
                cx - bw // 2, H - mb - ah - 6,
                text=str(r["size"]), fill=color, font=("Segoe UI", 7))

            # Fragment bar
            fh = max(int(ch * r["internal"] / mx_), 1) if r["internal"] > 0 else 0
            if fh:
                self.chart_canvas.create_rectangle(
                    cx + 2, H - mb - fh, cx + bw + 2, H - mb,
                    fill=RED_LIGHT, outline="")
                self.chart_canvas.create_text(
                    cx + bw // 2 + 2, H - mb - fh - 6,
                    text=str(r["internal"]), fill=RED, font=("Segoe UI", 7))

            self.chart_canvas.create_text(
                cx, H - mb + 10, text=nm,
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
                                            fill=RED_LIGHT, outline="")
        self.chart_canvas.create_text(lx + 11, ly + 4,
                                       text="Phân mảnh nội (KB)",
                                       fill=TEXT_MUTED, font=("Segoe UI", 7),
                                       anchor="w")