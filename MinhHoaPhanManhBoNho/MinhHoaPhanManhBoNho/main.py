import tkinter as tk
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.mainmenu import MainMenu
def main(): 
    root = tk.Tk()

    root.title("Mô Phỏng Phân Mảnh Bộ Nhớ")
    root.configure(bg="#0d1117")
    root.geometry("1200x820")
    root.minsize(900, 640)
 
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    win_w, win_h = 1200, 820
    x = (screen_w - win_w) // 2
    y = (screen_h - win_h) // 2
    root.geometry(f"{win_w}x{win_h}+{x}+{y}")

    app = MainMenu(root)
    app.pack(fill="both", expand=True)
    root.mainloop()

if __name__ == "__main__":
    main()
