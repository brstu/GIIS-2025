import cv2
import numpy as np
from matplotlib import pyplot as plt
from tkinter import Tk, Button, Label, OptionMenu, StringVar, Entry
from PIL import Image, ImageTk
import tkinter.filedialog as fd

def add_salt_and_pepper_noise(image, noise_level=0.02, method='random'):
    noisy_image = image.copy()
    total_pixels = image.shape[0] * image.shape[1]
    num_noise = int(total_pixels * noise_level)

    if method == 'random':
        indices = np.random.choice(total_pixels, num_noise, replace=False)
    elif method == 'grid':
        indices = np.arange(0, total_pixels, max(1, total_pixels // num_noise))
    elif method == 'diagonal':
        indices = [(i * image.shape[1] + i) % total_pixels for i in range(num_noise)]
    else:
        raise ValueError("Неподдерживаемый метод зашумления")

    for index in indices:
        y, x = divmod(index, image.shape[1])
        if len(image.shape) == 3:
            noisy_image[y, x] = [255, 255, 255] if (x + y) % 2 == 0 else [0, 0, 0]
        else:
            noisy_image[y, x] = 255 if (x + y) % 2 == 0 else 0

    return noisy_image

def median_filter_1D(image, kernel_size, axis):
    if axis == 0:
        return cv2.medianBlur(image, kernel_size)
    elif axis == 1:
        return cv2.medianBlur(image.T, kernel_size).T

def median_filter_combined(image, kernel_size):
    filtered_rows = median_filter_1D(image, kernel_size, axis=0)
    filtered_cols = median_filter_1D(filtered_rows, kernel_size, axis=1)
    return filtered_cols

def process_image(image, noise_level=0.02, kernel_size=3, noise_method='random'):
    noisy_image = add_salt_and_pepper_noise(image, noise_level, method=noise_method)
    filtered_image_rows = median_filter_1D(noisy_image, kernel_size, axis=0)
    filtered_image_cols = median_filter_1D(noisy_image, kernel_size, axis=1)
    filtered_image_combined = median_filter_combined(noisy_image, kernel_size)

    fig, axs = plt.subplots(1, 4, figsize=(20, 5))
    axs[0].imshow(image)
    axs[0].set_title("Исходное изображение")
    axs[1].imshow(noisy_image)
    axs[1].set_title(f"Зашумленное изображение ({noise_method})")
    axs[2].imshow(filtered_image_rows)
    axs[2].set_title("Фильтр по строкам")
    axs[3].imshow(filtered_image_cols)
    axs[3].set_title("Фильтр по столбцам")

    plt.figure(figsize=(5, 5))
    plt.imshow(filtered_image_combined)
    plt.title("Фильтр по строкам и столбцам")
    plt.axis("off")
    plt.show()

def open_image_and_process(noise_level, noise_method):
    image_path = fd.askopenfilename(title="Выберите изображение", filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp;*.tif")])
    if image_path:
        try:
            with Image.open(image_path) as img:
                image = np.array(img)
                process_image(image, noise_level=noise_level, kernel_size=5, noise_method=noise_method)
        except Exception as e:
            print(f"Ошибка загрузки изображения: {e}")

def create_gui():
    root = Tk()
    root.title("Настройки шума и обработки изображения")

    Label(root, text="Уровень шума (0-1):").grid(row=0, column=0)
    noise_level_var = StringVar(value="0.05")
    noise_level_entry = Entry(root, textvariable=noise_level_var)
    noise_level_entry.grid(row=0, column=1)

    Label(root, text="Метод шума:").grid(row=1, column=0)
    noise_method_var = StringVar(value="random")
    noise_method_menu = OptionMenu(root, noise_method_var, "random", "grid", "diagonal")
    noise_method_menu.grid(row=1, column=1)

    def on_process_image():
        noise_level = float(noise_level_var.get())
        noise_method = noise_method_var.get()
        open_image_and_process(noise_level, noise_method)

    process_button = Button(root, text="Загрузить изображение и обработать", command=on_process_image)
    process_button.grid(row=2, column=0, columnspan=2)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
