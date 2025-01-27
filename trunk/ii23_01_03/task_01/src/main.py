import cv2
import numpy as np
import matplotlib.pyplot as plt


def add_noise(image, noise_type="points", noise_level=0.05):
    noisy_image = image.copy()
    h, w = image.shape[:2]
    num_noise = int(noise_level * h * w)

    if noise_type == "points":
        for _ in range(num_noise):
            x, y = np.random.randint(0, w), np.random.randint(0, h)
            noisy_image[y, x] = np.random.choice([0, 255])
    return noisy_image


def cross_median_filter(image, window_size=3, center=(1, 1)):
    padded_image = cv2.copyMakeBorder(image, window_size // 2, window_size // 2, window_size // 2, window_size // 2,
                                      cv2.BORDER_REFLECT)
    filtered_image = np.zeros_like(image)
    h, w = image.shape

    offsets = []
    for i in range(-window_size // 2, window_size // 2 + 1):
        offsets.append((i, 0))  # Vertical cross
        offsets.append((0, i))  # Horizontal cross

    for y in range(h):
        for x in range(w):
            pixel_values = []
            for dy, dx in offsets:
                cy, cx = y + dy + center[0], x + dx + center[1]
                if 0 <= cy < h + window_size and 0 <= cx < w + window_size:
                    pixel_values.append(padded_image[cy, cx])

            filtered_image[y, x] = np.median(pixel_values)

    return filtered_image


def main():
    file_path = input("Введите путь к изображению: ")
    image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print("Ошибка: не удалось загрузить изображение.")
        return

    noise_type = input("Тип шума (points/...): ").strip().lower()
    noise_level = float(input("Уровень шума (0-1): "))
    window_size = int(input("Размер окна фильтрации (нечетное число): "))
    center_x = int(input("Смещение центра по x: "))
    center_y = int(input("Смещение центра по y: "))

    noisy_image = add_noise(image, noise_type=noise_type, noise_level=noise_level)

    filtered_image = cross_median_filter(noisy_image, window_size=window_size, center=(center_y, center_x))

    plt.figure(figsize=(12, 6))
    plt.subplot(1, 3, 1)
    plt.title("Исходное изображение")
    plt.imshow(image, cmap="gray")
    plt.axis("off")

    plt.subplot(1, 3, 2)
    plt.title("Зашумленное изображение")
    plt.imshow(noisy_image, cmap="gray")
    plt.axis("off")

    plt.subplot(1, 3, 3)
    plt.title("Отфильтрованное изображение")
    plt.imshow(filtered_image, cmap="gray")
    plt.axis("off")

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
