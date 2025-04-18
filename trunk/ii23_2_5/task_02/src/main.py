import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from sklearn.preprocessing import MinMaxScaler
from ttkbootstrap import Style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class ToolTip:

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, _, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + cy + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="#ffffe0", relief="solid", borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=5, ipady=3)

    def hide_tip(self, event=None):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

class DataVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Интерактивный визуализатор данных")
        self.root.geometry("1200x800")
        self.style = Style(theme='darkly')
        self.root.configure(bg=self.style.colors.bg)
        self.data = None
        self.canvas = None

        title = ttk.Label(root, text="Интерактивная визуализация", font=("Segoe UI", 18, "bold"))
        title.pack(pady=(20, 10))

        top_frame = ttk.Frame(root)
        top_frame.pack(pady=10)

        self.load_button = ttk.Button(top_frame, text="Загрузить файл", command=self.load_file)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.chart_type = tk.StringVar()
        self.chart_dropdown = ttk.Combobox(top_frame, textvariable=self.chart_type, state="readonly")
        self.chart_dropdown['values'] = ['Линейный график', 'Гистограмма', 'Диаграмма рассеяния', 'Круговая диаграмма']
        self.chart_dropdown.set('Линейный график')
        self.chart_dropdown.pack(side=tk.LEFT, padx=5)

        self.plot_button = ttk.Button(top_frame, text="Построить график", command=self.plot_chart)
        self.plot_button.pack(side=tk.LEFT, padx=5)

        self.save_button = ttk.Button(top_frame, text="Сохранить график", command=self.save_chart)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.export_pdf_button = ttk.Button(top_frame, text="Сохранить как PDF", command=self.save_as_pdf)
        self.export_pdf_button.pack(side=tk.LEFT, padx=5)
        ToolTip(self.export_pdf_button, "Сохранить график в формате PDF")

        self.help_button = ttk.Button(top_frame, text="ℹ️ Подсказка", command=self.show_help)
        self.help_button.pack(side=tk.LEFT, padx=5)

        # Панель осей
        axis_frame = ttk.Frame(root)
        axis_frame.pack(pady=5)

        ttk.Label(axis_frame, text="X:").pack(side=tk.LEFT)
        self.x_column = tk.StringVar()
        self.x_dropdown = ttk.Combobox(axis_frame, textvariable=self.x_column, width=20)
        self.x_dropdown.pack(side=tk.LEFT, padx=5)

        ttk.Label(axis_frame, text="Y:").pack(side=tk.LEFT)
        self.y_column = tk.StringVar()
        self.y_dropdown = ttk.Combobox(axis_frame, textvariable=self.y_column, width=20)
        self.y_dropdown.pack(side=tk.LEFT, padx=5)

        ttk.Label(axis_frame, text="Группировать по:").pack(side=tk.LEFT, padx=10)
        self.group_column = tk.StringVar()
        self.group_dropdown = ttk.Combobox(axis_frame, textvariable=self.group_column, width=20)
        self.group_dropdown.pack(side=tk.LEFT)

        # Кнопки обработки данных
        process_frame = ttk.Frame(root)
        process_frame.pack(pady=5)

        self.clean_button = ttk.Button(process_frame, text="Очистить пропущенные значения", command=self.clean_data)
        self.clean_button.pack(side=tk.LEFT, padx=5)

        self.normalize_button = ttk.Button(process_frame, text="Нормализовать данные", command=self.normalize_data)
        self.normalize_button.pack(side=tk.LEFT, padx=5)

        self.group_button = ttk.Button(process_frame, text="Группировать и усреднить", command=self.group_and_aggregate)

        self.group_button.pack(side=tk.LEFT, padx=5)

        # Таблица
        self.table_frame = ttk.LabelFrame(root, text="Таблица данных")
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.tree = None

        # Область графика
        self.chart_frame = ttk.LabelFrame(root, text="График")
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        ToolTip(self.load_button, "Загрузить CSV или Excel файл с данными")
        ToolTip(self.chart_dropdown, "Выберите тип графика для отображения")
        ToolTip(self.plot_button, "Построить график по выбранным столбцам")
        ToolTip(self.x_dropdown, "Выберите столбец для оси X")
        ToolTip(self.y_dropdown, "Выберите столбец для оси Y")
        ToolTip(self.save_button, "Сохранить график как PNG")
        #ToolTip(self.export_pdf_button, "Сохранить график как PDF")
        ToolTip(self.clean_button, "Удалить строки с пропущенными значениями")
        ToolTip(self.normalize_button, "Привести числовые данные к шкале от 0 до 1")
        ToolTip(self.group_button, "Сгруппировать по столбцу X и посчитать среднее для остальных")


        self.group_button = ttk.Button(process_frame, text="Группировать и агрегировать",
                                       command=self.group_and_aggregate)
        ttk.Label(process_frame, text="Функция агрегирования:").pack(side=tk.LEFT, padx=(20, 5))

        self.agg_function = tk.StringVar()
        self.agg_dropdown = ttk.Combobox(process_frame, textvariable=self.agg_function, state='readonly', width=10)
        self.agg_dropdown['values'] = ['Среднее', 'Сумма']
        self.agg_dropdown.current(0)
        self.agg_dropdown.pack(side=tk.LEFT, padx=5)

        ToolTip(self.agg_dropdown, "Выберите метод агрегирования для группировки")

        self.group_button.pack(side=tk.LEFT, padx=5)
        ToolTip(self.group_button, "Группировать по X и применить выбранную функцию к Y")

    def load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV файлы", "*.csv"), ("Excel файлы", "*.xlsx *.xls")]
        )
        if file_path:
            try:
                if file_path.endswith(".csv"):
                    self.data = pd.read_csv(file_path, encoding='utf-8-sig')
                else:
                    self.data = pd.read_excel(file_path)
                self.show_data_in_table()
                self.update_column_options()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")

    def update_column_options(self):
        if self.data is not None:
            cols = list(self.data.columns)

            # Категориальные и числовые столбцы
            cat_cols = self.data.select_dtypes(include='object').columns.tolist()
            num_cols = self.data.select_dtypes(include='number').columns.tolist()

            self.x_dropdown['values'] = cat_cols
            self.y_dropdown['values'] = num_cols
            self.group_dropdown['values'] = cat_cols

            if cat_cols:
                self.x_column.set(cat_cols[0])
                self.group_column.set(cat_cols[0])
            if num_cols:
                self.y_column.set(num_cols[0])

    def show_data_in_table(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        self.tree = ttk.Treeview(self.table_frame, show='headings')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree["columns"] = list(self.data.columns)
        for col in self.data.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

        for _, row in self.data.iterrows():
            self.tree.insert("", tk.END, values=list(row))

    def clean_data(self):
        if self.data is not None:
            self.data.dropna(inplace=True)
            self.show_data_in_table()
            messagebox.showinfo("Готово", "Пропущенные значения удалены.")

    def normalize_data(self):
        if self.data is not None:
            num_cols = self.data.select_dtypes(include='number').columns
            if not num_cols.empty:
                scaler = MinMaxScaler()
                self.data[num_cols] = scaler.fit_transform(self.data[num_cols])
                self.show_data_in_table()
                messagebox.showinfo("Готово", "Числовые данные нормализованы.")

    def group_and_aggregate(self):
        if self.data is None:
            messagebox.showwarning("Внимание", "Сначала загрузите данные.")
            return

        x = self.x_column.get()
        y = self.y_column.get()
        func = self.agg_function.get()

        if not x or not y:
            messagebox.showwarning("Внимание", "Выберите столбцы для осей X и Y.")
            return

        try:
            if func == "Среднее":
                grouped = self.data.groupby(x)[y].mean().reset_index()
            elif func == "Сумма":
                grouped = self.data.groupby(x)[y].sum().reset_index()
            elif func == "Максимум":
                grouped = self.data.groupby(x)[y].max().reset_index()
            elif func == "Минимум":
                grouped = self.data.groupby(x)[y].min().reset_index()
            else:
                messagebox.showerror("Ошибка", "Неизвестная функция агрегирования.")
                return

            self.data = grouped
            self.show_data_in_table()
            self.update_column_options()

            messagebox.showinfo("Готово", f"Данные сгруппированы по '{x}' с использованием '{func.lower()}'.")
        except Exception as e:
            messagebox.showerror("Ошибка при группировке", str(e))

    def plot_chart(self):
        if self.data is None:
            messagebox.showwarning("Внимание", "Сначала загрузите данные.")
            return

        chart_type = self.chart_type.get()
        x = self.x_column.get()
        y = self.y_column.get()

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(6, 4))

        try:
            if chart_type == 'Линейный график':
                self.data.plot(x=x, y=y, kind='line', ax=ax)
            elif chart_type == 'Гистограмма':
                self.data[y].plot(kind='hist', ax=ax)
            elif chart_type == 'Диаграмма рассеяния':
                self.data.plot(kind='scatter', x=x, y=y, ax=ax)
            elif chart_type == 'Круговая диаграмма':
                if self.data[y].dtype in ['int64', 'float64']:
                    self.data.groupby(x)[y].mean().plot.pie(autopct='%1.1f%%', ax=ax)
                else:
                    messagebox.showerror("Ошибка",
                                         "Для круговой диаграммы нужен числовой столбец Y и категориальный X.")
                    return

            ax.set_xlabel(x)
            ax.set_ylabel(y)
            ax.set_title(f"{chart_type}: {y} по {x}")

            self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            toolbar = NavigationToolbar2Tk(self.canvas, self.chart_frame)
            toolbar.update()
            toolbar.pack(side=tk.BOTTOM, fill=tk.X)


        except Exception as e:
            messagebox.showerror("Ошибка при построении графика", str(e))

    def save_chart(self):
        if self.canvas:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("PDF", "*.pdf")]
            )
            if file_path:
                self.canvas.figure.savefig(file_path)
                messagebox.showinfo("Готово", "График сохранён успешно!")

    def show_help(self):
        messagebox.showinfo("Подсказка",
            "1. Загрузите CSV или Excel файл\n"
            "2. Выберите нужные оси X и Y\n"
            "3. Выберите тип графика\n"
            "4. Можно очистить или нормализовать данные\n"
            "5. График можно сохранить или увеличить через панель под ним"
        )

    def save_as_pdf(self):
        if self.canvas is None:
            messagebox.showwarning("Внимание", "Сначала постройте график.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if file_path:
            try:
                # Создаем PDF и сохраняем график
                with PdfPages(file_path) as pdf:
                    fig = self.canvas.figure
                    pdf.savefig(fig)
                messagebox.showinfo("Успех", f"График успешно сохранён как PDF:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить PDF:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = DataVisualizerApp(root)
    root.mainloop()