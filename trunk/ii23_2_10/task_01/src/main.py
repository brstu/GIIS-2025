import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, colorchooser
from PIL import Image, ImageTk
import random

def open_image():
    global img, img_gray
    file_path = filedialog.askopenfilename()
    if not file_path:
        return
    img = cv2.imread(file_path)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    display_image(img_gray, "Original Image")

def display_image(image, title):
    img_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_tk = ImageTk.PhotoImage(img_pil)
    label.config(image=img_tk)
    label.image = img_tk
    label_text.set(title)

def add_salt_and_pepper_noise():
    global img_gray
    noise_level = salt_pepper_slider.get()
    noisy_img = img_gray.copy()
    rows, cols = noisy_img.shape
    num_salt = int(noise_level * rows * cols / 10000)
    num_pepper = int(noise_level * rows * cols / 10000)

    for _ in range(num_salt):
        x, y = random.randint(0, cols-1), random.randint(0, rows-1)
        noisy_img[y, x] = 255

    for _ in range(num_pepper):
        x, y = random.randint(0, cols-1), random.randint(0, rows-1)
        noisy_img[y, x] = 0

    img_gray = noisy_img
    display_image(noisy_img, "Salt and Pepper Noise")

def add_gaussian_noise():
    global img_gray
    mean = gaussian_mean_slider.get()
    sigma = gaussian_sigma_slider.get()
    gaussian_noise = np.random.normal(mean, sigma, img_gray.shape)
    noisy_img = np.clip(img_gray + gaussian_noise, 0, 255).astype(np.uint8)
    img_gray = noisy_img
    display_image(noisy_img, "Gaussian Noise")

def median_filter_1xN():
    global img_gray
    ksize = filter_slider.get()
    if ksize % 2 == 0:
        ksize += 1
    filtered_img = cv2.medianBlur(img_gray, (1, ksize)[1])
    img_gray = filtered_img
    display_image(filtered_img, "Filtered 1xN")

def median_filter_Nx1():
    global img_gray
    ksize = filter_slider.get()
    if ksize % 2 == 0:
        ksize += 1
    filtered_img = cv2.medianBlur(img_gray, (ksize, 1)[0])
    img_gray = filtered_img
    display_image(filtered_img, "Filtered Nx1")

def choose_bg_color():
    color = colorchooser.askcolor()[1]
    if color:
        root.config(bg=color)
        frame.config(bg=color)
        btn_frame.config(bg=color)
        slider_frame.config(bg=color)
        color_frame.config(bg=color)
        label.config(bg=color)
        label_text.set("Select an Image")

def choose_button_color():
    color = colorchooser.askcolor()[1]
    if color:
        btn_open.config(bg=color)
        btn_noise_salt_pepper.config(bg=color)
        btn_noise_gaussian.config(bg=color)
        btn_filter_1xN.config(bg=color)
        btn_filter_Nx1.config(bg=color)
        btn_color.config(bg=color)
        btn_button_color.config(bg=color)
        filter_slider.config(bg=color)
        salt_pepper_slider.config(bg=color)
        gaussian_mean_slider.config(bg=color)
        gaussian_sigma_slider.config(bg=color)

root = tk.Tk()
root.title("Median Filter")
root.geometry("950x600")
root.config(bg='#ffffff')

frame = tk.Frame(root, bg='#ffffff')
frame.grid(row=0, column=0, columnspan=3, pady=20)

label_text = tk.StringVar()
label_text.set("Select an Image")
label = tk.Label(frame, textvariable=label_text, bg='#ffffff', font=('Helvetica', 14))
label.grid(row=0, column=0, columnspan=3)

btn_frame = tk.Frame(root, bg='#ffffff')
btn_frame.grid(row=1, column=0, padx=20, pady=10)

btn_open = tk.Button(btn_frame, text="Open Image", command=open_image, bg='#ffffff', font=('Helvetica', 12))
btn_open.grid(row=0, column=0, padx=10, pady=5)

btn_noise_salt_pepper = tk.Button(btn_frame, text="Add Salt and Pepper Noise", command=add_salt_and_pepper_noise, bg='#ffffff', font=('Helvetica', 12))
btn_noise_salt_pepper.grid(row=1, column=0, padx=10, pady=5)

btn_noise_gaussian = tk.Button(btn_frame, text="Add Gaussian Noise", command=add_gaussian_noise, bg='#ffffff', font=('Helvetica', 12))
btn_noise_gaussian.grid(row=2, column=0, padx=10, pady=5)

btn_filter_1xN = tk.Button(btn_frame, text="Apply 1xN Median Filter", command=median_filter_1xN, bg='#ffffff', font=('Helvetica', 12))
btn_filter_1xN.grid(row=3, column=0, padx=10, pady=5)

btn_filter_Nx1 = tk.Button(btn_frame, text="Apply Nx1 Median Filter", command=median_filter_Nx1, bg='#ffffff', font=('Helvetica', 12))
btn_filter_Nx1.grid(row=4, column=0, padx=10, pady=5)

slider_frame = tk.Frame(root, bg='#ffffff')
slider_frame.grid(row=1, column=1, padx=20, pady=10)

salt_pepper_slider = tk.Scale(slider_frame, from_=1, to=1000, orient='horizontal', bg='#ffffff', fg='black', sliderlength=20, length=200)
salt_pepper_slider.grid(row=0, column=0, padx=10, pady=5)

gaussian_mean_slider = tk.Scale(slider_frame, from_=0, to=255, orient='horizontal', bg='#ffffff', fg='black', sliderlength=20, length=200)
gaussian_mean_slider.grid(row=1, column=0, padx=10, pady=5)

gaussian_sigma_slider = tk.Scale(slider_frame, from_=0, to=100, orient='horizontal', bg='#ffffff', fg='black', sliderlength=20, length=200)
gaussian_sigma_slider.grid(row=2, column=0, padx=10, pady=5)

filter_slider = tk.Scale(slider_frame, from_=1, to=21, orient='horizontal', bg='#ffffff', fg='black', sliderlength=20, length=200)
filter_slider.grid(row=3, column=0, padx=10, pady=5)

color_frame = tk.Frame(root, bg='#ffffff')
color_frame.grid(row=1, column=2, padx=20, pady=10)

btn_color = tk.Button(color_frame, text="Choose Background Color", command=choose_bg_color, bg='#ffffff', font=('Helvetica', 12))
btn_color.grid(row=0, column=0, padx=10, pady=5)

btn_button_color = tk.Button(color_frame, text="Choose Button and Slider Color", command=choose_button_color, bg='#ffffff', font=('Helvetica', 12))
btn_button_color.grid(row=1, column=0, padx=10, pady=5)

root.mainloop()
