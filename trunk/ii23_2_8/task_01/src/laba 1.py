import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2
import numpy as np
import secrets
from copy import deepcopy

class NoiseGenerator:
    """Класс для создания шума в изображениях."""
    @staticmethod
    def apply_noise(image, probability):
        noisy_image = image.copy()
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                rand_val = secrets.randbelow(100) / 100
                if rand_val < probability / 2:
                    noisy_image[i, j] = [0, 0, 0]
                elif rand_val < probability:
                    noisy_image[i, j] = [255, 255, 255]
                else:
                    noisy_image[i, j] = image[i, j]
        return noisy_image

class MedianFilter:
    """Класс для применения медианного фильтра к изображению."""
    @staticmethod
    def apply_median_filter(image, apply_row_filter, apply_column_filter, kernel_size):
        def filter_row(channel):
            h, w = channel.shape
            pad = kernel_size // 2
            padded_channel = np.pad(channel, pad, mode='constant', constant_values=0)
            result = np.zeros_like(channel)
            for i in range(h):
                for j in range(w):
                    window = padded_channel[i + pad:i + pad + kernel_size, j]
                    result[i, j] = np.median(window)
            return result

        def filter_column(channel):
            h, w = channel.shape
            pad = kernel_size // 2
            padded_channel = np.pad(channel, pad, mode='constant', constant_values=0)
            result = np.zeros_like(channel)
            for i in range(h):
                for j in range(w):
                    window = padded_channel[i, j + pad:j + pad + kernel_size]
                    result[i, j] = np.median(window)
            return result

        filtered_image = image.copy()
        if apply_row_filter:
            r, g, b = cv2.split(filtered_image)
            r = filter_row(r)
            g = filter_row(g)
            b = filter_row(b)
            filtered_image = cv2.merge([r, g, b])

        if apply_column_filter:
            r, g, b = cv2.split(filtered_image)
            r = filter_column(r)
            g = filter_column(g)
            b = filter_column(b)
            filtered_image = cv2.merge([r, g, b])

        return filtered_image

class ImageProcessorApp:
    """Класс для создания приложения обработки изображений."""
    def __init__(self, master):
        self.master = master
        self.master.title("Image Processor")

        self.label_image = tk.Label(master)
        self.label_image.pack(pady=10)

        self.button_load = tk.Button(master, text="Load Image", command=self.load_image)
        self.button_load.pack(pady=5)

        self.button_reset = tk.Button(master, text="Reset Image", command=self.reset_image)
        self.button_reset.pack(pady=5)

        self.button_add_noise = tk.Button(master, text="Add Noise", command=self.add_noise)
        self.button_add_noise.pack(pady=5)

        self.label_filter_size = tk.Label(master, text="Median Filter Size:")
        self.label_filter_size.pack(pady=5)

        self.entry_filter_size = tk.Entry(master)
        self.entry_filter_size.pack(pady=5)

        self.var_row_filter = tk.IntVar()
        self.var_column_filter = tk.IntVar()

        self.checkbox_row_filter = tk.Checkbutton(master, text="Row Filter", variable=self.var_row_filter)
        self.checkbox_row_filter.pack()

        self.checkbox_column_filter = tk.Checkbutton(master, text="Column Filter", variable=self.var_column_filter)
        self.checkbox_column_filter.pack()

        self.button_apply_filter = tk.Button(master, text="Apply Median Filter", command=self.apply_filter)
        self.button_apply_filter.pack(pady=5)

        self.original_image = None
        self.processed_image = None

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        if file_path:
            self.original_image = cv2.resize(cv2.imread(file_path), (500, 500))
            self.processed_image = deepcopy(self.original_image)
            self.display_image(self.original_image)

    def reset_image(self):
        if self.original_image is not None:
            self.processed_image = deepcopy(self.original_image)
            self.display_image(self.processed_image)

    def add_noise(self):
        if self.original_image is not None:
            self.processed_image = NoiseGenerator.apply_noise(self.processed_image, 0.05)
            self.display_image(self.processed_image)

    def apply_filter(self):
        if self.original_image is not None:
            filter_size = int(self.entry_filter_size.get())
            self.processed_image = MedianFilter.apply_median_filter(self.processed_image,
                                                                    self.var_row_filter.get(),
                                                                    self.var_column_filter.get(),
                                                                    filter_size)
            self.display_image(self.processed_image)

    def display_image(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        photo = ImageTk.PhotoImage(image_pil)
        self.label_image.config(image=photo)
        self.label_image.image = photo

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()


# ii23_2_8 - название папки