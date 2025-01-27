import cv2
import numpy as np
from tkinter import Tk, Canvas, Button, filedialog, StringVar, DoubleVar, IntVar, OptionMenu, Scale, Label, Entry
from PIL import Image, ImageTk

original_image = None
noisy_image = None
filtered_image = None
restored_image = None

def resize_to_fit(image, width, height):
    h, w = image.shape[:2]
    scale = min(width / w, height / h)
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(image, (new_w, new_h))

def open_image():
    global original_image, tk_original_image
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if not file_path:
        return

    image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        print("Ошибка: не удалось загрузить изображение. Проверьте формат файла.")
        return

    original_image = image
    resized_image = resize_to_fit(image, canvas_width, canvas_height)

    img = Image.fromarray(resized_image)
    tk_original_image = ImageTk.PhotoImage(img)

    original_canvas.create_image(0, 0, anchor="nw", image=tk_original_image)
    original_canvas.image = tk_original_image

def add_noise():
    global noisy_image, tk_noisy_image

    if original_image is None:
        print("Сначала загрузите изображение!")
        return

    noise_type = noise_type_var.get()
    noise_level = noise_level_var.get()

    noisy_image = add_noise_to_image(original_image, noise_type, noise_level)

    resized_noisy_image = resize_to_fit(noisy_image, canvas_width, canvas_height)
    tk_noisy_image = ImageTk.PhotoImage(Image.fromarray(resized_noisy_image))

    noisy_canvas.create_image(0, 0, anchor="nw", image=tk_noisy_image)
    noisy_canvas.image = tk_noisy_image

def add_noise_to_image(image, noise_type="points", noise_level=0.05):
    noisy_image = image.copy()
    h, w = image.shape[:2]
    num_noise = int(noise_level * h * w)

    if noise_type == "points":
        for _ in range(num_noise):
            x, y = np.random.randint(0, w), np.random.randint(0, h)
            noisy_image[y, x] = np.random.choice([0, 255])
    return noisy_image

def apply_filter():
    global filtered_image, tk_filtered_image

    if noisy_image is None:
        print("Сначала добавьте шум к изображению!")
        return

    window_size = filter_window_var.get()
    center_x = filter_center_x_var.get()
    center_y = filter_center_y_var.get()

    filtered_image = cross_median_filter(noisy_image, window_size, (center_y, center_x))

    resized_filtered_image = resize_to_fit(filtered_image, canvas_width, canvas_height)
    tk_filtered_image = ImageTk.PhotoImage(Image.fromarray(resized_filtered_image))

    filtered_canvas.create_image(0, 0, anchor="nw", image=tk_filtered_image)
    filtered_canvas.image = tk_filtered_image

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

def restore_image():
    global restored_image, tk_filtered_image

    if noisy_image is None:
        print("Сначала добавьте шум к изображению!")
        return

    restored_image = original_image.copy()

    resized_restored_image = resize_to_fit(restored_image, canvas_width, canvas_height)
    tk_filtered_image = ImageTk.PhotoImage(Image.fromarray(resized_restored_image))

    filtered_canvas.create_image(0, 0, anchor="nw", image=tk_filtered_image)
    filtered_canvas.image = tk_filtered_image

root = Tk()
root.title("Обработка изображений")

canvas_width = 300
canvas_height = 300

original_canvas = Canvas(root, width=canvas_width, height=canvas_height, bg="white")
original_canvas.grid(row=0, column=0, padx=10, pady=10)
original_canvas.create_text(150, 150, text="Оригинал", fill="gray")

noisy_canvas = Canvas(root, width=canvas_width, height=canvas_height, bg="white")
noisy_canvas.grid(row=0, column=1, padx=10, pady=10)
noisy_canvas.create_text(150, 150, text="Шум", fill="gray")

filtered_canvas = Canvas(root, width=canvas_width, height=canvas_height, bg="white")
filtered_canvas.grid(row=0, column=2, padx=10, pady=10)
filtered_canvas.create_text(150, 150, text="Фильтр/Восстановление", fill="gray")

noise_type_var = StringVar(value="points")
Label(root, text="Тип шума").grid(row=1, column=0, pady=5)
OptionMenu(root, noise_type_var, "points").grid(row=1, column=1, pady=5)

noise_level_var = DoubleVar(value=0.05)
Label(root, text="Уровень шума").grid(row=2, column=0, pady=5)
Scale(root, from_=0, to=1, resolution=0.01, orient="horizontal", variable=noise_level_var).grid(row=2, column=1, pady=5)

filter_window_var = IntVar(value=3)
filter_center_x_var = IntVar(value=1)
filter_center_y_var = IntVar(value=1)

Label(root, text="Размер окна").grid(row=3, column=0, pady=5)
Entry(root, textvariable=filter_window_var).grid(row=3, column=1, pady=5)

Label(root, text="Центр X").grid(row=4, column=0, pady=5)
Entry(root, textvariable=filter_center_x_var).grid(row=4, column=1, pady=5)

Label(root, text="Центр Y").grid(row=5, column=0, pady=5)
Entry(root, textvariable=filter_center_y_var).grid(row=5, column=1, pady=5)

Button(root, text="Загрузить изображение", command=open_image).grid(row=6, column=0, pady=10)
Button(root, text="Добавить шум", command=add_noise).grid(row=6, column=1, pady=10)
Button(root, text="Применить фильтр", command=apply_filter).grid(row=6, column=2, pady=10)
Button(root, text="Восстановить изображение", command=restore_image).grid(row=7, column=2, pady=10)

root.mainloop()
