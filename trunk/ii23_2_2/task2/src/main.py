import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt

class DataAnalysisApp:
    def __init__(self, parent):
        self.parent = parent
        self.parent.title("Анализатор данных v2.0")
        self.parent.geometry("1280x720")
        self.parent.configure(bg="#202020")
        
        self.dataset = None
        self.current_chart = None

        self.setup_styles()
        self.build_interface()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#404040")
        style.configure("TLabel", background="#404040", foreground="#f0f0f0", font=("Arial", 12))
        style.configure("C.TButton", font=("Arial", 11), borderwidth=1, background="#3b6b58", foreground="#ffffff")

    def build_interface(self):
        container = ttk.Frame(self.parent, padding=15)
        container.pack(expand=True, fill=tk.BOTH)

        panel = ttk.Frame(container)
        panel.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        options = [
            ("Загрузить данные", self.load_data),
            ("График тренда", self.create_line_chart),
            ("Гистограмма", self.generate_bar_chart),
            ("Диаграмма рассеивания", self.scatter_chart),
            ("Круговая диаграмма", self.pie_chart),
            ("Помощь", self.display_help),
            ("Выход", self.parent.quit)
        ]

        for label, action in options:
            btn = ttk.Button(panel, text=label, style="C.TButton", command=action, width=22)
            btn.pack(pady=4, ipady=6)

    def load_data(self):
        filetypes = [("Файлы данных", "*.csv;*.xls*")]
        path = filedialog.askopenfilename(filetypes=filetypes)
        if not path:
            return

        try:
            self.dataset = pd.read_csv(path) if path.endswith('.csv') else pd.read_excel(path)
            self.show_data_preview()
        except Exception as err:
            messagebox.showerror("Ошибка загрузки", f"Ошибка обработки файла:\n{str(err)}")

    def show_data_preview(self):
        preview = tk.Toplevel(self.parent)
        preview.title("Просмотр данных")
        preview.geometry("900x500")

        scrollbar = ttk.Scrollbar(preview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        table = ttk.Treeview(preview, yscrollcommand=scrollbar.set)
        table.pack(expand=True, fill=tk.BOTH)
        scrollbar.config(command=table.yview)

        table["columns"] = list(self.dataset.columns)
        for column in self.dataset.columns:
            table.heading(column, text=column)
            table.column(column, width=120, anchor=tk.W)

        for _, row in self.dataset.iterrows():
            table.insert("", tk.END, values=tuple(row))

    def select_columns(self, callback, single=False):
        if self.dataset is None:
            messagebox.showwarning("Данные отсутствуют", "Сначала загрузите набор данных")
            return

        selection_window = tk.Toplevel(self.parent)
        selection_window.title("Выберите столбцы")
        selection_window.geometry("300x400")

        ttk.Label(selection_window, text="Выберите столбцы:").pack(pady=8)

        listbox = tk.Listbox(selection_window, selectmode=tk.SINGLE if single else tk.EXTENDED, bg="#505050", fg="white")
        listbox.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        
        for col in self.dataset.columns:
            listbox.insert(tk.END, col)

        def confirm():
            selected = [listbox.get(i) for i in listbox.curselection()]
            selection_window.destroy()
            if single and len(selected) != 1:
                messagebox.showwarning("Ошибка", "Выберите один столбец")
                return
            callback(selected[0] if single else selected)

        ttk.Button(selection_window, text="Выбрать", style="C.TButton", command=confirm).pack(pady=8)

    def create_line_chart(self):
        def plot(cols):
            if cols:
                self.dataset[cols].plot.line(title="График тренда")
                plt.show()
        self.select_columns(plot)

    def generate_bar_chart(self):
        def plot(cols):
            if len(cols) != 2:
                messagebox.showwarning("Ошибка", "Выберите два столбца")
                return
            self.dataset.groupby(cols[0])[cols[1]].sum().plot.bar(title="Гистограмма")
            plt.show()
        self.select_columns(plot)

    def scatter_chart(self):
        def plot(cols):
            if len(cols) < 2:
                return
            plt.scatter(self.dataset[cols[0]], self.dataset[cols[1]], c='#3b6b58', alpha=0.7)
            plt.title("Диаграмма рассеивания")
            plt.xlabel(cols[0])
            plt.ylabel(cols[1])
            plt.grid(True, alpha=0.3)
            plt.show()
        self.select_columns(plot)

    def pie_chart(self):
        def plot(col):
            counts = self.dataset[col].value_counts()
            plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90)
            plt.title(f"Распределение: {col}")
            plt.show()
        self.select_columns(plot, single=True)

    def display_help(self):
        messagebox.showinfo("Помощь", "1. Загрузите CSV/XLSX\n2. Выберите визуализацию\n3. Выберите нужные столбцы\n4. Анализируйте!")

if __name__ == "__main__":
    root = tk.Tk()
    app = DataAnalysisApp(root)
    root.mainloop()
