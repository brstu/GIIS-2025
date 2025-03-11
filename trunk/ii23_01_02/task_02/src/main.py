import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt

root = tk.Tk()
root.title("Интерактивный визуализатор данных")
root.geometry("1280x720")
root.configure(bg="#1e1e1e")

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "TButton",
    background="#4CAF50",
    foreground="white",
    font=("Arial", 12, "bold"),
    padding=10,
)
style.map(
    "TButton",
    background=[("active", "#FF5722")],
    foreground=[("active", "white")]
)

root.configure(bg="#3E4E5E")

style.configure("TFrame", background="#3E4E5E")
style.configure("TLabel", background="#3E4E5E", foreground="white", font=("Arial", 14))



frame = ttk.Frame(root, padding=20)
frame.pack(expand=True, fill="both")

title_label = ttk.Label(frame, text="Меню", font=("Arial", 16, "bold"))
title_label.pack(pady=10)

df = None


def load_data():
    global df
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx;*.xls")])
    if not file_path:
        return
    try:
        df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
        display_data(df)
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")


def display_data(df):
    data_window = tk.Toplevel(root)
    data_window.title("Таблица данных")
    data_window.geometry("900x600")

    frame_table = ttk.Frame(data_window, padding=10)
    frame_table.pack(expand=True, fill="both")

    tree = ttk.Treeview(frame_table, columns=list(df.columns), show="headings")

    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=150, anchor="center")

    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))

    tree.pack(expand=True, fill="both")


def select_columns(callback, single=False):
    if df is None:
        messagebox.showwarning("Предупреждение", "Сначала загрузите данные!")
        return

    def on_select():
        selected = listbox.curselection()
        columns = [listbox.get(i) for i in selected]
        top.destroy()
        if single:
            callback(columns[0])
        else:
            callback(columns)

    top = tk.Toplevel(root)
    top.title("Выбор столбцов")
    top.geometry("300x300")

    label = ttk.Label(top, text="Выберите столбцы:")
    label.pack(pady=5)

    listbox = tk.Listbox(top, selectmode=tk.SINGLE if single else tk.MULTIPLE, bg="#333", fg="white")
    for col in df.columns:
        listbox.insert(tk.END, col)
    listbox.pack(expand=True, fill="both", pady=5)

    button = ttk.Button(top, text="Выбрать", command=on_select)
    button.pack(pady=5)


def plot_line_chart():
    def callback(columns):
        df[columns].plot(kind='line', figsize=(8, 5))
        plt.title("Линейный график")
        plt.grid(True)
        plt.show()

    select_columns(callback)


def plot_histogram():
    def callback(columns):
        if len(columns) != 2:
            messagebox.showwarning("Предупреждение", "Выберите два столбца!")
            return
        df.groupby(columns[0])[columns[1]].sum().plot(kind='bar', figsize=(8, 5), alpha=0.7, edgecolor='black')
        plt.title("Гистограмма")
        plt.xlabel(columns[0])
        plt.grid(True)
        plt.show()

    select_columns(callback)


def plot_scatter():
    def callback(columns):
        if len(columns) < 2:
            messagebox.showwarning("Предупреждение", "Выберите два столбца!")
            return
        df.plot(kind='scatter', x=columns[0], y=columns[1], figsize=(8, 5))
        plt.title("Диаграмма рассеяния")
        plt.grid(True)
        plt.show()

    select_columns(callback)


def plot_pie_chart():
    def callback(column):
        df[column].value_counts().plot(kind='pie', autopct='%1.1f%%', figsize=(6, 6))
        plt.title("Круговая диаграмма")
        plt.show()

    select_columns(callback, single=True)


def show_help():
    messagebox.showinfo("Помощь",
                        "1. Загрузите данные (CSV или Excel).\n2. Выберите тип графика.\n3. Анализируйте данные!")


buttons = [
    ("Загрузка данных", load_data),
    ("Линейный график", plot_line_chart),
    ("Гистограмма", plot_histogram),
    ("Диаграмма рассеяния", plot_scatter),
    ("Круговая диаграмма", plot_pie_chart),
    ("Помощь", show_help),
    ("Выход", root.quit)
]

for text, command in buttons:
    btn = ttk.Button(frame, text=text, style="TButton", command=command)
    btn.pack(pady=5, ipadx=10, ipady=5, fill="x")

root.mainloop()
