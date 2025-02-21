import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from ttkbootstrap import Style
from ttkbootstrap.widgets import Scale, Button, Label, Entry
from PIL import Image, ImageTk


class ImageDenoisingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Denoising App")
        self.root.geometry("900x700")
        self.style = Style("darkly")

        self.image = None
        self.noisy_image = None
        self.filtered_image = None

        self.frame_images = tk.Frame(root)
        self.frame_images.pack(pady=10, padx=20, expand=True)

        self.canvas_original = tk.Canvas(self.frame_images, width=250, height=250)
        self.canvas_original.grid(row=0, column=0, padx=10)

        self.canvas_filtered = tk.Canvas(self.frame_images, width=250, height=250)
        self.canvas_filtered.grid(row=0, column=1, padx=10)

        self.btn_load = Button(root, text="Load Image", command=self.load_image, style="primary.TButton")
        self.btn_load.pack(pady=10, padx=20, fill="x")

        self.noise_label = Label(root, text="Noise Level", font=("Arial", 10, "bold"))
        self.noise_label.pack(pady=5)

        self.noise_level = Scale(root, from_=0, to=100, orient="horizontal", style="primary.TScale")
        self.noise_level.pack(pady=5, padx=20, fill="x")

        self.btn_add_noise = Button(root, text="Add Noise", command=self.add_noise, style="danger.TButton")
        self.btn_add_noise.pack(pady=10, padx=20, fill="x")

        self.filter_size_label = Label(root, text="Filter Size (odd number)", font=("Arial", 10, "bold"))
        self.filter_size_label.pack(pady=5)

        self.filter_size = tk.IntVar(value=3)
        self.filter_size_entry = Entry(root, textvariable=self.filter_size, font=("Arial", 12), width=5)
        self.filter_size_entry.pack(pady=5)

        self.btn_filter_1xn = Button(root, text="Apply 1xN Filter", command=lambda: self.apply_filter(1, self.filter_size.get()), style="success.TButton")
        self.btn_filter_1xn.pack(pady=8, padx=20, fill="x")

        self.btn_filter_nx1 = Button(root, text="Apply Nx1 Filter", command=lambda: self.apply_filter(self.filter_size.get(), 1), style="info.TButton")
        self.btn_filter_nx1.pack(pady=8, padx=20, fill="x")

        self.btn_filter_combined = Button(root, text="Apply 1xN and Nx1 Filter", command=self.apply_combined_filter, style="warning.TButton")
        self.btn_filter_combined.pack(pady=10, padx=20, fill="x")

    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            self.show_image(self.image, self.canvas_original)

    def add_noise(self):
        if self.image is None:
            return
        noise_level = self.noise_level.get()
        noisy_image = self.image.copy()
        num_pixels = int((noise_level / 100) * noisy_image.size)
        for _ in range(num_pixels):
            x, y = np.random.randint(0, noisy_image.shape[1]), np.random.randint(0, noisy_image.shape[0])
            noisy_image[y, x] = np.random.choice([0, 255])
        self.noisy_image = noisy_image
        self.show_image(self.noisy_image, self.canvas_filtered)

    def apply_filter(self, kx, ky):
        if self.noisy_image is None:
            return

        if kx % 2 == 0 or ky % 2 == 0:
            messagebox.showerror("Invalid Filter Size", "Filter size must be odd.")
            return
        if kx == 1 and ky == 1:
            messagebox.showwarning("No Effect", "Filter size of 1x1 will have no effect on the image.")
            return

        # фильтр по строкам
        filtered_by_rows = cv2.medianBlur(self.noisy_image, ksize=ky)

        # фильтр по столбцам
        filtered_by_columns = cv2.medianBlur(self.noisy_image, ksize=kx)

        # комбинированный фильтрп
        self.filtered_image = filtered_by_columns
        self.filtered_image = cv2.medianBlur(self.filtered_image, ksize=ky)

        self.show_image(self.filtered_image, self.canvas_filtered)

    def apply_combined_filter(self):
        size = self.filter_size.get()
        self.apply_filter(size, size)

    def show_image(self, img, canvas):
        img = Image.fromarray(img)
        img = img.resize((250, 250))
        img_tk = ImageTk.PhotoImage(img)
        canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
        canvas.image = img_tk


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageDenoisingApp(root)
    root.mainloop()
