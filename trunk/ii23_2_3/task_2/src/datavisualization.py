import pandas as pd
import matplotlib.pyplot as plt

def make_linear_graph(y_data, y_label):
    if isinstance(y_data, pd.Series):
        if pd.api.types.is_numeric_dtype(y_data):
            plt.figure(figsize=(10, 6))
            plt.plot(y_data.index, y_data, label=y_label, color='blue')

            plt.title('Линейный график')
            plt.xlabel('Индекс')  # Ось X
            plt.ylabel(y_label)    # Ось Y
            plt.legend()
            plt.grid()
            plt.show()
        else:
            print("Ошибка: Все значения должны быть числовыми.")
    else:
        print("Ошибка: y_data должна быть pandas.Series.")

def make_scatter_diagram(x_data, y_data, x_label, y_label):
    if isinstance(x_data, pd.Series) and isinstance(y_data, pd.Series):
        # Проверяем, являются ли значения числовыми
        if pd.api.types.is_numeric_dtype(x_data) and pd.api.types.is_numeric_dtype(y_data):
            plt.figure(figsize=(10, 6))
            plt.scatter(x_data, y_data, label='Диаграмма рассеивания', color='blue')

            plt.title('Диаграмма рассеивания')
            plt.xlabel(x_label)  # Используем название колонки для оси X
            plt.ylabel(y_label)  # Используем название колонки для оси Y
            plt.legend()
            plt.grid()
            plt.show()
        else:
            print("Ошибка: Все значения должны быть числовыми.")
    else:
        print("Ошибка: x_data и y_data должны быть pandas.Series.")

def make_circle_diagram(data, label):
    if isinstance(data, pd.Series):
            counts = data.value_counts()

            plt.figure(figsize=(8, 8))
            plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90)
            plt.title(f'Круговая диаграмма для {label}')
            plt.axis('equal')
            plt.show()
    else:
        print("Ошибка: data должна быть pandas.Series.")

def make_hist(data, label, bins=10):
    if isinstance(data, pd.Series):
            plt.figure(figsize=(10, 6))
            plt.hist(data, bins=bins, color='blue', edgecolor='black', alpha=0.7)

            plt.title(f'Гистограмма для {label}')
            plt.xlabel(label)
            plt.ylabel('Частота')
            plt.grid(axis='y', alpha=0.75)
            plt.show()
    else:
        print("Ошибка: data должна быть pandas.Series.")

def clean_data(data):
    pass