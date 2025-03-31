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
import sys
import pandas as pd
import numpy as np

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QTableView,
    QVBoxLayout, QWidget, QComboBox, QPushButton, QLabel,
    QHBoxLayout, QMessageBox, QDialog, QFormLayout, QSplitter,
    QDialogButtonBox, QListWidget, QAbstractItemView, QToolBar,
    QSpinBox
)
from PySide6.QtCore import Qt, QAbstractTableModel, Slot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavToolbar
from matplotlib.figure import Figure


class DataFrameTableModel(QAbstractTableModel):
    """
    Класс-адаптер, позволяющий отображать pandas DataFrame в QTableView.
    """
    def __init__(self, dataframe):
        super().__init__()
        self._df = dataframe

    def rowCount(self, parent=None):
        return self._df.shape[0]

    def columnCount(self, parent=None):
        return self._df.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            val = self._df.iloc[index.row(), index.column()]
            return str(val)
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._df.columns[section])
            else:
                return str(self._df.index[section])
        return None

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            try:
                self._df.iloc[index.row(), index.column()] = float(value)
                self.dataChanged.emit(index, index)
                return True
            except ValueError:
                return False
        return False

    def flags(self, index):
        base_flags = super().flags(index)
        return base_flags | Qt.ItemIsEditable

    def sort(self, column, order):
        col_name = self._df.columns[column]
        ascending = (order == Qt.AscendingOrder)
        self.layoutAboutToBeChanged.emit()
        self._df.sort_values(by=col_name, ascending=ascending, inplace=True)
        self._df.reset_index(drop=True, inplace=True)
        self.layoutChanged.emit()


class PlotCanvas(QWidget):
    """
    Класс-обёртка над FigureCanvas и панелью инструментов matplotlib.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._figure = Figure()
        self.canvas = Canvas(self._figure)
        self.toolbar = NavToolbar(self.canvas, self)

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def clear_plot(self):
        self._figure.clear()

    def get_axes(self):
        return self._figure.add_subplot(111)

    def redraw(self):
        self.canvas.draw()


class ScalingDialog(QDialog):
    """
    Диалоговое окно для выбора метода нормализации (масштабирования).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор метода масштабирования")

        self.method_box = QComboBox()
        self.method_box.addItems(["Min-Max (0-1)", "Z-Score", "MaxAbs (-1..1)"])

        form = QFormLayout(self)
        form.addRow("Метод:", self.method_box)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        form.addRow(btns)


class AggregateDialog(QDialog):
    """
    Диалоговое окно для группировки и агрегирования данных.
    """
    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Группировка и агрегирование")

        self.cols_list = QListWidget()
        self.cols_list.addItems(columns)
        self.cols_list.setSelectionMode(QAbstractItemView.MultiSelection)

        self.agg_funcs = QComboBox()
        self.agg_funcs.addItems(["sum", "mean", "count", "min", "max"])

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Столбцы для группировки:"))
        layout.addWidget(self.cols_list)
        layout.addWidget(QLabel("Функция агрегирования:"))
        layout.addWidget(self.agg_funcs)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)


class DataVisualizerWindow(QMainWindow):
    """
    Основное окно приложения, предоставляющее функциональность:
    - Загрузка CSV/XLSX
    - Очистка пропущенных значений
    - Масштабирование числовых данных
    - Группировка и агрегирование
    - Удаление строк
    - Построение графиков (Line, Bar, Scatter, Pie, Histogram)
    - Экспорт графиков
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Visualizer: Interactive Charts")
        self.setMinimumSize(1200, 800)

        self.data_frame = None
        self._backup_data = None

        self._init_ui()

    def _init_ui(self):
        # Главное содержимое
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Разделитель
        self.splitter = QSplitter(Qt.Horizontal)
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.splitter)

        # Левая часть (управление)
        self.control_panel = QWidget()
        self.control_layout = QVBoxLayout(self.control_panel)

        # Панель инструментов
        self.toolbar = QToolBar("Основные действия")
        self.addToolBar(self.toolbar)

        self.btn_open_file = QPushButton("Загрузить данные")
        self.btn_open_file.clicked.connect(self.load_data)
        self.toolbar.addWidget(self.btn_open_file)

        self.btn_hide_table = QPushButton("Скрыть таблицу")
        self.btn_hide_table.setCheckable(True)
        self.btn_hide_table.clicked.connect(self.switch_table_visibility)
        self.toolbar.addWidget(self.btn_hide_table)

        # Типы диаграмм
        chart_box_label = QLabel("Тип визуализации:")
        self.chart_type_combo = QComboBox()
        # Добавляем гистограмму (Histogram) к списку
        self.chart_type_combo.addItems(["Line", "Bar", "Scatter", "Pie", "Histogram"])
        self.chart_type_combo.currentIndexChanged.connect(self.update_chart_controls)

        # Элементы для выбора осей
        self.x_axis_label = QLabel("X-Axis:")
        self.x_axis_combo = QComboBox()
        self.y_axis_label = QLabel("Y-Axis:")
        self.y_axis_combo = QComboBox()

        # Дополнительный контрол для гистограммы (количество корзин)
        self.hist_bins_label = QLabel("Количество корзин (Histogram):")
        self.hist_bins_spin = QSpinBox()
        self.hist_bins_spin.setRange(1, 100)
        self.hist_bins_spin.setValue(10)

        # Группы кнопок
        self.btn_normalize = QPushButton("Масштабировать")
        self.btn_normalize.clicked.connect(self.show_scaling_dialog)

        self.btn_aggregate = QPushButton("Агрегировать")
        self.btn_aggregate.clicked.connect(self.show_aggregate_dialog)

        self.btn_reset = QPushButton("Сброс данных")
        self.btn_reset.clicked.connect(self.restore_backup)

        self.btn_drop_na = QPushButton("Удалить пропущенные")
        self.btn_drop_na.clicked.connect(self.remove_missing)

        self.btn_remove_rows = QPushButton("Удалить выбранное")
        self.btn_remove_rows.clicked.connect(self.remove_selected)

        self.btn_export = QPushButton("Экспорт графика")
        self.btn_export.clicked.connect(self.export_plot)

        # Компонуем элементы на левой панели
        # Настройки для выбора диаграмм, осей, и т.д.
        self.control_layout.addWidget(chart_box_label)
        self.control_layout.addWidget(self.chart_type_combo)

        self.control_layout.addWidget(self.x_axis_label)
        self.control_layout.addWidget(self.x_axis_combo)
        self.control_layout.addWidget(self.y_axis_label)
        self.control_layout.addWidget(self.y_axis_combo)
        self.control_layout.addWidget(self.hist_bins_label)
        self.control_layout.addWidget(self.hist_bins_spin)

        # Блок кнопок обработки/агрегации
        self.control_layout.addWidget(self.btn_normalize)
        self.control_layout.addWidget(self.btn_aggregate)
        self.control_layout.addWidget(self.btn_drop_na)
        self.control_layout.addWidget(self.btn_remove_rows)
        self.control_layout.addWidget(self.btn_reset)
        self.control_layout.addWidget(self.btn_export)

        self.control_layout.addStretch()
        self.control_panel.setLayout(self.control_layout)

        # Центральная часть: таблица и виджет графиков
        self.table_view = QTableView()
        self.table_view.setSortingEnabled(True)

        self.plot_area = PlotCanvas()

        # Добавляем в сплиттер
        left_container = QSplitter(Qt.Vertical)
        left_container.addWidget(self.control_panel)
        left_container.addWidget(self.table_view)
        left_container.setSizes([200, 600])

        self.splitter.addWidget(left_container)
        self.splitter.addWidget(self.plot_area)
        self.splitter.setSizes([400, 800])

        # Первоначально скрываем настройки для гистограммы (пока не выбран Histogram)
        self.toggle_histogram_controls(False)

    @Slot()
    def switch_table_visibility(self, checked):
        self.table_view.setVisible(not checked)
        self.btn_hide_table.setText("Показать таблицу" if checked else "Скрыть таблицу")

    @Slot()
    def update_chart_controls(self):
        """
        Управляет видимостью различных контролов (оси X/Y, количество корзин)
        в зависимости от выбранного типа графика.
        """
        chart_type = self.chart_type_combo.currentText()
        if chart_type == "Pie":
            self.x_axis_label.setVisible(False)
            self.x_axis_combo.setVisible(False)
            self.y_axis_label.setText("Категория:")
            self.toggle_histogram_controls(False)
        elif chart_type == "Histogram":
            self.x_axis_label.setVisible(True)
            self.x_axis_combo.setVisible(True)
            self.y_axis_label.setText("Y-Axis:")
            self.toggle_histogram_controls(True)
        else:
            self.x_axis_label.setVisible(True)
            self.x_axis_combo.setVisible(True)
            self.y_axis_label.setText("Y-Axis:")
            self.toggle_histogram_controls(False)
        self.update_plot()

    def toggle_histogram_controls(self, visible):
        self.hist_bins_label.setVisible(visible)
        self.hist_bins_spin.setVisible(visible)

    @Slot()
    def load_data(self):
        """
        Загрузка CSV или Excel в pandas DataFrame и обновление таблицы.
        """
        filename, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл данных", "",
            "CSV Files (*.csv);;Excel Files (*.xlsx *.xls)"
        )
        if filename:
            try:
                if filename.endswith(".csv"):
                    self.data_frame = pd.read_csv(filename)
                else:
                    self.data_frame = pd.read_excel(filename)

                self._backup_data = self.data_frame.copy()
                self._refresh_table()
                self._refresh_axis_options()
                self.update_plot()
            except Exception as err:
                QMessageBox.critical(self, "Ошибка загрузки", f"Не удалось загрузить файл:\n{err}")

    def _refresh_table(self):
        if self.data_frame is not None:
            model = DataFrameTableModel(self.data_frame)
            model.dataChanged.connect(self.update_plot)  # Перестраивать график при редактировании
            self.table_view.setModel(model)
            self.table_view.resizeColumnsToContents()

    def _refresh_axis_options(self):
        if self.data_frame is not None and not self.data_frame.empty:
            cols = self.data_frame.columns.tolist()
            self.x_axis_combo.clear()
            self.x_axis_combo.addItems(cols)
            self.y_axis_combo.clear()
            self.y_axis_combo.addItems(cols)
            if len(cols) > 0:
                self.x_axis_combo.setCurrentIndex(0)
            if len(cols) > 1:
                self.y_axis_combo.setCurrentIndex(1)

    @Slot()
    def show_scaling_dialog(self):
        """
        Открывает диалоговое окно для выбора типа нормализации/масштабирования.
        """
        if self.data_frame is None or self.data_frame.empty:
            return
        dlg = ScalingDialog(self)
        if dlg.exec():
            method = dlg.method_box.currentText()
            numeric_cols = self.data_frame.select_dtypes(include=np.number).columns
            if numeric_cols.empty:
                QMessageBox.information(self, "Нет числовых столбцов", "Доступных числовых столбцов не найдено.")
                return

            try:
                if method == "Min-Max (0-1)":
                    self.data_frame[numeric_cols] = (
                        (self.data_frame[numeric_cols] - self.data_frame[numeric_cols].min()) /
                        (self.data_frame[numeric_cols].max() - self.data_frame[numeric_cols].min())
                    )
                elif method == "Z-Score":
                    self.data_frame[numeric_cols] = (
                        (self.data_frame[numeric_cols] - self.data_frame[numeric_cols].mean()) /
                        self.data_frame[numeric_cols].std()
                    )
                elif method == "MaxAbs (-1..1)":
                    self.data_frame[numeric_cols] = (
                        self.data_frame[numeric_cols] /
                        self.data_frame[numeric_cols].abs().max()
                    )
                self._refresh_table()
                self.update_plot()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка масштабирования", f"Произошла ошибка:\n{e}")

    @Slot()
    def show_aggregate_dialog(self):
        """
        Открывает диалоговое окно для группировки и агрегирования.
        """
        if self.data_frame is None or self.data_frame.empty:
            return
        dlg = AggregateDialog(self.data_frame.columns.tolist(), self)
        if dlg.exec():
            selected_cols = [it.text() for it in dlg.cols_list.selectedItems()]
            func = dlg.agg_funcs.currentText()
            if selected_cols:
                try:
                    self.data_frame = (
                        self.data_frame
                        .groupby(selected_cols)
                        .agg(func)
                        .reset_index()
                    )
                    self._refresh_table()
                    self._refresh_axis_options()
                    self.update_plot()
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка агрегирования", str(e))

    @Slot()
    def remove_missing(self):
        """
        Удаляет все строки с пропущенными значениями (NaN).
        """
        if self.data_frame is None or self.data_frame.empty:
            return
        confirmation = QMessageBox.question(
            self, "Подтверждение", "Удалить все строки с пропущенными значениями?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmation == QMessageBox.Yes:
            self.data_frame.dropna(inplace=True)
            self.data_frame.reset_index(drop=True, inplace=True)
            self._refresh_table()
            self._refresh_axis_options()
            self.update_plot()

    @Slot()
    def remove_selected(self):
        """
        Удаляет выделенные строки из DataFrame.
        """
        if self.data_frame is None:
            return
        selection = self.table_view.selectionModel().selectedRows()
        if not selection:
            QMessageBox.information(self, "Удаление строк", "Ничего не выбрано для удаления.")
            return
        confirmation = QMessageBox.question(
            self, "Подтверждение", "Действительно удалить выделенные строки?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmation == QMessageBox.Yes:
            for index in sorted(selection, key=lambda x: x.row(), reverse=True):
                row_idx = index.row()
                self.data_frame.drop(self.data_frame.index[row_idx], inplace=True)
            self.data_frame.reset_index(drop=True, inplace=True)
            self._refresh_table()
            self._refresh_axis_options()
            self.update_plot()

    @Slot()
    def restore_backup(self):
        """
        Восстанавливает исходные данные из бэкапа (до изменений).
        """
        if self._backup_data is not None:
            self.data_frame = self._backup_data.copy()
            self._refresh_table()
            self._refresh_axis_options()
            self.update_plot()

    def update_plot(self):
        """
        Построение/обновление графика в соответствии с выбранными параметрами.
        """
        if self.data_frame is None or self.data_frame.empty:
            return

        self.plot_area.clear_plot()
        ax = self.plot_area.get_axes()

        ctype = self.chart_type_combo.currentText()
        all_cols = self.data_frame.columns.tolist()

        if ctype == "Pie":
            # Для круговой диаграммы нам нужна только "категория" (Y)
            category = self.y_axis_combo.currentText()
            if category not in all_cols:
                return
            counts = self.data_frame[category].value_counts()
            ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%")
            ax.set_title(f"Pie Chart of {category}")
        elif ctype == "Histogram":
            # Для гистограммы достаточно одного столбца (X)
            col_x = self.x_axis_combo.currentText()
            if col_x not in all_cols:
                return
            bins = self.hist_bins_spin.value()
            ax.hist(self.data_frame[col_x].dropna(), bins=bins)
            ax.set_xlabel(col_x)
            ax.set_ylabel("Count")
            ax.set_title(f"Histogram of {col_x}")
        else:
            # Для всех остальных (Line, Bar, Scatter) нужны X и Y
            col_x = self.x_axis_combo.currentText()
            col_y = self.y_axis_combo.currentText()
            if col_x not in all_cols or col_y not in all_cols:
                return

            if ctype == "Line":
                ax.plot(self.data_frame[col_x], self.data_frame[col_y], marker='o')
                ax.set_title(f"{col_y} vs {col_x}")
            elif ctype == "Bar":
                ax.bar(self.data_frame[col_x], self.data_frame[col_y])
                ax.set_title(f"Bar Chart of {col_y} by {col_x}")
            elif ctype == "Scatter":
                ax.scatter(self.data_frame[col_x], self.data_frame[col_y])
                ax.set_title(f"Scatter Plot of {col_y} vs {col_x}")

            ax.set_xlabel(col_x)
            ax.set_ylabel(col_y)

        self.plot_area.redraw()

    @Slot()
    def export_plot(self):
        """
        Экспорт текущего графика в PNG, JPEG или PDF.
        """
        if self.data_frame is None:
            return
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить график", "",
            "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg);;PDF File (*.pdf)"
        )
        if filename:
            try:
                self.plot_area._figure.savefig(filename)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка сохранения", str(e))


def main():
    app = QApplication(sys.argv)
    window = DataVisualizerWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```
 
## Результаты работы

Интерфейс до загрузки данных
 ![](img/1.png)

Выбор загружаемого файла
 ![](img/2.png)

Интерфейс после загрузки данных
 ![](img/3.png)

 
1. Интерфейс пользователя:
    - Возможность загрузки файлов данных (например, CSV, Excel).✅
      ![](img/4.png)
    - Меню для выбора типов визуализации (линейные графики, гистограммы, диаграммы рассеяния и т.д.).✅
      ![](img/5.png)
      - Интерактивные элементы управления (фильтры, ползунки, выпадающие списки и т.д.) для изменения параметров визуализации.✅
      ![](img/6.png)
      ![](img/7.png)
      ![](img/8.png)
      ![](img/9.png)
      - показать таблицу:
      ![](img/12.png)
      - скрыть таблицу:
      ![](img/13.png)
2. Обработка данных:
    - Импорт данных из загруженных файлов + визуализация данных в форме таблицы.✅
      ![](img/10.png)
    - Обработка и очистка данных (например, устранение пропущенных значений, нормализация).✅
      например, удаление пропущенных значений:
    - кнопка удаления:
    - ![](img/11.png)
      до удаления:
    - ![](img/14.png)
    - после удаления:
    - ![](img/15.png)
    - ![](img/16.png)
    - Возможность удаления выделенных данных:
    - ![img.png](17.png)
    - ![img.png](18.png)
    - ![img.png](19.png)
    - Возможность группировки и агрегирования данных.✅
    - ![](img/20.png)
    - ![](img/21.png)
1. Алгоритмы визуализации:
    - Реализация различных типов визуализаций (линейные графики, гистограммы, диаграммы рассеяния, круговые диаграммы и т.д.).✅
      ![](img/22.png)
      ![](img/23.png)
    - ![](img/24.png)
    - Возможность динамического обновления визуализаций при изменении параметров.✅
    - Интерактивные графики (увеличение, уменьшение, выделение отдельных элементов).✅
      - ![](img/25.png)
      - ![](img/26.png)
      - ![](img/27.png)
1. Функциональные возможности:
    - Возможность экспорта визуализаций в виде изображений (PNG, JPEG) или PDF.✅
      - ![](img/28.png)
      - ![](img/29.png)
