import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk

def add_impulse_noise(image, noise_level):
    """Добавление импульсных помех на изображение."""
    noisy_image = image.copy()
    num_noise_points = int(noise_level * image.size)

    for _ in range(num_noise_points):
        x = np.random.randint(0, image.shape[1])
        y = np.random.randint(0, image.shape[0])
        noisy_image[y, x] = 255 if np.random.rand() > 0.5 else 0

    return noisy_image

def apply_median_filter(image, kernel_size):
    """Применение медианного фильтра."""
    channels = cv2.split(image)
    filtered_channels = [cv2.medianBlur(channel, kernel_size) for channel in channels]
    return cv2.merge(filtered_channels)

def open_image():
    """Открыть изображение."""
    file_path = filedialog.askopenfilename()
    if file_path:
        global original_image, displayed_image
        original_image = cv2.imread(file_path, cv2.IMREAD_COLOR)  # Загружаем цветное изображение
        update_displayed_image(original_image)

def update_displayed_image(image):
    """Обновить отображаемое изображение."""
    global displayed_image
    displayed_image = image
    image_bgr = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Преобразование из BGR в RGB
    image_pil = Image.fromarray(image_bgr)
    image_tk = ImageTk.PhotoImage(image_pil)
    image_label.config(image=image_tk)
    image_label.image = image_tk

def save_image():
    """Сохранить текущее изображение."""
    if displayed_image is not None:
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")])
        if file_path:
            cv2.imwrite(file_path, displayed_image)

def apply_noise_and_filter():
    """Применить шум и фильтр."""
    if original_image is not None:
        try:
            noise_level = float(noise_level_var.get())
            kernel_size = int(kernel_size_var.get())

            if kernel_size % 2 == 0:
                raise ValueError("Размер окна фильтрации должен быть нечетным.")

            # Добавляем шум
            noisy_image = add_impulse_noise(original_image, noise_level)

            # Применяем медианный фильтр
            filtered_image = apply_median_filter(noisy_image, kernel_size)

            update_displayed_image(filtered_image)
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

def remove_noise():
    """Удалить шум с изображения без добавления нового."""
    if original_image is not None:
        try:
            kernel_size = int(kernel_size_var.get())

            if kernel_size % 2 == 0:
                raise ValueError("Размер окна фильтрации должен быть нечетным.")

            # Применяем медианный фильтр
            filtered_image = apply_median_filter(original_image, kernel_size)

            update_displayed_image(filtered_image)
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))

# Создание интерфейса
root = tk.Tk()
root.title("Фильтрация изображений")

original_image = None
displayed_image = None

frame = ttk.Frame(root)
frame.pack(padx=10, pady=10)

image_label = ttk.Label(frame)
image_label.pack()

controls_frame = ttk.Frame(frame)
controls_frame.pack(pady=10)

open_button = ttk.Button(controls_frame, text="Открыть изображение", command=open_image)
open_button.grid(row=0, column=0, padx=5)

save_button = ttk.Button(controls_frame, text="Сохранить изображение", command=save_image)
save_button.grid(row=0, column=1, padx=5)

noise_level_label = ttk.Label(controls_frame, text="Уровень шума (0-1):")
noise_level_label.grid(row=1, column=0, pady=5, sticky="e")

noise_level_var = tk.StringVar(value="0.1")
noise_level_entry = ttk.Entry(controls_frame, textvariable=noise_level_var)
noise_level_entry.grid(row=1, column=1, pady=5, sticky="w")

kernel_size_label = ttk.Label(controls_frame, text="Размер окна фильтрации:")
kernel_size_label.grid(row=2, column=0, pady=5, sticky="e")

kernel_size_var = tk.StringVar(value="3")
kernel_size_entry = ttk.Entry(controls_frame, textvariable=kernel_size_var)
kernel_size_entry.grid(row=2, column=1, pady=5, sticky="w")

# Убираем выпадающий список для фильтра
apply_button = ttk.Button(controls_frame, text="Применить шум и фильтр", command=apply_noise_and_filter)
apply_button.grid(row=3, column=0, columnspan=2, pady=10)

remove_noise_button = ttk.Button(controls_frame, text="Удалить шум", command=remove_noise)
remove_noise_button.grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()
