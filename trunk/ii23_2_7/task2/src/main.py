import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, filedialog, Label, Button, StringVar, OptionMenu, Canvas, PhotoImage
from PIL import Image, ImageTk


class IceCreamSupplyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Поставки мороженого - Санта Бремор")
        self.file_path = None
        self.data = None
        self.selected_ice_cream = StringVar(value="Выберите вид мороженого")
        # Меню выбора вида мороженого
        Label(root, text="Выберите вид мороженого:").pack()
        self.ice_cream_menu = OptionMenu(root, self.selected_ice_cream, "BL_plombir", "Gourmet_gauda", "Soletto_coffee",
                                         "TOP_kiwi", "YUKKI_Mishka")
        self.ice_cream_menu.pack()

        # Кнопка для отображения картинки
        Button(root, text="Показать картинку", command=self.display_image).pack()
        self.file_path = StringVar()
        self.chart_type = StringVar(value="Выберите тип графика")
        self.current_image = None

        Label(root, text="Выберите файл для загрузки:").pack()
        Button(root, text="Загрузить файл", command=self.load_file).pack()
        Label(root, text="Выберите тип визуализации:").pack()
        OptionMenu(root, self.chart_type, "Линейный график", "Гистограмма", "Диаграмма рассеяния",
                   "Круговая диаграмма").pack()
        Button(root, text="Построить график", command=self.plot_chart).pack()

        # Область для отображения изображения
        self.canvas = Canvas(root, width=300, height=300)
        self.canvas.pack()

        self.data = None

    def load_file(self):
        file_types = [("CSV Files", "*.csv"), ("Excel Files", "*.xlsx")]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        self.file_path.set(file_path)
        self.load_data(file_path)

    def load_data(self, file_path):
        if file_path.endswith(".csv"):
            self.data = pd.read_csv(file_path)
        elif file_path.endswith(".xlsx"):
            self.data = pd.read_excel(file_path, engine='openpyxl')
        print(self.data)

    def plot_chart(self):
        if self.data is None:
            print("Сначала загрузите данные.")
            return

        chart_type = self.chart_type.get()
        x = self.data.iloc[:, 0]
        y = self.data.iloc[:, 1]

        plt.figure(figsize=(8, 6))
        if chart_type == "Линейный график":
            plt.plot(x, y, marker='o')
        elif chart_type == "Гистограмма":
            plt.bar(x, y)
        elif chart_type == "Диаграмма рассеяния":
            plt.scatter(x, y)
        elif chart_type == "Круговая диаграмма":
            plt.pie(y, labels=x, autopct='%1.1f%%')

        plt.title("График: " + chart_type)
        plt.xlabel("Дата")
        plt.ylabel("Количество мороженого (кг)")
        plt.show()


    def display_image(self):
        ice_cream = self.selected_ice_cream.get()
        image_paths = {
            "BL_plombir": "C:\\Users\\Алла\\PycharmProjects\\PythonProject2\\BL_plombir_220.png",
            "Gourmet_gauda": "C:\\Users\\Алла\\PycharmProjects\\PythonProject2\\gourmet_gauda.png",
            "Soletto_coffee": "C:\\Users\\Алла\\PycharmProjects\\PythonProject2\\Soletto_rogue_coffee_hazelnut_75.png",
            "TOP_kiwi": "C:\\Users\\Алла\\PycharmProjects\\PythonProject2\\TOP_kiwi_70.png",
            "YUKKI_Mishka": "C:\\Users\\Алла\\PycharmProjects\\PythonProject2\\YUKKI_Mishka_belovezskiy.png"
        }

        if ice_cream in image_paths:
            try:
                image_path = image_paths[ice_cream]
                image = Image.open(image_path).resize((300, 300))
                photo = ImageTk.PhotoImage(image)
                self.canvas.create_image(0, 0, anchor="nw", image=photo)
                self.canvas.image = photo
            except Exception as e:
                print(f"Ошибка загрузки изображения: {e}")
        else:
            print("Пожалуйста, выберите вид мороженого.")

if __name__ == "__main__":
    root = Tk()
    app = IceCreamSupplyApp(root)
    root.mainloop()
