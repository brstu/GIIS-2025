import cv2
import numpy as np
import random
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import secrets


def add_impulse_noise(image, noise_level=0.02, noise_type='points'):
    noisy_image = image.copy()
    h, w = noisy_image.shape[:2]
    num_noise = int(noise_level * h * w)

    if noise_type == 'points':
        for _ in range(num_noise):
            x, y = secrets.randbelow(w), secrets.randbelow(h)
            noisy_image[y, x] = 255 if secrets.randbelow(2) else 0
    elif noise_type == 'lines':
        for _ in range(int(num_noise / 50)):
            x1, y1, x2, y2 = [secrets.randbelow(dim) for dim in [w, h, w, h]]
            cv2.line(noisy_image, (x1, y1), (x2, y2), 255 if secrets.randbelow(2) else 0, 1)

    return noisy_image


def threshold_filter(image, threshold=128):
    filtered = cv2.GaussianBlur(image, (3, 3), 0)
    _, filtered = cv2.threshold(filtered, threshold, 255, cv2.THRESH_BINARY)
    return filtered


def median_filter(image, kernel_size=3):
    return cv2.medianBlur(image, kernel_size)


def open_image():
    global img, img_display, img_original
    file_path = filedialog.askopenfilename()
    if not file_path:
        return
    img = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    img_original = img.copy()
    display_image(img)


def apply_noise():
    global img
    if img is None:
        return
    noise_level = noise_level_slider.get()
    noise_type = noise_type_var.get()
    img = add_impulse_noise(img_original, noise_level, noise_type)
    display_image(img)


def apply_filter():
    global img
    if img is None:
        return
    filter_type = filter_type_var.get()
    if filter_type == "Threshold":
        threshold = threshold_slider.get()
        img = threshold_filter(img, threshold)
    elif filter_type == "Median":
        kernel_size = median_slider.get()
        img = median_filter(img, kernel_size)
    display_image(img)


def display_image(image):
    global img_display, panel
    max_size = 400
    h, w = image.shape[:2]
    scale = min(max_size / w, max_size / h)
    new_w, new_h = int(w * scale), int(h * scale)
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    image = Image.fromarray(resized)
    img_display = ImageTk.PhotoImage(image)
    panel.config(image=img_display)


def create_ui():
    global panel, img, img_display, img_original
    global noise_level_slider, noise_type_var, filter_type_var, threshold_slider, median_slider

    img = None
    img_original = None
    root = tk.Tk()
    root.title("Image Noise Filtering")
    root.geometry("700x700")
    root.configure(bg="lightblue")

    panel = tk.Label(root)
    panel.pack()

    controls_frame = tk.Frame(root)
    controls_frame.pack()

    btn_frame = tk.Frame(root, bg="lightblue")
    btn_frame.pack()


    btn_open = tk.Button(btn_frame, text="Open Image", command=open_image, bg="orange", width=20, height=2)
    btn_open.pack(pady=5, anchor=tk.CENTER)

    noise_type_var = tk.StringVar(value="points")
    noise_type_menu = ttk.Combobox(controls_frame, textvariable=noise_type_var, values=["points", "lines"])
    noise_type_menu.grid(row=1, column=0, padx=5, pady=5)

    noise_level_slider = tk.Scale(controls_frame, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL,
                                  label="Noise Level")
    noise_level_slider.grid(row=1, column=1, padx=5, pady=5)

    btn_noise = tk.Button(controls_frame, text="Add Noise", command=apply_noise, bg="orange")
    btn_noise.grid(row=1, column=2, padx=5, pady=5)

    filter_type_var = tk.StringVar(value="Threshold")
    filter_type_menu = ttk.Combobox(controls_frame, textvariable=filter_type_var, values=["Threshold", "Median"])
    filter_type_menu.grid(row=2, column=0, padx=5, pady=5)

    threshold_slider = tk.Scale(controls_frame, from_=0, to=255, orient=tk.HORIZONTAL, label="Threshold")
    threshold_slider.grid(row=2, column=1, padx=5, pady=5)

    median_slider = tk.Scale(controls_frame, from_=1, to=9, resolution=2, orient=tk.HORIZONTAL, label="Median Kernel")
    median_slider.grid(row=2, column=2, padx=5, pady=5)

    btn_filter = tk.Button(controls_frame, text="Remove Noise", command=apply_filter, bg="orange")
    btn_filter.grid(row=2, column=3, padx=5, pady=5)

    root.mainloop()


def main():
    create_ui()


if __name__ == '__main__':
    main()
