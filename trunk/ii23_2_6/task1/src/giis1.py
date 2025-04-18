import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QLabel, QWidget, QPushButton, QFileDialog, QGridLayout, QSlider, QMessageBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt


class ImageFilterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.file_name = None
        self.noise_level = 10  # Уровень шума
        self.threshold = 20  # Порог фильтрации
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Image Noise Filter')
        self.setFixedSize(800, 600)

        self.image_label1 = QLabel(self)
        self.image_label2 = QLabel(self)

        self.load_button = QPushButton('Load Image', self)
        self.load_button.clicked.connect(self.load_image)

        self.noise_slider = QSlider(Qt.Horizontal, self)
        self.noise_slider.setRange(1, 50)
        self.noise_slider.setValue(self.noise_level)
        self.noise_slider.valueChanged.connect(self.update_noise_level)

        self.noise_button = QPushButton('Add Noise', self)
        self.noise_button.clicked.connect(self.add_noise)

        self.threshold_slider = QSlider(Qt.Horizontal, self)
        self.threshold_slider.setRange(1, 50)
        self.threshold_slider.setValue(self.threshold)
        self.threshold_slider.valueChanged.connect(self.update_threshold)

        self.filter_button = QPushButton('Apply Filter', self)
        self.filter_button.clicked.connect(self.apply_filter)

        layout = QGridLayout(self)
        layout.addWidget(self.load_button, 0, 0)
        layout.addWidget(self.image_label1, 1, 0)
        layout.addWidget(self.image_label2, 1, 1)
        layout.addWidget(self.noise_slider, 2, 0)
        layout.addWidget(self.noise_button, 2, 1)
        layout.addWidget(self.threshold_slider, 3, 0)
        layout.addWidget(self.filter_button, 3, 1)
        self.setLayout(layout)

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open Image', '', 'Image Files (*.png *.jpg *.jpeg)')
        if file_name:
            self.file_name = file_name
            pixmap = QPixmap(file_name)
            self.image_label1.setPixmap(pixmap)
            self.image_label2.setPixmap(pixmap)

    def update_noise_level(self, value):
        self.noise_level = value

    def update_threshold(self, value):
        self.threshold = value

    def add_noise(self):
        if self.file_name:
            image = cv2.imread(self.file_name, cv2.IMREAD_COLOR)
            height, width, _ = image.shape
            num_pixels = (height * width * self.noise_level) // 100

            # Добавление точек (импульсного шума)
            for _ in range(num_pixels):
                x, y = np.random.randint(0, width), np.random.randint(0, height)
                color = (0, 0, 0) if np.random.rand() < 0.5 else (255, 255, 255)
                image[y, x] = color

            # Добавление случайных линий
            for _ in range(self.noise_level // 5):
                x1, y1 = np.random.randint(0, width), np.random.randint(0, height)
                x2, y2 = np.random.randint(0, width), np.random.randint(0, height)
                color = (0, 0, 0) if np.random.rand() < 0.5 else (255, 255, 255)
                cv2.line(image, (x1, y1), (x2, y2), color, 1)

            self.noisy_image = image.copy()
            self.display_image(image, self.image_label2)
        else:
            QMessageBox.warning(self, 'Error', 'Load an image first!')

    def apply_filter(self):
        if hasattr(self, 'noisy_image'):
            filtered_image = cv2.medianBlur(self.noisy_image, 3)  # 3x3 окно
            self.display_image(filtered_image, self.image_label2)
        else:
            QMessageBox.warning(self, 'Error', 'Add noise first!')

    def display_image(self, image, label):
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_img = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        label.setPixmap(QPixmap.fromImage(q_img))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageFilterApp()
    ex.show()
    sys.exit(app.exec_())
