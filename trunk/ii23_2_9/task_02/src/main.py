import sys
import pandas as pd
import numpy as np
from PySide6.QtWidgets import (QApplication, QMainWindow, QFileDialog, QTableView,
                               QVBoxLayout, QWidget, QComboBox, QPushButton, QLabel,
                               QHBoxLayout, QMessageBox, QDialog, QFormLayout, QSplitter,
                               QLineEdit, QDialogButtonBox, QListWidget, QAbstractItemView, QToolBar)
from PySide6.QtCore import Qt, QAbstractTableModel, Slot, QItemSelectionModel, QItemSelection
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
            else:
                return str(self._data.index[section])
        return None

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            try:
                self._data.iloc[index.row(), index.column()] = float(value)
                self.dataChanged.emit(index, index)
                return True
            except:
                return False
        return False

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsEditable

    def sort(self, column, order):
        colname = self._data.columns[column]
        ascending = (order == Qt.AscendingOrder)
        self.layoutAboutToBeChanged.emit()
        self._data.sort_values(by=colname, ascending=ascending, inplace=True)
        self._data.reset_index(drop=True, inplace=True)
        self.layoutChanged.emit()


class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_figure(self, x, y, chart_type):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if chart_type == 'Line':
            ax.plot(x, y, label=f'{y.name} vs {x.name}')
        elif chart_type == 'Bar':
            ax.bar(x, y, label=f'{y.name} by {x.name}')
        elif chart_type == 'Scatter':
            ax.scatter(x, y, label=f'{y.name} vs {x.name}')
        elif chart_type == 'Pie':
            counts = y.value_counts()
            ax.pie(counts.values, labels=counts.index, autopct='%1.1f%%')

        ax.set_title(f"{chart_type} Chart")
        ax.legend()
        self.canvas.draw()


class NormalizationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Normalization Settings")
        layout = QFormLayout()

        self.method = QComboBox()
        self.method.addItems(["Min-Max (0-1)", "Z-Score", "MaxAbs (-1 to 1)"])

        layout.addRow("Normalization Method:", self.method)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addRow(buttons)
        self.setLayout(layout)


class GroupByDialog(QDialog):
    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Group By Settings")
        layout = QVBoxLayout()

        self.group_columns = QListWidget()
        self.group_columns.addItems(columns)
        self.group_columns.setSelectionMode(QAbstractItemView.MultiSelection)

        self.agg_function = QComboBox()
        self.agg_function.addItems(["sum", "mean", "count", "min", "max"])

        layout.addWidget(QLabel("Group by columns:"))
        layout.addWidget(self.group_columns)
        layout.addWidget(QLabel("Aggregation function:"))
        layout.addWidget(self.agg_function)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.df = None
        self.original_df = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Advanced Data Visualizer')
        self.setGeometry(100, 100, 1400, 900)

        # Главный виджет и splitter
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.splitter = QSplitter(Qt.Vertical)

        # Виджет для управления
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)

        # Панель инструментов
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Кнопки управления
        self.toggle_table_btn = QPushButton('Скрыть таблицу')
        self.toggle_table_btn.setCheckable(True)
        self.toggle_table_btn.clicked.connect(self.toggle_table)
        toolbar.addWidget(self.toggle_table_btn)

        self.load_btn = QPushButton('Загрузить файл')
        self.load_btn.clicked.connect(self.load_file)
        toolbar.addWidget(self.load_btn)

        # Группа настроек графика
        settings_group = QWidget()
        settings_layout = QFormLayout(settings_group)

        self.chart_type = QComboBox()
        self.chart_type.addItems(['Line', 'Bar', 'Scatter', 'Pie'])
        settings_layout.addRow(QLabel('Тип графика:'), self.chart_type)

        # Виджеты для выбора осей
        self.x_widget = QWidget()
        x_layout = QHBoxLayout(self.x_widget)
        x_layout.setContentsMargins(0, 0, 0, 0)
        self.x_label = QLabel('Ось X:')
        self.x_column = QComboBox()
        x_layout.addWidget(self.x_label)
        x_layout.addWidget(self.x_column)

        self.y_widget = QWidget()
        y_layout = QHBoxLayout(self.y_widget)
        y_layout.setContentsMargins(0, 0, 0, 0)
        self.y_label = QLabel('Ось Y:')
        self.y_column = QComboBox()
        y_layout.addWidget(self.y_label)
        y_layout.addWidget(self.y_column)

        settings_layout.addRow(self.x_widget)
        settings_layout.addRow(self.y_widget)

        control_layout.addWidget(settings_group)

        # Кнопки операций
        btn_group = QWidget()
        btn_layout = QHBoxLayout(btn_group)

        self.normalize_btn = QPushButton('Нормировать')
        self.group_btn = QPushButton('Группировать')
        self.reset_btn = QPushButton('Сброс')
        self.export_btn = QPushButton('Экспорт')
        self.clean_btn = QPushButton('Очистка данных')
        self.delete_btn = QPushButton('Удалить выбранные строки')

        btn_layout.addWidget(self.normalize_btn)
        btn_layout.addWidget(self.group_btn)
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.clean_btn)
        btn_layout.addWidget(self.delete_btn)

        control_layout.addWidget(btn_group)

        # Таблица данных
        self.table_view = QTableView()
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSortingEnabled(True)  # Включаем сортировку по заголовкам

        # График
        self.plot_widget = MatplotlibWidget()

        # Сборка интерфейса
        self.splitter.addWidget(control_widget)
        self.splitter.addWidget(self.table_view)
        self.splitter.addWidget(self.plot_widget)
        self.splitter.setSizes([100, 300, 500])

        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(self.splitter)

        # Сигналы
        self.chart_type.currentTextChanged.connect(self.update_controls_visibility)
        self.chart_type.currentIndexChanged.connect(self.update_plot)
        self.x_column.currentIndexChanged.connect(self.update_plot)
        self.y_column.currentIndexChanged.connect(self.update_plot)
        self.normalize_btn.clicked.connect(self.show_normalization_dialog)
        self.group_btn.clicked.connect(self.show_group_dialog)
        self.reset_btn.clicked.connect(self.reset_data)
        self.export_btn.clicked.connect(self.export_plot)
        self.clean_btn.clicked.connect(self.clean_data)
        self.delete_btn.clicked.connect(self.delete_selected_rows)

        # Инициализация видимости элементов
        self.update_controls_visibility()

    def toggle_table(self, checked):
        self.table_view.setVisible(not checked)
        self.toggle_table_btn.setText('Показать таблицу' if checked else 'Скрыть таблицу')

    def update_controls_visibility(self):
        """Скрываем X для Pie-графика"""
        is_pie = self.chart_type.currentText() == 'Pie'
        self.x_widget.setVisible(not is_pie)
        self.y_label.setText('Категория:' if is_pie else 'Ось Y:')

    @Slot()
    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Open File', '', 'CSV (*.csv);;Excel (*.xlsx)')
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.df = pd.read_csv(file_path)
                elif file_path.endswith('.xlsx'):
                    self.df = pd.read_excel(file_path)
                self.original_df = self.df.copy()
                self.update_table()
                self.update_columns()
                self.update_plot()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Ошибка загрузки: {str(e)}")

    def update_table(self):
        model = PandasModel(self.df)
        model.dataChanged.connect(self.on_data_changed)
        self.table_view.setModel(model)
        self.table_view.resizeColumnsToContents()
        self.table_view.setSortingEnabled(True)

    def on_data_changed(self):
        self.update_plot()

    def update_columns(self):
        self.x_column.clear()
        self.y_column.clear()
        if self.df is not None and not self.df.empty:
            columns = self.df.columns.tolist()
            self.x_column.addItems(columns)
            self.y_column.addItems(columns)
            if len(columns) >= 1:
                self.x_column.setCurrentIndex(0)
            if len(columns) >= 2:
                self.y_column.setCurrentIndex(1)

    @Slot()
    def show_normalization_dialog(self):
        if self.df is None:
            return

        dialog = NormalizationDialog(self)
        if dialog.exec():
            method = dialog.method.currentText()
            numeric_cols = self.df.select_dtypes(include=np.number).columns

            if method == "Min-Max (0-1)":
                self.df[numeric_cols] = (self.df[numeric_cols] - self.df[numeric_cols].min()) / (
                        self.df[numeric_cols].max() - self.df[numeric_cols].min())
            elif method == "Z-Score":
                self.df[numeric_cols] = (self.df[numeric_cols] - self.df[numeric_cols].mean()) / self.df[
                    numeric_cols].std()
            elif method == "MaxAbs (-1 to 1)":
                self.df[numeric_cols] = self.df[numeric_cols] / self.df[numeric_cols].abs().max()

            self.update_table()
            self.update_plot()

    @Slot()
    def show_group_dialog(self):
        if self.df is None:
            return

        dialog = GroupByDialog(self.df.columns.tolist(), self)
        if dialog.exec():
            selected_columns = [item.text() for item in dialog.group_columns.selectedItems()]
            agg_func = dialog.agg_function.currentText()

            if selected_columns:
                self.df = self.df.groupby(selected_columns).agg(agg_func).reset_index()
                self.update_table()
                self.update_columns()
                self.update_plot()

    @Slot()
    def reset_data(self):
        if self.original_df is not None:
            self.df = self.original_df.copy()
            self.update_table()
            self.update_columns()
            self.update_plot()

    @Slot()
    def clean_data(self):
        if self.df is None:
            return
        reply = QMessageBox.question(self, "Подтверждение", "Удалить строки с пропущенными значениями?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.df = self.df.dropna().reset_index(drop=True)
            self.update_table()
            self.update_columns()
            self.update_plot()

    @Slot()
    def delete_selected_rows(self):
        if self.df is None:
            return
        selected = self.table_view.selectionModel().selectedRows()
        if not selected:
            QMessageBox.information(self, "Удаление строк", "Не выбраны строки для удаления.")
            return
        reply = QMessageBox.question(self, "Подтверждение", "Удалить выбранные строки?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            indices = sorted([index.row() for index in selected], reverse=True)
            for row in indices:
                idx = self.df.index[row]
                self.df = self.df.drop(idx)
            self.df = self.df.reset_index(drop=True)
            self.update_table()
            self.update_columns()
            self.update_plot()

    def update_plot(self):
        if self.df is None or self.df.empty:
            return

        chart_type = self.chart_type.currentText()
        columns = self.df.columns.tolist()

        if not columns:
            return

        if chart_type != 'Pie':
            x_col = self.x_column.currentText()
            y_col = self.y_column.currentText()
            if x_col not in columns:
                x_col = columns[0]
                self.x_column.setCurrentText(x_col)
            if y_col not in columns:
                y_col = columns[0]
                self.y_column.setCurrentText(y_col)
        else:
            y_col = self.y_column.currentText()
            if y_col not in columns:
                y_col = columns[0]
                self.y_column.setCurrentText(y_col)
            x_col = None

        try:
            self.plot_widget.figure.clear()
            ax = self.plot_widget.figure.add_subplot(111)

            if chart_type == 'Line':
                ax.plot(self.df[x_col], self.df[y_col])
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.set_title(f"{y_col} vs {x_col}")
            elif chart_type == 'Bar':
                ax.bar(self.df[x_col], self.df[y_col])
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.set_title(f"{y_col} by {x_col}")
            elif chart_type == 'Scatter':
                ax.scatter(self.df[x_col], self.df[y_col])
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.set_title(f"{y_col} vs {x_col}")
            elif chart_type == 'Pie':
                counts = self.df[y_col].value_counts()
                ax.pie(counts.values, labels=counts.index, autopct='%1.1f%%')
                ax.set_title(f"Distribution of {y_col}")

            self.plot_widget.canvas.draw()
        except Exception as e:
            QMessageBox.critical(self, "Plot Error", f"Ошибка построения графика: {repr(e)}")

    @Slot()
    def export_plot(self):
        if self.df is not None:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Plot", "", "PNG (*.png);;PDF (*.pdf)", options=options)
            if file_path:
                try:
                    self.plot_widget.figure.savefig(file_path)
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())
