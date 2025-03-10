import numpy as np
from PIL import Image, ImageTk
import random
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt

def add_noise(image, noise_level):
    noisy_image = image.copy()
    num_noise_pixels = int(noise_level * image.size[0] * image.size[1]) #количество пикселей 
    for _ in range(num_noise_pixels):
        x = random.randint(0, image.size[0] - 1)
        y = random.randint(0, image.size[1] - 1)
        noisy_image.putpixel((x, y), (255, 255, 255) if random.random() > 0.5 else (0, 0, 0))
    return noisy_image

def threshold_filter(image, threshold):
    # Преобразуем изображение в оттенки серого
    grayscale_image = image.convert('L')

    # Применяем пороговый фильтр
    filtered_image = grayscale_image.point(lambda p: 255 if p > threshold else 0)

    # Проверка значений пикселей (для отладки)
    print(f"Threshold applied: {threshold}")
    print(f"Pixel values after threshold: {[filtered_image.getpixel((x, y)) for x in range(10) for y in range(10)]}")

    return filtered_image.convert('RGB')

def process_image():
    global original_image, noise_level, threshold
    noisy_image = add_noise(original_image, noise_level)
    filtered_image = threshold_filter(noisy_image, threshold)

    # Отображение изображений
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 3, 1)
    plt.title("Исходное изображение")
    plt.imshow(np.array(original_image))
    plt.axis('off')

    plt.subplot(1, 3, 2)
    plt.title("Зашумлённое изображение")
    plt.imshow(np.array(noisy_image))
    plt.axis('off')

    plt.subplot(1, 3, 3)
    plt.title("Отфильтрованное изображение")
    plt.imshow(np.array(filtered_image))
    plt.axis('off')

    plt.show()

def load_image():
    global original_image, img_label
    file_path = filedialog.askopenfilename()
    if file_path:
        original_image = Image.open(file_path).convert('RGB')
        original_image.thumbnail((400, 400))  # Уменьшаем размер для отображения
        img = ImageTk.PhotoImage(original_image)
        img_label.config(image=img)
        img_label.image = img  # Сохраняем ссылку на изображение
        messagebox.showinfo("Информация", "Изображение загружено успешно!")

def create_interface():
    global noise_level, threshold, img_label, noise_scale, threshold_scale
    root = tk.Tk()
    root.title("Фильтрация изображения")
    root.geometry("600x600")
    root.configure(bg="#f0f0f0")

    tk.Button(root, text="Загрузить изображение", command=load_image, bg="#4CAF50", fg="white", font=("Arial", 12)).pack(pady=10)

    tk.Label(root, text="Уровень зашумления (0-1):", bg="#f0f0f0", font=("Arial", 12)).pack()
    noise_scale = tk.Scale(root, from_=0, to=1, resolution=0.01, orient='horizontal', bg="#f0f0f0")
    noise_scale.pack()

    tk.Label(root, text="Порог фильтра (0-255):", bg="#f0f0f0", font=("Arial", 12)).pack()
    threshold_scale = tk.Scale(root, from_=0, to=255, orient='horizontal', bg="#f0f0f0")
    threshold_scale.pack()

    def update_values():
        global noise_level, threshold
        noise_level = noise_scale.get()
        threshold = threshold_scale.get()

    tk.Button(root, text="Применить фильтр", command=lambda: [update_values(), process_image()], bg="#2196F3", fg="white", font=("Arial", 12)).pack(pady=10)

    img_label = tk.Label(root, bg="#f0f0f0")
    img_label.pack(pady=10)

    root.mainloop()

original_image = None
noise_level = 0.1
threshold = 128

create_interface()