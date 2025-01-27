import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import numpy as np
import cv2

class ImageViewerApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Noise Canceller")
        self.root.geometry("1000x800")
        self.file_name = None
        self.image = None
        self.image_array = None
        self.edit_im = None
        self.init_ui()

    def init_ui(self):
        # Main Frames
        self.image_frame = tk.Frame(self.root, height=400)
        self.image_frame.pack(fill=tk.BOTH, expand=False)

        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(fill=tk.X)

        self.tab_frame = tk.Frame(self.root)
        self.tab_frame.pack(fill=tk.BOTH, expand=False)

        # Image labels
        self.image_label1 = tk.Label(self.image_frame, text="Original Image", bg="lightgray")
        self.image_label1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.image_label2 = tk.Label(self.image_frame, text="Edited Image", bg="lightgray")
        self.image_label2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Control buttons
        self.load_button = tk.Button(self.control_frame, text="Load Image", command=self.load_image)
        self.load_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.use_button = tk.Button(self.control_frame, text="Use", command=self.use_function)
        self.use_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.save_button = tk.Button(self.control_frame, text="Save Image", command=self.save_image)
        self.save_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Tabs
        self.tab_control = ttk.Notebook(self.tab_frame)
        self.tab_control.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.noise_tab = ttk.Frame(self.tab_control)
        self.recover_tab = ttk.Frame(self.tab_control)
        self.ai_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.noise_tab, text="Make Noise")
        self.tab_control.add(self.recover_tab, text="Recover Photo")
        self.tab_control.add(self.ai_tab, text="AI Photo")

        # Noise tab controls
        self.noise_slider = tk.Scale(self.noise_tab, from_=0, to=10, orient=tk.HORIZONTAL, label="Noise Level")
        self.noise_slider.pack(pady=1)

        self.noise_button = tk.Button(self.noise_tab, text="Make Noise", command=self.make_noise)
        self.noise_button.pack(pady=1)

        # Recover tab controls
        self.size_slider = tk.Scale(self.recover_tab, from_=3, to=15, orient=tk.HORIZONTAL, label="Size", resolution=2)
        self.size_slider.set(3)
        self.size_slider.pack(pady=1)

        self.x_slider = tk.Scale(self.recover_tab, from_=0, to=15, orient=tk.HORIZONTAL, label="Cross Center X",
                                 resolution=1)
        self.x_slider.set(3)
        self.x_slider.pack(pady=1)

        self.y_slider = tk.Scale(self.recover_tab, from_=0, to=15, orient=tk.HORIZONTAL, label="Cross Center Y",
                                 resolution=1)
        self.y_slider.set(3)
        self.y_slider.pack(pady=1)

        self.recover_button = tk.Button(self.recover_tab, text="Recover", command=self.recover)
        self.recover_button.pack(pady=1)

        self.size_slider.bind("<Motion>", self.update_xy_range)

        # AI tab controls
        self.gaussian_slider = tk.Scale(self.ai_tab, from_=1, to=31, orient=tk.HORIZONTAL, label="Gaussian Blur",
                                        resolution=2)
        self.gaussian_slider.set(3)
        self.gaussian_slider.grid(row=0, column=0, padx=1, pady=1)

        self.gaussian_button = tk.Button(self.ai_tab, text="Apply Gaussian Blur", command=self.apply_gaussian_blur)
        self.gaussian_button.grid(row=0, column=1, padx=1, pady=1)

        self.filter1_slider = tk.Scale(self.ai_tab, from_=50, to=150, orient=tk.HORIZONTAL, label="Filter Threshold1",
                                       resolution=1)
        self.filter1_slider.set(50)
        self.filter1_slider.grid(row=1, column=0, padx=1, pady=1)

        self.filter2_slider = tk.Scale(self.ai_tab, from_=150, to=250, orient=tk.HORIZONTAL, label="Filter Threshold2",
                                       resolution=1)
        self.filter2_slider.set(150)
        self.filter2_slider.grid(row=2, column=0, padx=1, pady=1)

        self.canny_button = tk.Button(self.ai_tab, text="Apply Canny Edge Detection",
                                      command=self.apply_canny_edge_detection)
        self.canny_button.grid(row=2, column=1, padx=1, pady=1)

        self.kmeans_slider = tk.Scale(self.ai_tab, from_=2, to=10, orient=tk.HORIZONTAL, label="K-means", resolution=1)
        self.kmeans_slider.set(3)
        self.kmeans_slider.grid(row=3, column=0, padx=1, pady=1)

        self.kmeans_button = tk.Button(self.ai_tab, text="Apply K-means", command=self.apply_kmeans_clustering)
        self.kmeans_button.grid(row=3, column=1, padx=1, pady=1)

        self.transform_slider = tk.Scale(self.ai_tab, from_=0, to=360, orient=tk.HORIZONTAL, label="Transform",
                                         resolution=1)
        self.transform_slider.set(0)
        self.transform_slider.grid(row=4, column=0, padx=1, pady=1)

        self.rotation_button = tk.Button(self.ai_tab, text="Apply Rotation", command=self.apply_rotation)
        self.rotation_button.grid(row=4, column=1, padx=1, pady=1)

        self.upgrade_button = tk.Button(self.ai_tab, text="Apply Histogram Equalization",
                                        command=self.apply_histogram_equalization)
        self.upgrade_button.grid(row=5, column=1, padx=1, pady=1)

        # Progress bar
        self.progress_bar = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress_bar.pack(pady=1)


    def load_image(self):
        file_name = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
        )
        if file_name:
            self.file_name = file_name
            self.image = Image.open(file_name)
            self.image_array = np.array(self.image)  # Сохраняем numpy-массив для работы
            self.display_image(self.image, self.image_label1)
            self.display_image(self.image, self.image_label2)

    def save_image(self):
        if self.edit_im:
            file_name = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
            )
            if file_name:
                self.edit_im.save(file_name)
        else:
            messagebox.showerror("Error", "No edited image to save.")

    def display_image(self, image, label):
        image.thumbnail((600, 600))
        tk_image = ImageTk.PhotoImage(image)
        label.config(image=tk_image)
        label.image = tk_image

    def make_noise(self):
        if self.image_array is not None:
            image = self.image_array.copy()
            noise_level = self.noise_slider.get()

            height, width, channels = image.shape
            if channels == 4:
                colors = np.random.randint(0, 255, (round(noise_level / 100 * height * width), 3), dtype=np.uint8)
                x_coords = np.random.randint(0, width, colors.shape[0])
                y_coords = np.random.randint(0, height, colors.shape[0])

                for i in range(colors.shape[0]):
                    image[y_coords[i], x_coords[i], :3] = colors[i]
            else:
                num_pixels_to_alter = round(noise_level / 100 * height * width)
                x_coords = np.random.randint(0, width, num_pixels_to_alter)
                y_coords = np.random.randint(0, height, num_pixels_to_alter)
                colors = np.random.randint(0, 255, (num_pixels_to_alter, 3), dtype=np.uint8)
                image[y_coords, x_coords] = colors

            self.edit_im = Image.fromarray(image)
            self.display_image(self.edit_im, self.image_label2)
        else:
            messagebox.showerror("Error", "No image loaded.")

    def update_xy_range(self, event):
        # Получаем текущее значение слайдера размера
        size = self.size_slider.get()

        # Обновляем максимальные значения для слайдеров X и Y
        max_val = size - 1
        self.x_slider.config(to=max_val)
        self.y_slider.config(to=max_val)

    def recover(self):
        if self.image_array is not None:
            try:

                self.load_button.config(state=tk.DISABLED)
                self.use_button.config(state=tk.DISABLED)
                self.save_button.config(state=tk.DISABLED)
                self.progress_bar['value'] = 0
                self.root.update_idletasks()

                edit_im = self.image_array.copy()
                height, width, channels = edit_im.shape

                size = self.size_slider.get()
                x = self.x_slider.get()
                y = self.y_slider.get()

                if size < 3 or size % 2 == 0:
                    messagebox.showerror("Error", "Kernel size must be an odd number greater than or equal to 3.")
                    return
                if x >= size or y >= size:
                    messagebox.showerror("Error", "Cross center must be within kernel size.")
                    return

                kernel = np.zeros((size, size), dtype=np.uint8)
                kernel[x, :] = 1
                kernel[:, y] = 1

                top_padding = y
                bottom_padding = size - y - 1
                left_padding = x
                right_padding = size - x - 1
                edit_im = np.pad(edit_im,
                                 ((top_padding, bottom_padding), (left_padding, right_padding), (0, 0)),
                                 mode="constant")

                padded_height, padded_width, _ = edit_im.shape
                num_of_zeros = size ** 2 - 2 * size + 1
                median = int((size - 1) / 2 + 1)
                filter_im = np.zeros_like(edit_im, dtype=np.uint8)

                num_of_iterations = (padded_height - top_padding - bottom_padding) * (
                        padded_width - left_padding - right_padding) * channels
                k = 0

                for i in range(top_padding, padded_height - bottom_padding):
                    for j in range(left_padding, padded_width - right_padding):
                        for c in range(channels):
                            region = (edit_im[i - top_padding:i + bottom_padding + 1,
                                      j - left_padding:j + right_padding + 1, c] * kernel).flatten()
                            sorted_values = np.sort(region)
                            filter_im[i, j, c] = sorted_values[num_of_zeros:][median]

                        k += 1
                        progress_value = int(k / num_of_iterations * 100)
                        if k%1000 == 0:
                            self.progress_bar['value'] = progress_value
                            self.root.update_idletasks()

                edit_im = filter_im[top_padding:padded_height - bottom_padding,
                          left_padding:padded_width - right_padding, :]
                edit_im = edit_im.astype(np.uint8)

                self.edit_im = Image.fromarray(edit_im)
                self.display_image(self.edit_im, self.image_label2)

                self.progress_bar['value'] = 100
            finally:
                self.load_button.config(state=tk.NORMAL)
                self.use_button.config(state=tk.NORMAL)
                self.save_button.config(state=tk.NORMAL)
        else:
            messagebox.showerror("Error", "No image loaded.")

    def use_function(self):
        if self.edit_im:
            self.image_array = np.array(self.edit_im)
            self.display_image(self.edit_im, self.image_label1)
        else:
            messagebox.showerror("Error", "No changes to apply.")

    def apply_gaussian_blur(self):
        if self.image_array is not None:
            filter_size = self.gaussian_slider.get()
            self.edit_im = cv2.GaussianBlur(self.image_array, (filter_size, filter_size), 0)
            self.edit_im = Image.fromarray(cv2.cvtColor(self.edit_im, cv2.COLOR_BGR2RGB))
            self.display_image(self.edit_im, self.image_label2)
        else:
            messagebox.showerror("Error", "No image loaded.")

    def apply_canny_edge_detection(self):
        if self.image_array is not None:
            filter1 = self.filter1_slider.get()
            filter2 = self.filter2_slider.get()
            gray_image = cv2.cvtColor(self.image_array, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray_image, filter1, filter2)
            self.edit_im = Image.fromarray(edges)
            self.display_image(self.edit_im, self.image_label2)
        else:
            messagebox.showerror("Error", "No image loaded.")

    def apply_kmeans_clustering(self):
        if self.image_array is not None:
            k = self.kmeans_slider.get()
            pixel_values = self.image_array.reshape((-1, 3))
            pixel_values = np.float32(pixel_values)
            _, labels, centers = cv2.kmeans(pixel_values, k, None,(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2),10, cv2.KMEANS_RANDOM_CENTERS)
            centers = np.uint8(centers)
            segmented_image = centers[labels.flatten()]
            segmented_image = segmented_image.reshape(self.image_array.shape)
            self.edit_im = Image.fromarray(segmented_image)
            self.display_image(self.edit_im, self.image_label2)
        else:
            messagebox.showerror("Error", "No image loaded.")

    def apply_rotation(self):
        if self.image_array is not None:
            (h, w) = self.image_array.shape[:2]
            center = (int(w / 2), int(h / 2))
            matrix = cv2.getRotationMatrix2D(center, self.transform_slider.get(), 1.0)
            rotated_image = cv2.warpAffine(self.image_array, matrix, (w, h))
            self.edit_im = Image.fromarray(rotated_image)
            self.display_image(self.edit_im, self.image_label2)
        else:
            messagebox.showerror("Error", "No image loaded.")

    def apply_histogram_equalization(self):
        if self.image_array is not None:
            image = cv2.cvtColor(self.image_array, cv2.COLOR_BGR2YUV)
            image[:, :, 0] = cv2.equalizeHist(image[:, :, 0])
            equalized_image = cv2.cvtColor(image, cv2.COLOR_YUV2RGB)
            self.edit_im = Image.fromarray(equalized_image)
            self.display_image(self.edit_im, self.image_label2)
        else:
            messagebox.showerror("Error", "No image loaded.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageViewerApp(root)
    root.mainloop()
