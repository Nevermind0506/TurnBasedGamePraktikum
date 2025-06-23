import tkinter as tk
from tk_game_ui import RPGGameUI

def main():
    """Fungsi utama untuk menginisialisasi dan menjalankan permainan."""
    try:
        root = tk.Tk()
        game = RPGGameUI(root)
        root.mainloop()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()