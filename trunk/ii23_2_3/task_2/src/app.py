import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from tkinter import ttk
import datavisualization as mydv


class DataFrameViewer(tk.Tk):
    def __init__(self):
        super().__init__()

        self.attributes('-fullscreen', True)
        self.bind("<Escape>", self.exit_program)

        self.title("Просмотр таблицы Pandas")

        self.menu = tk.Menu(self)
        self.config(menu=self.menu)

        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="Загрузка CSV", command=self.load_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Очистить данные", command=self.clean_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_program)
        self.menu.add_cascade(label="File", menu=file_menu)

        visualisation_menu = tk.Menu(self.menu, tearoff=0)
        visualisation_menu.add_command(label="График", command=self.make_linear_graph)
        visualisation_menu.add_command(label="Круговая диаграмма", command=self.make_circle_diagram)
        visualisation_menu.add_command(label="Диаграмма рассеивания", command=self.make_scatter_diagram)
        visualisation_menu.add_command(label="Гистограмма", command=self.make_hist)
        self.menu.add_cascade(label="Visualisation", menu=visualisation_menu)

        info_menu = tk.Menu(self.menu, tearoff=0)
        info_menu.add_command(label="Show Info", command=self.show_inf)
        self.menu.add_cascade(label="Info", menu=info_menu)

        self.frame = tk.Frame(self)
        self.frame.pack(expand=True, fill='both')

        self.tree = ttk.Treeview(self.frame, show='headings')
        self.tree.pack(expand=True, fill='both')

        self.separator = tk.Frame(self, height=self.winfo_height() // 2)
        self.separator.pack(fill='x')

        self.is_loaded = False
        self.df = None

    def clean_csv(self):
        if self.is_loaded:
            self.df.dropna(inplace=True)
            print("Строки с пустыми значениями были удалены.")
        else:
            print("Ошибка: Данные не загружены.")

    def make_scatter_diagram(self):
        if self.is_loaded:
            graph_window = tk.Toplevel(self)
            graph_window.title("Выбор колонок для графика")

            ttk.Label(graph_window, text="Выберите ось X:").grid(column=0, row=0, padx=10, pady=10)
            x_column = ttk.Combobox(graph_window, values=self.df.columns.tolist())
            x_column.grid(column=1, row=0, padx=10, pady=10)

            ttk.Label(graph_window, text="Выберите ось Y:").grid(column=0, row=1, padx=10, pady=10)
            y_column = ttk.Combobox(graph_window, values=self.df.columns.tolist())
            y_column.grid(column=1, row=1, padx=10, pady=10)

            ttk.Button(graph_window, text="Построить график",
                       command=lambda: self.plot_graph_scatter(x_column.get(), y_column.get())).grid(column=0, row=2,columnspan=2, pady=10)

    def plot_graph_scatter(self, x_col, y_col):
        if x_col and y_col:
            x_data = self.df[x_col]
            y_data = self.df[y_col]

            if pd.api.types.is_numeric_dtype(x_data) and pd.api.types.is_numeric_dtype(y_data):
                mydv.make_scatter_diagram(x_data, y_data, x_col, y_col)
            else:
                messagebox.showwarning("Предупреждение", "Обе колонки должны содержать числовые значения.")
        else:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите обе колонки.")

    def make_circle_diagram(self):
        if self.is_loaded:
            graph_window = tk.Toplevel(self)
            graph_window.title("Выбор колонку для графика")

            ttk.Label(graph_window, text="Выберите:").grid(column=0, row=0, padx=10, pady=10)
            x_column = ttk.Combobox(graph_window, values=self.df.columns.tolist())
            x_column.grid(column=1, row=0, padx=10, pady=10)

            ttk.Button(graph_window, text="Построить график",
                       command=lambda: self.plot_graph_pie(x_column.get())).grid(column=0, row=2, columnspan=2,pady=10)

    def plot_graph_pie(self, x_col):
        if x_col:
            x_data = self.df[x_col]

            mydv.make_circle_diagram(x_data, x_col)
        else:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите колонку.")

    def make_linear_graph(self):
        if self.is_loaded:
            graph_window = tk.Toplevel(self)
            graph_window.title("Выбор колонку для графика")

            ttk.Label(graph_window, text="Выберите:").grid(column=0, row=0, padx=10, pady=10)
            x_column = ttk.Combobox(graph_window, values=self.df.columns.tolist())
            x_column.grid(column=1, row=0, padx=10, pady=10)

            ttk.Button(graph_window, text="Построить график",
                       command=lambda: self.plot_graph_linear(x_column.get())).grid(column=0, row=2,columnspan=2,pady=10)

    def plot_graph_linear(self, x_col):
        if x_col:
            x_data = self.df[x_col]

            if pd.api.types.is_numeric_dtype(x_data):
                mydv.make_linear_graph(x_data, x_col)
            else:
                messagebox.showwarning("Предупреждение", "Колонки должны содержать числовые значения.")
        else:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите колонку.")

    def make_hist(self):
        if self.is_loaded:
            graph_window = tk.Toplevel(self)
            graph_window.title("Выбор колонку для графика")

            ttk.Label(graph_window, text="Выберите:").grid(column=0, row=0, padx=10, pady=10)
            x_column = ttk.Combobox(graph_window, values=self.df.columns.tolist())
            x_column.grid(column=1, row=0, padx=10, pady=10)

            ttk.Button(graph_window, text="Построить график",
                       command=lambda: self.plot_graph_hist(x_column.get())).grid(column=0, row=2, columnspan=2, pady=10)

    def plot_graph_hist(self, x_col):
        if x_col:
            x_data = self.df[x_col]

            mydv.make_hist(x_data, x_col)
        else:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите колонку.")

    def show_inf(self):
        messagebox.showinfo("Подсказка", "Вроде как все интуитивно понятно\n"
                                         "*Вкладка File: загрузка данных, очистка от пустых полей, выход\n"
                                         "*Вклдака Visualization:ОБЯЗАТЕЛЬНО СНАЧАЛА ЗАГРУЗИТЬ CSV\n разные виды графиков, в некоторых надо чтоб были числовые значения")

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                self.df = pd.read_csv(file_path)
                self.is_loaded = True
                self.display_dataframe(self.df)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")

    def display_dataframe(self, df):
        self.tree.delete(*self.tree.get_children())

        self.tree["columns"] = list(df)

        for column in df:
            self.tree.heading(column, text=column)
            self.tree.column(column, anchor="center")

        for index, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))

        self.adjust_column_widths()

    def adjust_column_widths(self):
        total_width = self.winfo_width()
        num_columns = len(self.tree["columns"])
        if num_columns > 0:
            column_width = total_width // num_columns
            for column in self.tree["columns"]:
                self.tree.column(column, width=column_width)

    def exit_program(self, event=None):
        self.quit()