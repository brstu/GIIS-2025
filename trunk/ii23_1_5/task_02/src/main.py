import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from matplotlib import pyplot as plt


class DataVisualizerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Анализ Данных v1.2")
        self.master.geometry("1280x720")
        self.master.configure(bg="#1a1a1a")

        self.data_container = None
        self.current_visualization = None

        self.configure_styles()
        self.create_widgets()

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use("alt")
        style.configure("TFrame", background="#333333")
        style.configure("TLabel", background="#333333", foreground="#e6e6e6", font=("Helvetica", 12))
        style.map("C.TButton",
                  foreground=[('active', 'white'), ('!active', '#cccccc')],
                  background=[('active', '#4a766e'), ('!active', '#2d4a44')]
                  )
        style.configure("C.TButton", font=("Helvetica", 11), borderwidth=1)

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding=15)
        main_frame.pack(expand=True, fill=tk.BOTH)

        control_panel = ttk.Frame(main_frame)
        control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        buttons = [
            ("Импорт набора данных", self.import_dataset),
            ("Линейное отображение", self.setup_line_visual),
            ("Столбчатый анализ", self.prepare_bar_analysis),
            ("Точечное отображение", self.init_scatter_display),
            ("Секторная диаграмма", self.activate_pie_chart),
            ("Справка", self.show_instructions),
            ("Завершение работы", self.master.quit)
        ]

        for text, cmd in buttons:
            btn = ttk.Button(control_panel, text=text, style="C.TButton",
                             command=cmd, width=22)
            btn.pack(pady=4, ipady=6)

    def import_dataset(self):
        file_types = [("Табличные данные", "*.csv;*.xls*")]
        file_path = filedialog.askopenfilename(filetypes=file_types)
        if not file_path: return

        try:
            if file_path.endswith('.csv'):
                self.data_container = pd.read_csv(file_path)
            else:
                self.data_container = pd.read_excel(file_path)
            self.display_data_window()
        except Exception as e:
            messagebox.showerror("Ошибка чтения", f"Ошибка при обработке файла:\n{str(e)}")

    def display_data_window(self):
        data_win = tk.Toplevel(self.master)
        data_win.title("Просмотр данных")
        data_win.geometry("900x500")

        tree_scroll = ttk.Scrollbar(data_win)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        data_table = ttk.Treeview(data_win, yscrollcommand=tree_scroll.set)
        data_table.pack(expand=True, fill=tk.BOTH)
        tree_scroll.config(command=data_table.yview)

        data_table["columns"] = list(self.data_container.columns)
        for col in self.data_container.columns:
            data_table.heading(col, text=col)
            data_table.column(col, width=120, anchor=tk.W)

        for _, row in self.data_container.iterrows():
            data_table.insert("", tk.END, values=tuple(row))

    def column_selector(self, action, needs_single=False):
        if self.data_container is None:
            messagebox.showwarning("Данные не загружены", "Сначала импортируйте набор данных")
            return

        selector = tk.Toplevel(self.master)
        selector.title("Выбор параметров")
        selector.geometry("280x380")

        ttk.Label(selector, text="Выберите необходимые столбцы:").pack(pady=8)

        listbox = tk.Listbox(selector, selectmode=tk.SINGLE if needs_single else tk.EXTENDED,
                             bg="#404040", fg="white", font=("Consolas", 11))
        listbox.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        for col in self.data_container.columns:
            listbox.insert(tk.END, col)

        def process_selection():
            selected = [listbox.get(i) for i in listbox.curselection()]
            selector.destroy()
            if needs_single and len(selected) != 1:
                messagebox.showwarning("Неверный выбор", "Требуется выбор одного столбца")
                return
            action(selected[0] if needs_single else selected)

        ttk.Button(selector, text="Подтвердить", style="C.TButton",
                   command=process_selection).pack(pady=8)

    def setup_line_visual(self):
        def plot_action(cols):
            if len(cols) < 1: return
            self.data_container[cols].plot.line(title="Линейная диаграмма")
            plt.tight_layout()
            plt.show()

        self.column_selector(plot_action)

    def prepare_bar_analysis(self):
        def plot_action(cols):
            if len(cols) != 2:
                messagebox.showwarning("Ошибка выбора", "Требуется выбор двух столбцов")
                return

            categorical, numerical = cols
            if pd.api.types.is_numeric_dtype(self.data_container[numerical]):
                self.data_container.groupby(categorical)[numerical].sum().plot.bar(
                    title="Суммарные значения по категориям",
                    edgecolor='#2d4a44',
                    color='#4a766e'
                )
            else:
                pd.crosstab(self.data_container[categorical], self.data_container[numerical]).plot.bar(
                    stacked=True,
                    title="Комбинированное распределение"
                )
            plt.xlabel(categorical)
            plt.xticks(rotation=45)
            plt.show()

        self.column_selector(plot_action)

    def init_scatter_display(self):
        def plot_action(cols):
            if len(cols) < 2: return
            plt.figure(figsize=(8, 6))
            plt.scatter(
                self.data_container[cols[0]],
                self.data_container[cols[1]],
                c='#4a766e',
                alpha=0.7
            )
            plt.title("Диаграмма рассеивания")
            plt.xlabel(cols[0])
            plt.ylabel(cols[1])
            plt.grid(True, alpha=0.3)
            plt.show()

        self.column_selector(plot_action)

    def activate_pie_chart(self):
        def plot_action(col):
            counts = self.data_container[col].value_counts()
            plt.pie(
                counts,
                labels=counts.index,
                autopct='%1.1f%%',
                startangle=90,
                colors=plt.cm.Paired.colors
            )
            plt.title(f"Распределение по '{col}'")
            plt.show()

        self.column_selector(plot_action, needs_single=True)

    def show_instructions(self):
        help_text = """
        Руководство пользователя:
        1. Используйте кнопку импорта для загрузки CSV/XLSX файлов
        2. Выберите тип визуализации из доступных вариантов
        3. Для построения графиков следуйте инструкциям выбора данных
        4. Анализируйте полученные визуализации
        """
        messagebox.showinfo("Справочная информация", help_text)


if __name__ == "__main__":
    root = tk.Tk()
    app = DataVisualizerApp(root)
    root.mainloop()