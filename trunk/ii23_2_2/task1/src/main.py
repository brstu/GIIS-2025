import cv2
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

def generate_noise(img, level=0.02, pattern='random'):
    output = img.copy()
    total_pixels = img.shape[0] * img.shape[1]
    num_noisy = int(total_pixels * level)
    
    noise_indices = {
        'random': np.random.choice(total_pixels, num_noisy, replace=False),
        'grid': np.linspace(0, total_pixels - 1, num_noisy, dtype=int),
        'diagonal': [(i * img.shape[1] + i) % total_pixels for i in range(num_noisy)]
    }.get(pattern, [])
    
    if noise_indices is None or len(noise_indices) == 0:
        raise ValueError("Invalid noise pattern")
    
    for idx in noise_indices:
        y, x = divmod(idx, img.shape[1])
        if len(img.shape) == 3:
            output[y, x] = [255, 255, 255] if (y + x) % 2 == 0 else [0, 0, 0]
        else:
            output[y, x] = 255 if (y + x) % 2 == 0 else 0
    
    return output

def apply_median_blur(image, k_size, transpose=False):
    return cv2.medianBlur(image.T if transpose else image, k_size).T if transpose else cv2.medianBlur(image, k_size)

def filter_image(img_data, kernel_size):
    step1 = apply_median_blur(img_data, kernel_size)
    return apply_median_blur(step1, kernel_size, transpose=True)

def visualize_results(original, noisy, filtered_x, filtered_y, combined):
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))
    titles = ["Original", "Noisy", "Filtered (X)", "Filtered (Y)"]
    images = [original, noisy, filtered_x, filtered_y]
    
    for ax, img, title in zip(axes, images, titles):
        ax.imshow(img, cmap='gray' if len(img.shape) == 2 else None)
        ax.set_title(title)
    
    plt.figure(figsize=(5, 5))
    plt.imshow(combined, cmap='gray' if len(combined.shape) == 2 else None)
    plt.title("Fully Filtered")
    plt.axis("off")
    plt.show()

def process_image(img_array, noise_intensity=0.02, filter_size=3, noise_mode='random'):
    if img_array is None or img_array.size == 0:
        print("Invalid image data")
        return
    
    noisy_img = generate_noise(img_array, noise_intensity, pattern=noise_mode)
    filtered_x = apply_median_blur(noisy_img, filter_size)
    filtered_y = apply_median_blur(noisy_img, filter_size, transpose=True)
    final_result = filter_image(noisy_img, filter_size)
    visualize_results(img_array, noisy_img, filtered_x, filtered_y, final_result)

def select_image():
    file_path = filedialog.askopenfilename(title="Choose an Image", filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp;*.tif")])
    if not file_path:
        return
    
    try:
        with Image.open(file_path) as img:
            img = img.convert('RGB')
            img_arr = np.array(img)
            if img_arr is None or img_arr.size == 0:
                print("Error: Loaded image is empty or invalid.")
                return
            process_image(img_arr, noise_intensity=0.05, filter_size=5, noise_mode='random')
    except Exception as e:
        print(f"Error loading image: {e}")

def create_ui():
    root = tk.Tk()
    root.title("Noise & Filtering")
    
    tk.Label(root, text="Noise Level (0-1):").grid(row=0, column=0)
    noise_lvl_var = tk.StringVar(value="0.05")
    tk.Entry(root, textvariable=noise_lvl_var).grid(row=0, column=1)
    
    tk.Label(root, text="Noise Type:").grid(row=1, column=0)
    noise_type_var = tk.StringVar(value="random")
    tk.OptionMenu(root, noise_type_var, "random", "grid", "diagonal").grid(row=1, column=1)
    
    def process():
        select_image()
    
    tk.Button(root, text="Load & Process Image", command=process).grid(row=2, column=0, columnspan=2)
    root.mainloop()

if __name__ == "__main__":
    create_ui()
