import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class VisualizerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Анализатор данных")
        self.master.configure(bg="#e0e0e0")  # Основной цвет окна — светло-серый

        # Настройка стиля ttk
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TLabel", background="#e0e0e0")
        style.configure("TButton", background="#dcdcdc", foreground="black")
        style.configure("TCombobox", fieldbackground="white", background="#f0f0f0")

        self.dataset = None

        # Меню
        self.menu = tk.Menu(master)

        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="Открыть файл", command=self.open_file)
        file_menu.add_command(label="Сохранить график", command=self.save_figure)
        file_menu.add_command(label="Выход", command=master.quit)
        self.menu.add_cascade(label="Файл", menu=file_menu)

        graph_menu = tk.Menu(self.menu, tearoff=0)
        graph_menu.add_command(label="Линейный график", command=self.draw_line_chart)
        graph_menu.add_command(label="Гистограмма", command=self.draw_histogram)
        graph_menu.add_command(label="Диаграмма рассеяния", command=self.draw_scatter_plot)
        graph_menu.add_command(label="Круговая диаграмма", command=self.draw_pie_chart)
        graph_menu.add_command(label="Boxplot", command=self.draw_box_plot)
        self.menu.add_cascade(label="Графики", menu=graph_menu)

        self.menu.add_command(label="Справка", command=self.display_help)
        self.master.config(menu=self.menu)

        # Область графика
        self.figure = plt.Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=master)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Таблица данных
        self.text_output = tk.Text(master, height=10, bg="#f9f9f9", fg="black")
        self.text_output.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

    def choose_two_columns(self, title, message):
        if self.dataset is not None:
            dialog = tk.Toplevel(self.master)
            dialog.title(title)
            dialog.geometry("300x150")
            dialog.configure(bg="#d3d3d3")

            ttk.Label(dialog, text=message).pack(pady=5)

            x_var = tk.StringVar()
            y_var = tk.StringVar()

            ttk.Label(dialog, text="Ось X:").pack(pady=5)
            x_box = ttk.Combobox(dialog, textvariable=x_var, values=self.dataset.columns.tolist())
            x_box.pack(pady=5)

            ttk.Label(dialog, text="Ось Y:").pack(pady=5)
            y_box = ttk.Combobox(dialog, textvariable=y_var, values=self.dataset.columns.tolist())
            y_box.pack(pady=5)

            def confirm():
                dialog.destroy()

            ttk.Button(dialog, text="OK", command=confirm).pack(pady=5)
            dialog.wait_window()
            return x_var.get(), y_var.get()
        else:
            messagebox.showwarning("Ошибка", "Сначала загрузите данные.")
            return None, None

    def draw_line_chart(self):
        y_col = self.choose_column("Линейный график", "Выберите числовой столбец", only_numeric=True)
        if y_col:
            self.figure.clear()
            axis = self.figure.add_subplot(111)
            axis.plot(self.dataset[y_col])
            axis.set_title(f"Линейный график: {y_col}")
            axis.set_ylabel(y_col)
            axis.set_xlabel("Индекс")
            self.canvas.draw()

    def draw_histogram(self):
        col = self.choose_column("Гистограмма", "Выберите числовой столбец", only_numeric=True)
        if col:
            self.figure.clear()
            axis = self.figure.add_subplot(111)
            axis.hist(self.dataset[col], bins=10)
            axis.set_title(f"Гистограмма: {col}")
            axis.set_xlabel(col)
            axis.set_ylabel("Частота")
            self.canvas.draw()

    def draw_scatter_plot(self):
        x_col, y_col = self.choose_two_columns("Диаграмма рассеяния", "Выберите столбцы X и Y")
        if x_col and y_col:
            self.figure.clear()
            axis = self.figure.add_subplot(111)
            axis.scatter(self.dataset[x_col], self.dataset[y_col])
            axis.set_title(f"{x_col} vs {y_col}")
            axis.set_xlabel(x_col)
            axis.set_ylabel(y_col)
            self.canvas.draw()

    def draw_pie_chart(self):
        col = self.choose_column("Круговая диаграмма", "Выберите числовой столбец", only_numeric=True)
        if col:
            self.figure.clear()
            axis = self.figure.add_subplot(111)
            axis.pie(self.dataset[col], labels=self.dataset.index, autopct='%1.1f%%')
            axis.set_title(f"Круговая диаграмма: {col}")
            self.canvas.draw()

    def draw_box_plot(self):
        col = self.choose_column("Boxplot", "Выберите числовой столбец", only_numeric=True)
        if col:
            self.figure.clear()
            axis = self.figure.add_subplot(111)
            axis.boxplot(self.dataset[col])
            axis.set_title(f"Boxplot: {col}")
            axis.set_xlabel(col)
            self.canvas.draw()

    def save_figure(self):
        if self.figure:
            save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("PDF", "*.pdf")])
            if save_path:
                self.figure.savefig(save_path)
                messagebox.showinfo("Успешно", f"График сохранён: {save_path}")

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv"), ("Excel", "*.xlsx")])
        if path:
            try:
                self.dataset = pd.read_csv(path) if path.endswith('.csv') else pd.read_excel(path)
                self.display_data()
            except Exception as error:
                messagebox.showerror("Ошибка", f"Ошибка при загрузке: {error}")

    def display_data(self):
        self.text_output.delete(1.0, tk.END)
        self.text_output.insert(tk.END, self.dataset.to_string())

    def choose_column(self, title, message, only_numeric=False):
        if self.dataset is not None:
            dialog = tk.Toplevel(self.master)
            dialog.title(title)
            dialog.geometry("300x100")
            dialog.configure(bg="#d3d3d3")

            ttk.Label(dialog, text=message).pack(pady=5)

            column_choice = tk.StringVar()
            columns = self.dataset.select_dtypes(include='number').columns.tolist() if only_numeric else self.dataset.columns.tolist()

            if not columns:
                messagebox.showwarning("Ошибка", "Нет подходящих столбцов.")
                return None

            combobox = ttk.Combobox(dialog, textvariable=column_choice, values=columns)
            combobox.pack(pady=5)

            selected = None

            def confirm():
                nonlocal selected
                selected = column_choice.get()
                dialog.destroy()

            ttk.Button(dialog, text="OK", command=confirm).pack(pady=5)
            dialog.wait_window()
            return selected
        else:
            messagebox.showwarning("Ошибка", "Сначала загрузите данные.")
            return None

    def display_help(self):
        help_msg = """
        Инструкция:
        1. Загрузите CSV или Excel файл.
        2. Выберите тип графика из меню.
        3. Укажите нужные столбцы.
        4. Сохраните график при необходимости.

        Примечания:
        - Для круговых диаграмм, гистограмм и boxplot используйте числовые столбцы.
        - Линейный график строится по одной колонке (ось Y).
        - Диаграмма рассеяния требует две колонки: X и Y.
        """
        messagebox.showinfo("Справка", help_msg)


if __name__ == "__main__":
    root_window = tk.Tk()
    app = VisualizerApp(root_window)
    root_window.mainloop()
