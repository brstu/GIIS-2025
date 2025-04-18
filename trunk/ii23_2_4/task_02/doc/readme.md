# Лабораторная работа 2

## Тема: "Интерактивный визуализатор данных"

## Цель работы

 Загрузка данных в табличном формате и отображение результатов в виде графиков и диаграмм для последующего анализа

## Основные требования

1. Интерфейс пользователя:
    - Возможность загрузки файлов данных (например, CSV, Excel).
    - Меню для выбора типов визуализации (линейные графики, гистограммы, диаграммы рассеяния и т.д.).
    - Интерактивные элементы управления (фильтры, ползунки, выпадающие списки и т.д.) для изменения параметров визуализации.
2. Обработка данных:
    - Импорт данных из загруженных файлов + визуализация данных в форме таблицы.
    - Обработка и очистка данных (например, устранение пропущенных значений, нормализация).
    - Возможность группировки и агрегирования данных.
3. Алгоритмы визуализации:
    - Реализация различных типов визуализаций (линейные графики, гистограммы, диаграммы рассеяния, круговые диаграммы и т.д.).
    - Возможность динамического обновления визуализаций при изменении параметров.
    - Интерактивные графики (увеличение, уменьшение, выделение отдельных элементов).
4. Функциональные возможности:
    - Возможность экспорта визуализаций в виде изображений (PNG, JPEG) или PDF.
    - Встроенные пояснения и подсказки для пользователей.

    
Оценка работы:
Для оценки работы в 4-5 баллов, нужно выполнить все Зеленые пункты.
Для оценки работы в 7-8 баллов, нужно дополнительно выполнить Бирюзовые пункты. Их всего 4, можно взять любые 3. 
Для оценки в 9-10 нужно выполнить Фиолетовые пункты. Их всего 2.
Итоговая оценка за работу складывается из числа выполненных требований к работе. Обязательными считаются зеленые, все остальные повышают итоговую оценку за работу. 

 

## Код программы

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import chardet

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read(10000)
        result = chardet.detect(raw_data)
        return result['encoding']

def load_data(file_path):
    try:
        if file_path.endswith('.csv'):
            encoding = detect_encoding(file_path)
            return pd.read_csv(file_path, encoding=encoding)
        elif file_path.endswith('.xlsx'):
            return pd.read_excel(file_path)
        else:
            messagebox.showerror("Ошибка", "Формат файла не поддерживается. Загрузите CSV или Excel.")
            return None
    except UnicodeDecodeError:
        messagebox.showerror("Ошибка", "Не удалось загрузить файл из-за проблемы с кодировкой.")
        return None
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
        return None

def clean_data(df):
    df.dropna(inplace=True)
    return df

def visualize_data(df, chart_type, x_col, y_col):
    plt.figure(figsize=(8, 5))
    if chart_type == "Линейный график":
        sns.lineplot(x=df[x_col], y=df[y_col])
    elif chart_type == "Гистограмма":
        sns.histplot(df[x_col], bins=20, kde=True)
    elif chart_type == "Диаграмма рассеяния":
        sns.scatterplot(x=df[x_col], y=df[y_col])
    elif chart_type == "Круговая диаграмма":
        df[x_col].value_counts().plot.pie(autopct='%1.1f%%')
    plt.show()

def select_file():
    global df
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
    if file_path:
        df = load_data(file_path)
        if df is not None:
            df = clean_data(df)
            columns = df.columns.tolist()
            x_col.set(columns[0] if columns else "")
            y_col.set(columns[1] if len(columns) > 1 else "")
            data_preview.set(df.head().to_string())

def plot_graph():
    if df is None:
        messagebox.showwarning("Предупреждение", "Сначала загрузите данные!")
        return
    try:
        visualize_data(df, chart_type.get(), x_col.get(), y_col.get())
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось построить график: {e}")

def create_gui():
    global x_col, y_col, chart_type, data_preview, df
    df = None
    root = tk.Tk()
    root.title("Визуализатор данных")
    root.geometry("600x500")
    root.configure(bg="#2E3B4E")
    
    style = ttk.Style()
    style.configure("TButton", font=("Arial", 12), padding=5, background="#4CAF50", foreground="white")
    style.configure("TLabel", font=("Arial", 12), background="#2E3B4E", foreground="white")
    style.configure("TCombobox", font=("Arial", 12))
    style.configure("TFrame", background="#2E3B4E")
    
    frame = ttk.Frame(root, padding=10)
    frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    ttk.Label(frame, text="Выберите файл данных:").grid(row=0, column=0, pady=5, sticky="w")
    ttk.Button(frame, text="Загрузить файл", command=select_file).grid(row=0, column=1, pady=5, padx=10)
    
    ttk.Label(frame, text="Выберите тип графика:").grid(row=1, column=0, pady=5, sticky="w")
    chart_type = tk.StringVar(value="Линейный график")
    ttk.Combobox(frame, textvariable=chart_type, values=["Линейный график", "Гистограмма", "Диаграмма рассеяния", "Круговая диаграмма"]).grid(row=1, column=1, pady=5, padx=10)
    
    ttk.Label(frame, text="X-ось:").grid(row=2, column=0, pady=5, sticky="w")
    x_col = tk.StringVar()
    ttk.Entry(frame, textvariable=x_col).grid(row=2, column=1, pady=5, padx=10)
    
    ttk.Label(frame, text="Y-ось:").grid(row=3, column=0, pady=5, sticky="w")
    y_col = tk.StringVar()
    ttk.Entry(frame, textvariable=y_col).grid(row=3, column=1, pady=5, padx=10)
    
    ttk.Button(frame, text="Построить график", command=plot_graph).grid(row=4, column=0, columnspan=2, pady=10)
    
    preview_frame = ttk.LabelFrame(frame, text="Предпросмотр данных", padding=5)
    preview_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky="nsew")
    
    data_preview = tk.StringVar()
    preview_label = ttk.Label(preview_frame, textvariable=data_preview, justify="left")
    preview_label.pack()
    
    root.mainloop()

def main():
    create_gui()

if __name__ == "__main__":
    main()

```
 
## Результаты работы

 
1. Интерфейс пользователя:
    - Возможность загрузки файлов данных (например, CSV, Excel).✅
      ![](img/2.png)
    - Меню для выбора типов визуализации (линейные графики, гистограммы, диаграммы рассеяния и т.д.).✅
    - Интерактивные элементы управления (фильтры, ползунки, выпадающие списки и т.д.) для изменения параметров визуализации.✅


2. Обработка данных:
    - Импорт данных из загруженных файлов + визуализация данных в форме таблицы.✅
    - Обработка и очистка данных (например, устранение пропущенных значений, нормализация).✅
    - Возможность группировки и агрегирования данных.
      
3. Алгоритмы визуализации:
    - Реализация различных типов визуализаций (линейные графики, гистограммы, диаграммы рассеяния, круговые диаграммы и т.д.).✅
    - Возможность динамического обновления визуализаций при изменении параметров.
    - Интерактивные графики (увеличение, уменьшение, выделение отдельных элементов).


4. Функциональные возможности:
    - Возможность экспорта визуализаций в виде изображений (PNG, JPEG) или PDF.✅
    - Встроенные пояснения и подсказки для пользователей.✅
