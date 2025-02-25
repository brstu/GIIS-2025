import cv2
import numpy as np
import secrets
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, simpledialog


def add_noise(image, noise_level=0.05, noise_type='points'):
    if image is None:
        raise ValueError("Ошибка загрузки изображения. Проверьте путь к файлу.")

    noisy_img = image.copy()
    h, w, c = image.shape
    num_pixels = int(noise_level * h * w)

    if noise_type == 'points':
        for _ in range(num_pixels):
            x, y = secrets.randbelow(w), secrets.randbelow(h)
            noisy_img[y, x] = [255, 255, 255] if secrets.randbits(1) else [0, 0, 0]
    elif noise_type == 'lines':
        for _ in range(int(num_pixels / 100)):
            x1, y1 = secrets.randbelow(w), secrets.randbelow(h)
            x2, y2 = secrets.randbelow(w), secrets.randbelow(h)
            cv2.line(noisy_img, (x1, y1), (x2, y2), (255, 255, 255), 1)
    return noisy_img


def median_filter_color(image, window_size=3):
    return cv2.medianBlur(image, window_size)


def process_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Ошибка загрузки изображения: {image_path}. Проверьте путь и формат файла.")

    root = tk.Tk()
    root.withdraw()
    noise_level = simpledialog.askfloat("Шум", "Выберите уровень шума (0-1):", minvalue=0, maxvalue=1, initialvalue=0.1)
    window_size = simpledialog.askinteger("Размер окна", "Введите размер окна фильтрации (нечетное число, >=3):",
                                          minvalue=3, initialvalue=3)
    if window_size % 2 == 0:
        window_size += 1  # Окно должно быть нечетным

    noisy_image = add_noise(image, noise_level)
    filtered_image = median_filter_color(noisy_image, window_size)

    plt.figure(figsize=(12, 6))
    plt.subplot(1, 3, 1)
    plt.title('Original')
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.subplot(1, 3, 2)
    plt.title('Noisy')
    plt.imshow(cv2.cvtColor(noisy_image, cv2.COLOR_BGR2RGB))
    plt.subplot(1, 3, 3)
    plt.title('Filtered')
    plt.imshow(cv2.cvtColor(filtered_image, cv2.COLOR_BGR2RGB))
    plt.show()

    save_image(filtered_image)


def open_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if not file_path:
        return
    process_image(file_path)


def save_image(image):
    file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG Files", "*.png"), ("JPG Files", "*.jpg"),
                                                        ("All Files", "*.*")])
    if file_path:
        cv2.imwrite(file_path, image)


if __name__ == "__main__":
    open_image()
