import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from image_manipulation import add_noise_line, add_noise_dot, median_filter_1d

class ImageDenoiseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Denoise App")

        self.browse_button = tk.Button(root, text="Browse", command=self.browse_image)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)

        self.left_image_label = tk.Label(root)
        self.left_image_label.grid(row=1, column=0, padx=10, pady=10)

        self.right_image_label = tk.Label(root)
        self.right_image_label.grid(row=1, column=1, padx=10, pady=10)

        self.noise_dot_label = tk.Label(root, text="Noise Dot Multiplier:")
        self.noise_dot_label.grid(row=2, column=0, padx=10, pady=10)

        self.noise_dot_entry = tk.Entry(root, width=10)
        self.noise_dot_entry.insert(0, "10000")
        self.noise_dot_entry.grid(row=2, column=1, padx=10, pady=10)

        self.noise_dot_button = tk.Button(root, text="Noise Dot", command=self.add_noise_dot)
        self.noise_dot_button.grid(row=2, column=2, padx=10, pady=10)

        self.noise_line_label = tk.Label(root, text="Noise Line Multiplier:")
        self.noise_line_label.grid(row=3, column=0, padx=10, pady=10)

        self.noise_line_entry = tk.Entry(root, width=10)
        self.noise_line_entry.insert(0, "25")
        self.noise_line_entry.grid(row=3, column=1, padx=10, pady=10)

        self.noise_line_button = tk.Button(root, text="Noise Line", command=self.add_noise_line)
        self.noise_line_button.grid(row=3, column=2, padx=10, pady=10)

        self.filter_size_label = tk.Label(root, text="Filter Size:")
        self.filter_size_label.grid(row=4, column=0, padx=10, pady=10)

        self.filter_size_entry = tk.Entry(root, width=10)
        self.filter_size_entry.insert(0, "3")
        self.filter_size_entry.grid(row=4, column=1, padx=10, pady=10)

        self.axis_label = tk.Label(root, text="Axis (0: Vertical, 1: Horizontal):")
        self.axis_label.grid(row=5, column=0, padx=10, pady=10)

        self.axis_entry = tk.Entry(root, width=10)
        self.axis_entry.insert(0, "0")
        self.axis_entry.grid(row=5, column=1, padx=10, pady=10)

        self.denoise_button = tk.Button(root, text="Denoise", command=self.denoise_image)
        self.denoise_button.grid(row=4, column=2, padx=10, pady=10)

        self.denoise_button = tk.Button(root, text="Save", command=self.save_image)
        self.denoise_button.grid(row=6, column=1, padx=10, pady=10)

        self.original_image = None
        self.processed_image = None
        self.file_path = None

    def save_image(self):
        if self.processed_image:
            save_path = filedialog.asksaveasfilename(defaultextension=".bmp", filetypes=[("BMP files", "*.bmp")])
            if save_path:
                self.processed_image.save(save_path)
                print(f"Image saved to {save_path}")

    def browse_image(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.bmp")])
        if self.file_path:
            self.load_image(self.file_path)

    def load_image(self, file_path):
        self.original_image = Image.open(file_path)
        self.processed_image = self.original_image.copy()
        self.display_image(self.original_image, self.left_image_label)

    def display_image(self, image, label):
        image.thumbnail((300, 300))
        photo = ImageTk.PhotoImage(image)
        label.config(image=photo)
        label.image = photo

    def add_noise_dot(self):
        if self.original_image:
            try:
                dot_num = int(self.noise_dot_entry.get())
            except ValueError:
                print("Invalid input for noise dot number. Using default value 10000.")
                dot_num = 10000
            self.processed_image = add_noise_dot(self.file_path, dot_num)
            self.display_image(self.processed_image, self.right_image_label)

    def add_noise_line(self):
        if self.original_image:
            try:
                line_num = int(self.noise_line_entry.get())
            except ValueError:
                print("Invalid input for noise line number. Using default value 25.")
                line_num = 25
            self.processed_image = add_noise_line(self.file_path, line_num)
            self.display_image(self.processed_image, self.right_image_label)

    def denoise_image(self):
        if self.processed_image:
            try:
                filter_size = int(self.filter_size_entry.get())
                axis = int(self.axis_entry.get())
            except ValueError:
                print("Invalid input for filter size or axis. Using default values (3, 0).")
                filter_size = 3
                axis = 0

            if axis == 0 or axis == 1:
                self.processed_image = median_filter_1d(self.file_path, filter_size, axis)
            else:
                print("Invalid axis value. Use 0 (vertical) or 1 (horizontal).")
                return
            self.display_image(self.processed_image, self.right_image_label)