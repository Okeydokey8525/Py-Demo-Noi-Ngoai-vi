import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys, os
 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.compaction import compaction

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


class CompactionTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._blocks:    list = []
        self._processes: list = []
        self._results:   list = []
        self._empty:     list = []
        self._compacted: list = []
        self._init_style()
        self._build_ui()
 
    # ──────── Style ────────
    def _init_style(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Light.TFrame", background=BG)
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
        self.configure(style="Light.TFrame")
 
    # ──────── Build UI ────────
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

        self._sf.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>", lambda e: cv.itemconfig(cw, width=e.width))
        cv.bind_all("<MouseWheel>", lambda e: cv.yview_scroll(-1 * (e.delta // 120), "units"))

        self._build_content(self._sf)

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
        wrap = tk.Frame(p, bg=ACCENT_BG, highlightbackground="#c7d2fe", highlightthickness=1)
        wrap.pack(fill="x", padx=16, pady=(14, 0))
        tk.Frame(wrap, bg=ACCENT, width=4).pack(side="left", fill="y")
        
        row = tk.Frame(wrap, bg=ACCENT_BG)
        row.pack(side="left", fill="x", padx=10, pady=8)
        tk.Label(row, text="Dồn bộ nhớ (Compaction): ", bg=ACCENT_BG, fg=TEXT, font=("Segoe UI", 10, "bold")).pack(side="left")
        tk.Label(row, text="Cấp phát First Fit ➔ Gom tất cả vùng trống rải rác thành một khối liên tục ở cuối.",
                 bg=ACCENT_BG, fg=TEXT_MUTED, font=("Segoe UI", 10)).pack(side="left")
 
    # ── 2. Input controls ──
    def _build_input(self, p):
        card = self._card(p, pady=6)
        r = tk.Frame(card, bg=WHITE)
        r.pack(fill="x", padx=16, pady=12)

        # Labels row
        lbl_row = tk.Frame(r, bg=WHITE)
        lbl_row.pack(fill="x", pady=(0, 4))
        tk.Label(lbl_row, text="Kích thước các khối nhớ (KB) [Ví dụ: 100, 500, 200, 300, 600]", bg=WHITE, fg=TEXT_MUTED, font=FONT_SMALL, anchor="w").pack(side="left", fill="x", expand=True)
        tk.Label(lbl_row, text="Kích thước các tiến trình (KB) [Ví dụ: 212, 417, 112, 426]", bg=WHITE, fg=TEXT_MUTED, font=FONT_SMALL, anchor="w").pack(side="left", fill="x", expand=True, padx=(16, 0))

        # Inputs row
        ctl = tk.Frame(r, bg=WHITE)
        ctl.pack(fill="x")

        self.ent_blocks = tk.Entry(ctl, bg=WHITE, fg=TEXT, insertbackground=TEXT, font=FONT_BODY, bd=1, relief="solid", highlightbackground=BORDER, highlightcolor=ACCENT, highlightthickness=1)
        self.ent_blocks.insert(0, "100, 500, 200, 300, 600")
        self.ent_blocks.pack(side="left", fill="x", expand=True, ipady=5)

        self.ent_procs = tk.Entry(ctl, bg=WHITE, fg=TEXT, insertbackground=TEXT, font=FONT_BODY, bd=1, relief="solid", highlightbackground=BORDER, highlightcolor=ACCENT, highlightthickness=1)
        self.ent_procs.insert(0, "212, 417, 112, 426")
        self.ent_procs.pack(side="left", fill="x", expand=True, ipady=5, padx=(16, 0))

        # Buttons row
        btn_row = tk.Frame(r, bg=WHITE)
        btn_row.pack(fill="x", pady=(12, 0))

        tk.Button(btn_row, text="▶  Chạy Compaction", bg=ACCENT, fg=WHITE, activebackground=ACCENT_DARK, activeforeground=WHITE, font=("Segoe UI", 10, "bold"), bd=0, relief="flat", cursor="hand2", padx=20, pady=7, command=self._on_run).pack(side="left")
        tk.Frame(btn_row, bg=WHITE, width=12).pack(side="left")
        tk.Button(btn_row, text="↺  Reset toàn bộ", bg=ORANGE, fg=WHITE, activebackground=ORANGE_DARK, activeforeground=WHITE, font=("Segoe UI", 10, "bold"), bd=0, relief="flat", cursor="hand2", padx=20, pady=7, command=self._on_reset).pack(side="left")
 
    # ── 3. RAM memory maps ──
    def _build_ram_map(self, p):
        card = self._card(p, pady=6)
        
        grid = tk.Frame(card, bg=WHITE)
        grid.pack(fill="x", padx=16, pady=12)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        # Trước Compaction
        left_f = tk.Frame(grid, bg=WHITE)
        left_f.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        hdr_b = tk.Frame(left_f, bg=WHITE)
        hdr_b.pack(fill="x", pady=(0, 4))
        tk.Label(hdr_b, text="🗺  TRƯỚC COMPACTION", bg=WHITE, fg=ACCENT, font=FONT_HEAD).pack(side="left")
        tk.Frame(left_f, bg=BORDER, height=1).pack(fill="x")
        
        self.canvas_before = tk.Canvas(left_f, bg=SURFACE2, height=120, highlightthickness=0, bd=0)
        self.canvas_before.pack(fill="x", pady=8)
        self.canvas_before.bind("<Configure>", lambda e: self._draw_memory_map_before())

        # Sau Compaction
        right_f = tk.Frame(grid, bg=WHITE)
        right_f.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        hdr_a = tk.Frame(right_f, bg=WHITE)
        hdr_a.pack(fill="x", pady=(0, 4))
        tk.Label(hdr_a, text="✨  SAU COMPACTION", bg=WHITE, fg=ACCENT_TXT, font=FONT_HEAD).pack(side="left")
        tk.Frame(right_f, bg=BORDER, height=1).pack(fill="x")
        
        self.canvas_after = tk.Canvas(right_f, bg=SURFACE2, height=120, highlightthickness=0, bd=0)
        self.canvas_after.pack(fill="x", pady=8)
        self.canvas_after.bind("<Configure>", lambda e: self._draw_memory_map_after())
 
    # ── 4. Big stat cards ──
    def _build_stat_cards(self, p):
        row = tk.Frame(p, bg=BG)
        row.pack(fill="x", padx=16, pady=(0, 6))
        row.columnconfigure(0, weight=1)
        row.columnconfigure(1, weight=1)
        row.columnconfigure(2, weight=1)

        self._sc_total = self._big_card(row, col=0, label="TỔNG BỘ NHỚ", value="0 KB", color=TEXT)
        self._sc_alloc = self._big_card(row, col=1, label="ĐÃ CẤP PHÁT", value="0 KB", color=ACCENT)
        self._sc_free  = self._big_card(row, col=2, label="TRỐNG (SAU DỒN)", value="0 KB", color=GREEN)
 
    # ── 5. Detailed stats ──
    def _build_detail_stats(self, p):
        card = self._card(p, pady=6)
        hdr = tk.Frame(card, bg=WHITE)
        hdr.pack(fill="x", padx=16, pady=(10, 6))
        tk.Label(hdr, text="📊  Chi tiết thống kê", bg=WHITE, fg=TEXT, font=FONT_HEAD).pack(side="left")
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=16)

        grid = tk.Frame(card, bg=WHITE)
        grid.pack(fill="x", padx=16, pady=10)

        stats_defs = [
            ("blocks",        "Số khối nhớ"),
            ("procs",         "Số tiến trình"),
            ("total_mem",     "Tổng bộ nhớ"),
            ("total_alloc",   "Đã cấp phát"),
            ("before_remain", "Trống (trước dồn)"),
            ("after_remain",  "Trống (sau dồn)"),
            ("unalloc",       "Không cấp được"),
        ]
        self._stat_labels = {}
        cols = 4
        for i, (key, label) in enumerate(stats_defs):
            c = i % cols
            r_row = i // cols
            cell = tk.Frame(grid, bg=SURFACE2, highlightbackground=BORDER, highlightthickness=1)
            cell.grid(row=r_row, column=c, sticky="ew", padx=(0 if c == 0 else 4, 0), pady=(0 if r_row == 0 else 4, 0))
            grid.columnconfigure(c, weight=1)
            inner = tk.Frame(cell, bg=SURFACE2, pady=6, padx=10)
            inner.pack(fill="both")
            tk.Label(inner, text=label, bg=SURFACE2, fg=TEXT_MUTED, font=FONT_SMALL, anchor="w").pack(fill="x")
            val = tk.Label(inner, text="—", bg=SURFACE2, fg=ACCENT, font=("Segoe UI", 13, "bold"), anchor="w")
            val.pack(fill="x")
            self._stat_labels[key] = val
 
    # ── 6. Table + Log ──
    def _build_table_log(self, p):
        wrap = tk.Frame(p, bg=BG)
        wrap.pack(fill="both", expand=True, padx=16, pady=(0, 6))
        wrap.columnconfigure(0, weight=3)
        wrap.columnconfigure(1, weight=2)
        wrap.rowconfigure(0, weight=1)

        # Table Card
        tbl_card = tk.Frame(wrap, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        tbl_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        tk.Label(tbl_card, text="📋  Kết quả cấp phát", bg=WHITE, fg=TEXT, font=FONT_HEAD, padx=14, pady=9, anchor="w").pack(fill="x")
        tk.Frame(tbl_card, bg=BORDER, height=1).pack(fill="x")
 
        cols = ("TT", "T.Trình", "Y/cầu(KB)", "Khối số", "Còn lại(KB)", "Tình trạng")
        self.tree = ttk.Treeview(tbl_card, columns=cols, show="headings", height=8)
        for col, w in zip(cols, [32, 72, 76, 64, 80, 80]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center", stretch=True)
        self.tree.tag_configure("ok",   background=GREEN_BG, foreground=GREEN)
        self.tree.tag_configure("fail", background=RED_BG,   foreground=RED)
        sb = ttk.Scrollbar(tbl_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=8)
        sb.pack(side="right", fill="y", pady=8, padx=(0, 4))
 
        # Log Card
        log_card = tk.Frame(wrap, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        log_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        tk.Label(log_card, text="📜  Quá trình chạy", bg=WHITE, fg=TEXT, font=FONT_HEAD, padx=14, pady=9, anchor="w").pack(fill="x")
        tk.Frame(log_card, bg=BORDER, height=1).pack(fill="x")
        self.log_box = scrolledtext.ScrolledText(
            log_card, bg=SURFACE2, fg=TEXT, font=FONT_MONO,
            insertbackground=TEXT, borderwidth=0, wrap=tk.WORD, state="disabled", height=10
        )
        self.log_box.pack(fill="both", expand=True, padx=8, pady=8)
        for tag, color in [
            ("ok",      GREEN),
            ("fail",    RED),
            ("info",    TEXT_MUTED),
            ("head",    ACCENT_TXT),
            ("compact", ACCENT),
            ("sep",     BORDER2),
            ("arrow",   YELLOW),
        ]:
            self.log_box.tag_config(tag, foreground=color)
 
    # ── 7. Chart ──
    def _build_chart(self, p):
        card = tk.Frame(p, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", padx=16, pady=(0, 18))
        tk.Label(card, text="📈  Biểu đồ phân bổ bộ nhớ (KB)", bg=WHITE, fg=TEXT, font=FONT_HEAD, padx=14, pady=9, anchor="w").pack(fill="x")
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x")
        self.chart_canvas = tk.Canvas(card, bg=WHITE, height=160, highlightthickness=0, bd=0)
        self.chart_canvas.pack(fill="x", padx=14, pady=10)
        self.chart_canvas.bind("<Configure>", lambda e: self._draw_chart())
 
    # ──────────────────── Helpers ────────────────────
    def _card(self, parent, pady=8):
        f = tk.Frame(parent, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        f.pack(fill="x", padx=16, pady=(0, pady))
        return f
 
    def _big_card(self, parent, col, label, value, color):
        pad_l = 0 if col == 0 else 5
        pad_r = 5 if col < 2 else 0
        f = tk.Frame(parent, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
        f.grid(row=0, column=col, sticky="ew", padx=(pad_l, pad_r), pady=2)
        inner = tk.Frame(f, bg=WHITE, pady=16, padx=20)
        inner.pack(fill="both", expand=True)
        val_lbl = tk.Label(inner, text=value, bg=WHITE, fg=color, font=("Segoe UI", 22, "bold"))
        val_lbl.pack()
        tk.Label(inner, text=label, bg=WHITE, fg=TEXT_MUTED, font=("Segoe UI", 8, "bold")).pack()
        return val_lbl
 
    def _log(self, msg, tag="info"):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n", tag)
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
 
    def _pcolor(self, idx: int) -> str:
        return BLOCK_COLORS[idx % len(BLOCK_COLORS)]
 
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
            messagebox.showerror("Lỗi nhập liệu", "Vui lòng nhập danh sách số nguyên dương, cách nhau dấu phẩy.")
            return
 
        results, empty_space, compacted = compaction(blocks, procs)
 
        self._blocks    = blocks
        self._processes = procs
        self._results   = results
        self._empty     = empty_space
        self._compacted = compacted
 
        # ── Log ──
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")
 
        self._log("══════════════════════════", "sep")
        self._log("  Thuật toán : First Fit + Compaction", "compact")
        self._log(f"  Khối nhớ  : {blocks}", "head")
        self._log(f"  Tiến trình: {procs}", "head")
        self._log("══════════════════════════", "sep")
        self._log("  [BƯỚC 1] Cấp phát First Fit:", "head")
 
        for r in results:
            if r["block"] is not None:
                self._log(f"  ✔ P{r['process']} ({r['size']}KB) ➔ Khối {r['block']} | còn = {r['remain']}KB", "ok")
            else:
                self._log(f"  ✘ P{r['process']} ({r['size']}KB) ➔ Không tìm được khối", "fail")
 
        self._log("──────────────────────────", "sep")
        self._log("  [BƯỚC 2] Compaction:", "compact")
        self._log(f"  Trạng thái khối trước dồn: {empty_space}", "info")
        self._log(f"  ⟹  Dồn tất cả vùng trống về cuối", "arrow")
        self._log(f"  Trạng thái sau dồn: {compacted}", "compact")
        total_free = sum(b for b in compacted if b > 0)
        self._log(f"  Tổng vùng trống liên tục: {total_free} KB", "compact")
        self._log("══════════════════════════", "sep")
 
        self._refresh()
 
    def _on_reset(self):
        self._blocks    = []
        self._processes = []
        self._results   = []
        self._empty     = []
        self._compacted = []
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")
        self._log("↺ Đã reset. Nhập dữ liệu mới và nhấn ▶ Chạy.", "head")
        self._refresh()
 
    # ──────────────────── Refresh ────────────────────
    def _refresh(self):
        self._update_table()
        self._update_stats()
        self._draw_memory_map_before()
        self._draw_memory_map_after()
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
            self._sc_total.configure(text="0 KB")
            self._sc_alloc.configure(text="0 KB")
            self._sc_free.configure(text="0 KB")
            return
 
        alloc        = [r for r in self._results if r["block"] is not None]
        ua           = [r for r in self._results if r["block"] is None]
        total_mem    = sum(self._blocks)
        total_alloc  = sum(r["size"] for r in alloc)
        before_rem   = sum(self._empty)
        after_rem    = sum(b for b in self._compacted if b > 0)
 
        # Cập nhật Thẻ thông số lớn
        self._sc_total.configure(text=f"{total_mem} KB")
        self._sc_alloc.configure(text=f"{total_alloc} KB")
        self._sc_free.configure(text=f"{after_rem} KB")

        # Cập nhật bảng chi tiết thống kê
        self._stat_labels["blocks"].configure(text=str(len(self._blocks)), fg=TEXT)
        self._stat_labels["procs"].configure(text=str(len(self._processes)), fg=TEXT)
        self._stat_labels["total_mem"].configure(text=f"{total_mem} KB", fg=TEXT)
        self._stat_labels["total_alloc"].configure(text=f"{total_alloc} KB", fg=TEXT)
        
        rc = GREEN if before_rem < total_mem * 0.3 else (YELLOW if before_rem < total_mem * 0.6 else RED)
        self._stat_labels["before_remain"].configure(text=f"{before_rem} KB", fg=rc)
        self._stat_labels["after_remain"].configure(text=f"{after_rem} KB", fg=GREEN)
        
        uc = GREEN if not ua else RED
        self._stat_labels["unalloc"].configure(text=str(len(ua)), fg=uc)
 
    # ── Memory map: trước compaction ──
    def _draw_memory_map_before(self):
        c = self.canvas_before
        c.delete("all")
        if not self._blocks:
            c.create_text(200, 50, text="Chưa có dữ liệu.", fill=TEXT_LIGHT, font=FONT_BODY)
            return
 
        total  = sum(self._blocks)
        w      = c.winfo_width() or 400
        mx     = 10
        my0, my1 = 12, 80
        usable = w - 2 * mx
 
        block_state = {}
        for r in self._results:
            if r["block"] is not None:
                block_state.setdefault(r["block"] - 1, []).append(r)
 
        x = mx
        for i, orig in enumerate(self._blocks):
            bw     = max(int(orig / total * usable), 6)
            remain = self._empty[i] if self._empty else orig
            used   = orig - remain
 
            if used > 0:
                processes_in = block_state.get(i, [])
                slot_x = x
                for pr in processes_in:
                    pw = max(int(pr["size"] / orig * bw), 2)
                    color = self._pcolor(pr["process"] - 1)
                    c.create_rectangle(slot_x, my0, slot_x + pw, my1, fill=color, outline="", width=0)
                    if pw > 20:
                        c.create_text(slot_x + pw // 2, (my0 + my1) // 2, text=f"P{pr['process']}", fill=WHITE, font=("Segoe UI", 8, "bold"))
                    slot_x += pw
                if remain > 0:
                    rw = bw - (slot_x - x)
                    if rw > 0:
                        c.create_rectangle(slot_x, my0, slot_x + rw, my1, fill=SURFACE2, outline="", width=0)
                        if rw > 16:
                            c.create_text(slot_x + rw // 2, (my0 + my1) // 2, text=f"{remain}", fill=TEXT_MUTED, font=("Segoe UI", 7))
                c.create_rectangle(x, my0, x + bw, my1, fill="", outline=BORDER, width=1)
            else:
                c.create_rectangle(x, my0, x + bw, my1, fill=SURFACE2, outline=BORDER2, width=1)
                if bw > 20:
                    c.create_text(x + bw // 2, (my0 + my1) // 2, text=f"FREE\n{orig}KB", fill=TEXT_LIGHT, font=("Segoe UI", 7))
 
            c.create_text(x + bw // 2, my1 + 9, text=str(orig), fill=TEXT_MUTED, font=("Segoe UI", 7))
            x += bw
 
        # Legend
        lx, ly = mx, my1 + 26
        for color, label in [(BLOCK_COLORS[0], "Đã dùng"), (SURFACE2, "Còn trống")]:
            c.create_rectangle(lx, ly - 8, lx + 10, ly, fill=color, outline=BORDER2 if color == SURFACE2 else "")
            c.create_text(lx + 13, ly - 4, text=label, fill=TEXT_MUTED, font=("Segoe UI", 7), anchor="w")
            lx += 70
 
    # ── Memory map: sau compaction ──
    def _draw_memory_map_after(self):
        c = self.canvas_after
        c.delete("all")
        if not self._compacted:
            c.create_text(200, 50, text="Chưa có dữ liệu.", fill=TEXT_LIGHT, font=FONT_BODY)
            return
 
        total  = sum(self._blocks)
        w      = c.winfo_width() or 400
        mx     = 10
        my0, my1 = 12, 80
        usable = w - 2 * mx
 
        alloc_procs = [r for r in self._results if r["block"] is not None]
        x = mx
        total_used = sum(r["size"] for r in alloc_procs)
        total_free = total - total_used
 
        for r in alloc_procs:
            pw = max(int(r["size"] / total * usable), 6)
            color = self._pcolor(r["process"] - 1)
            c.create_rectangle(x, my0, x + pw, my1, fill=color, outline=WHITE, width=1)
            if pw > 20:
                c.create_text(x + pw // 2, (my0 + my1) // 2, text=f"P{r['process']}\n{r['size']}KB", fill=WHITE, font=("Segoe UI", 7, "bold"))
            x += pw
 
        # Vùng trống lớn gom về cuối
        free_w = (mx + usable) - x
        if free_w > 0:
            c.create_rectangle(x, my0, x + free_w, my1, fill=GREEN_BG, outline=BORDER2, width=1)
            c.create_rectangle(x, my0, x + free_w, my1, fill="", outline=GREEN, width=1)
            if free_w > 30:
                c.create_text(x + free_w // 2, (my0 + my1) // 2, text=f"FREE\n{total_free}KB", fill=GREEN, font=("Segoe UI", 8, "bold"))
 
        # Legend
        lx, ly = mx, my1 + 24
        for color, label in [(BLOCK_COLORS[0], "Tiến trình"), (GREEN, "Vùng trống dồn")]:
            c.create_rectangle(lx, ly - 8, lx + 10, ly, fill=color, outline="")
            c.create_text(lx + 13, ly - 4, text=label, fill=TEXT_MUTED, font=("Segoe UI", 7), anchor="w")
            lx += 80
 
    # ── Chart ──
    def _draw_chart(self):
        c = self.chart_canvas
        c.delete("all")
        data = [r for r in self._results if r["block"] is not None]
        if not data:
            c.create_text(300, 80, text="Không có dữ liệu để vẽ biểu đồ.", fill=TEXT_LIGHT, font=FONT_BODY)
            return
 
        w  = c.winfo_width() or 640
        H  = 160
        ml, mr, mb, mt = 52, 16, 28, 25
        cw = w - ml - mr
        ch = H - mb - mt
        
        
        n  = len(data) + 1
        sp = cw / n
        bw = max(min(int(sp * 0.3), 32), 8)  
 
        
        after_rem = sum(b for b in self._compacted if b > 0) if self._compacted else 0
        mx_val = max(
            max(r["size"] for r in data),
            max((r["remain"] for r in data if r["remain"] is not None), default=0),
            after_rem,
            1,
        )
 
      
        c.create_line(ml, mt, ml, H - mb, fill=BORDER2, width=1)
        c.create_line(ml, H - mb, w - mr, H - mb, fill=BORDER2, width=1)
 
       
        for i in range(5):
            val = int(mx_val * i / 4)
            y   = H - mb - int(ch * i / 4)
            c.create_line(ml, y, w - mr, y, fill=BORDER, dash=(2, 4), width=1)
            c.create_text(ml - 6, y, text=str(val), fill=TEXT_MUTED, font=("Segoe UI", 7), anchor="e")
 
       
        for idx, r in enumerate(data):
            cx    = ml + int(sp * (idx + 0.5))
            color = self._pcolor(r["process"] - 1)
 
          
            ah = max(int(ch * r["size"] / mx_val), 2)
            c.create_rectangle(cx - bw - 1, H - mb - ah, cx - 1, H - mb, fill=color, outline="", width=0)
            c.create_text(cx - (bw // 2) - 1, H - mb - ah - 6, text=str(r["size"]), fill=TEXT_MUTED, font=("Segoe UI", 7))
 
            
            rem_val = r["remain"] if r["remain"] is not None else 0
            rh = max(int(ch * rem_val / mx_val), 1) if rem_val > 0 else 0
            if rem_val > 0:
                c.create_rectangle(cx + 1, H - mb - rh, cx + bw + 1, H - mb, fill=YELLOW, outline="", width=0)
                c.create_text(cx + (bw // 2) + 1, H - mb - rh - 6, text=str(rem_val), fill=YELLOW, font=("Segoe UI", 7))
 
            
            c.create_text(cx, H - mb + 10, text=f"P{r['process']}", fill=TEXT_MUTED, font=("Segoe UI", 7))
 
       
        if after_rem > 0:
            cx_free = ml + int(sp * (len(data) + 0.5))
            fh = max(int(ch * after_rem / mx_val), 2)
            
            c.create_rectangle(cx_free - bw, H - mb - fh, cx_free + bw, H - mb, fill=GREEN_BG, outline=GREEN, width=1)
            c.create_text(cx_free, H - mb - fh - 6, text=str(after_rem), fill=GREEN, font=("Segoe UI", 7, "bold"))
            c.create_text(cx_free, H - mb + 10, text="Vùng trống", fill=GREEN, font=("Segoe UI", 7, "bold"))
 
    
        lx, ly = ml, mt - 16
     
        c.create_rectangle(lx, ly, lx + 10, ly + 10, fill=BLOCK_COLORS[0], outline="")
        c.create_text(lx + 14, ly + 5, text="Y/cầu P_i (KB)", fill=TEXT_MUTED, font=("Segoe UI", 7), anchor="w")
        
        
        lx += 120
        c.create_rectangle(lx, ly, lx + 10, ly + 10, fill=YELLOW, outline="")
        c.create_text(lx + 14, ly + 5, text="Trống (Trước dồn)", fill=TEXT_MUTED, font=("Segoe UI", 7), anchor="w")
        
     
        lx += 140
        c.create_rectangle(lx, ly, lx + 10, ly + 10, fill=GREEN_BG, outline=GREEN, width=1)
        c.create_text(lx + 14, ly + 5, text="Vùng trống liên tục (Sau dồn)", fill=TEXT_MUTED, font=("Segoe UI", 7), anchor="w")