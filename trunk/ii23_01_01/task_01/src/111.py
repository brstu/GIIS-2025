import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk


def add_impulse_noise(image, noise_level):
    noisy = image.copy()
    num_noisy_pixels = int(noise_level * image.size)

    for _ in range(num_noisy_pixels):
        x = np.random.randint(0, image.shape[1])
        y = np.random.randint(0, image.shape[0])
        noisy[y, x] = 255 if np.random.rand() > 0.5 else 0

    return noisy


def apply_median_filter(image, ksize):
    channels = cv2.split(image)
    filtered = [cv2.medianBlur(c, ksize) for c in channels]
    return cv2.merge(filtered)


def open_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        global original_img, filtered_img
        original_img = cv2.imread(file_path)
        filtered_img = original_img.copy()
        show_images()


def show_images():
    if original_img is None:
        return

    # Original
    img1 = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)
    img1 = Image.fromarray(img1)
    img1 = ImageTk.PhotoImage(img1.resize((300, 300)))
    original_label.config(image=img1)
    original_label.image = img1

    # Filtered
    img2 = cv2.cvtColor(filtered_img, cv2.COLOR_BGR2RGB)
    img2 = Image.fromarray(img2)
    img2 = ImageTk.PhotoImage(img2.resize((300, 300)))
    filtered_label.config(image=img2)
    filtered_label.image = img2


def save_image():
    if filtered_img is not None:
        path = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
        if path:
            cv2.imwrite(path, filtered_img)


def apply_noise_and_filter():
    global filtered_img
    if original_img is None:
        return
    try:
        noise = noise_slider.get() / 100.0
        ksize = filter_slider.get()
        if ksize % 2 == 0:
            ksize += 1
        noisy = add_impulse_noise(original_img, noise)
        filtered_img = apply_median_filter(noisy, ksize)
        show_images()
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))


def remove_noise():
    global filtered_img
    if original_img is None:
        return
    try:
        ksize = filter_slider.get()
        if ksize % 2 == 0:
            ksize += 1
        filtered_img = apply_median_filter(original_img, ksize)
        show_images()
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))


# Интерфейс
root = tk.Tk()
root.title("Фильтрация изображений")

original_img = None
filtered_img = None

# Основной фрейм
main_frame = ttk.Frame(root)
main_frame.pack(padx=10, pady=10)

# Панель изображений
image_frame = ttk.Frame(main_frame)
image_frame.pack()

original_label = ttk.Label(image_frame, text="Оригинал")
original_label.pack(side=tk.LEFT, padx=5)

filtered_label = ttk.Label(image_frame, text="Фильтровано")
filtered_label.pack(side=tk.RIGHT, padx=5)

# Панель управления
control_frame = ttk.Frame(main_frame)
control_frame.pack(pady=10)

ttk.Button(control_frame, text="Открыть изображение", command=open_image).grid(row=0, column=0, padx=5)
ttk.Button(control_frame, text="Сохранить", command=save_image).grid(row=0, column=1, padx=5)

# Слайдер шума
ttk.Label(control_frame, text="Уровень шума (%)").grid(row=1, column=0, pady=5)
noise_slider = tk.Scale(control_frame, from_=0, to=100, orient=tk.HORIZONTAL)
noise_slider.set(10)
noise_slider.grid(row=1, column=1, pady=5)

# Слайдер фильтра
ttk.Label(control_frame, text="Размер фильтра").grid(row=2, column=0, pady=5)
filter_slider = tk.Scale(control_frame, from_=3, to=11, resolution=2, orient=tk.HORIZONTAL)
filter_slider.set(3)
filter_slider.grid(row=2, column=1, pady=5)

# Кнопки фильтрации
ttk.Button(control_frame, text="Применить шум + фильтр", command=apply_noise_and_filter).grid(row=3, column=0, columnspan=2, pady=10)
ttk.Button(control_frame, text="Удалить шум", command=remove_noise).grid(row=4, column=0, columnspan=2, pady=5)

root.mainloop()
