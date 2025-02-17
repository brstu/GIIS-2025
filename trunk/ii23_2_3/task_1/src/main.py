from app import ImageDenoiseApp
from image_manipulation import add_noise_dot, add_noise_line, median_filter_1d
import tkinter as tk
from tkinter import filedialog

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageDenoiseApp(root)
    root.mainloop()