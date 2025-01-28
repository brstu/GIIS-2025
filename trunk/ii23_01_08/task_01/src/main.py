import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import cv2
import numpy as np
from PIL import Image, ImageTk


class ImageProcessor:
    def __init__(self, root):
        self.root = root
        self.input_image = None
        self.current_display_image = None

        self.setup_ui()
    #кнопки
    def setup_ui(self):
        self.root.title("Image Processing")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")

        style = ttk.Style()
        style.configure("TButton", font=("Arial", 10), padding=8, relief="flat")
        style.configure("TFrame", background="#f0f0f0")
        style.map("TButton",
                  background=[("active", "#000000"), ("!active", "#000000")],
                  foreground=[("active", "black"), ("!active", "black")])

        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True)

        controls_frame = ttk.Frame(frame)
        controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)

        buttons = [
            ("Load Image", self.load_image),
            ("Save Image", self.save_image),
            ("Process Image", self.process_image),
            ("Remove Noise", self.remove_noise)
        ]

        for text, command in buttons:

            button = ttk.Button(controls_frame, text=text, command=command)
            button.pack(pady=10, fill=tk.X, padx=5)
            button.config(width=20)

        self.image_frame = ttk.Frame(frame, relief="sunken", borderwidth=2)
        self.image_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.image_label = tk.Label(self.image_frame, bg="white")
        self.image_label.pack(fill=tk.BOTH, expand=True)

    def show_error(self, message):
        messagebox.showerror("Error", message)
   #загрузка
    def load_image(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.input_image = cv2.imread(file_path)
            self.update_display(self.input_image)
   #сохранение
    def save_image(self):
        if self.current_display_image is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                       filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"),
                                                                   ("All files", "*.*")])
            if file_path:
                cv2.imwrite(file_path, self.current_display_image)

    def update_display(self, image):
        self.current_display_image = image
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        img_tk = ImageTk.PhotoImage(Image.fromarray(image_rgb))
        self.image_label.config(image=img_tk)
        self.image_label.image = img_tk
   #обработчик ДО
    def process_image(self):
        if self.input_image is not None:
            try:
                noise_level = simpledialog.askfloat("", "Enter noise level:", minvalue=0.0)
                if noise_level is None:
                    return

                filter_size = simpledialog.askinteger("", "Enter Threshold filter size:", minvalue=1)
                if filter_size is None or filter_size % 2 == 0:
                    self.show_error("Threshold filter size must be an odd number.")
                    return

                noisy_image = self.add_noise(self.input_image, noise_level)
                filtered_image = self.apply_Threshold(noisy_image, filter_size)  # Change here
                self.update_display(filtered_image)

            except Exception as e:
                self.show_error(str(e))
    #удаление шума
    def remove_noise(self):
        if self.input_image is not None:
            try:
                filter_size = simpledialog.askinteger("", "Enter Threshold filter size:", minvalue=1)
                if filter_size is None or filter_size % 2 == 0:
                    self.show_error("Threshold filter must be an odd number.")
                    return

                filtered_image = self.apply_Threshold(self.input_image, filter_size)
                self.update_display(filtered_image)

            except Exception as e:
                self.show_error(str(e))

    @staticmethod
    #добавление шума
    def add_noise(image, intensity):
        noisy_image = image.copy()
        height, width, _ = image.shape
        num_noise_points = int(intensity * width * height)

        for _ in range(num_noise_points):
            x, y = np.random.randint(0, width), np.random.randint(0, height)

            # Случайный выбор между черным и белым цветом для шума
            color = [255, 255, 255]
            noisy_image[y, x] = color

        return noisy_image

    @staticmethod
    #применение фильтра
    def apply_Threshold(image, filter_size):
        channels = cv2.split(image)
        filtered_channels = [cv2.medianBlur(channel, filter_size) for channel in channels]
        return cv2.merge(filtered_channels)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessor(root)
    root.mainloop()
