import cv2
import numpy as np
import random
import matplotlib.pyplot as plt


def add_noise(image, noise_level):
    noisy_image = image.copy()
    rows, cols = noisy_image.shape

    # Добавление точек (шум)
    num_points = int(noise_level * rows * cols)
    for _ in range(num_points):
        x, y = random.randint(0, rows - 1), random.randint(0, cols - 1)
        noisy_image[x, y] = random.choice([0, 255])

    # Добавление линий
    num_lines = int(noise_level * 10)  # Регулируемое количество линий
    for _ in range(num_lines):
        x1, y1 = random.randint(0, rows - 1), random.randint(0, cols - 1)
        x2, y2 = random.randint(0, rows - 1), random.randint(0, cols - 1)
        color = random.choice([0, 255])  # Белая или черная линия
        cv2.line(noisy_image, (y1, x1), (y2, x2), color, thickness=1)

    return noisy_image


def threshold_filter(image, threshold, window_size):
    filtered_image = np.zeros_like(image)
    rows, cols = image.shape
    offset = window_size // 2

    for i in range(offset, rows - offset):
        for j in range(offset, cols - offset):
            window = image[i - offset:i + offset + 1, j - offset:j + offset + 1]
            if np.mean(window) >= threshold:
                filtered_image[i, j] = 255
            else:
                filtered_image[i, j] = 0

    return filtered_image


# Параметры
input_image_file = 't1.jpg'  # Замените на ваш путь
noise_level = 0.2  # Уровень зашумления (0.0 - 1.0)
threshold = 128  # Значение порога фильтра
window_size = 3  # Размер окна фильтра

# Загрузка изображения
original_image = cv2.imread(input_image_file, cv2.IMREAD_GRAYSCALE)
if original_image is None:
    raise FileNotFoundError("Изображение не найдено!")

# Добавление шума
noisy_image = add_noise(original_image, noise_level)

# Применение порогового фильтра
filtered_image = threshold_filter(noisy_image, threshold, window_size)

# Визуализация изображений
plt.figure(figsize=(12, 6))
plt.subplot(1, 3, 1)
plt.title("Исходное изображение")
plt.imshow(original_image, cmap='gray')

plt.subplot(1, 3, 2)
plt.title("Зашумленное изображение")
plt.imshow(noisy_image, cmap='gray')

plt.subplot(1, 3, 3)
plt.title("Отфильтрованное изображение")
plt.imshow(filtered_image, cmap='gray')

plt.show()
