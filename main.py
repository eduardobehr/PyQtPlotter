# This Python file uses the following encoding: utf-8
import sys
# from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5 import QtGui, QtCore
from numpy import *
from PyQt5.Qt import QGraphicsLayout, QGraphicsWidget
# from pyqtgraph.graphicsItems import GraphicsLayout, GraphicsWidget
import numpy as np
import pyqtgraph as pg
from typing import Union
from csvcurveloader import CSVCurveLoader
import pandas as pd


# presets:
DEBUG = False
X_RANGE: tuple = (-10, +10)  # minimum and maximum value for the independent variable x (used as linspace argument)
X_DATA_POINTS: int = 1001  # number of data points for the x linspace

VIEWBOX = {
    'xmin': -10, 'xmax': +10,
    'ymin': -10, 'ymax': +10
}

ANTIALIASING = False
LINE_WIDTH = 3

COLORS = [
    pg.QtGui.QColor(*([int(255*0.000), int(255*0.447), int(255*0.741)])),
    pg.QtGui.QColor(*([int(255*0.850), int(255*0.325), int(255*0.098)])),
    pg.QtGui.QColor(*([int(255*0.929), int(255*0.694), int(255*0.125)])),
    pg.QtGui.QColor(*([int(255*0.494), int(255*0.184), int(255*0.556)])),
    pg.QtGui.QColor(*([int(255*0.466), int(255*0.674), int(255*0.188)])),
    pg.QtGui.QColor(*([int(255*0.301), int(255*0.745), int(255*0.933)])),
    pg.QtGui.QColor(*([int(255*0.635), int(255*0.078), int(255*0.184)]))
]


class QTextBrowser2(QTextBrowser):
    def __init__(self, *args, **kwargs):
        QTextBrowser.__init__(self)

    def keyPressEvent(self, a0: QtGui.QKeyEvent) -> None:
        if a0.key() == Qt.Key_Enter:
            print("AAAA")
            window.plot_text_input_data()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle('PyQt Plotter')
        self.resize(1000, 600)
        pg.setConfigOptions(antialias=ANTIALIASING)
        #
        # Define entities
        self.color_counter = 0
        self.pen = pg.mkPen(color=COLORS[self.color_counter], width=LINE_WIDTH)
        self.central_widget = QWidget(flags=Qt.WindowFlags())
        self.plot_widget = pg.GraphicsLayoutWidget(show=False, title="None")
        self.plot_widget.setBackground(background='w')
        self.plot_button = QPushButton('Plot')
        self.reset_button = QPushButton('Reset')
        self.v_layout = QVBoxLayout()
        self.function_input = QTextEdit()
        self.function_input.setStyleSheet("font: 20pt")
        self.input_label = QLabel('f(X)=')
        self.input_label.setStyleSheet("font: 20pt")
        self.bottom_HLayout_1 = QHBoxLayout()  # function input and buttons
        self.bottom_HLayout_2 = QHBoxLayout()  # console output messages
        self.bottom_FLayout_parameters = QFormLayout()

        self.spinbox_Xrange_min = QDoubleSpinBox()
        self.spinbox_Xrange_max = QDoubleSpinBox()
        self.spinbox_data_points = QSpinBox()
        self.label_Xrange_min = QLabel('X min')
        self.label_Yrange_max = QLabel('X max')
        self.label_data_points = QLabel('Points')

        self.output_text_browser = QTextBrowser2()
        self.QtText = QtGui.QTextDocument()
        self.input = ""  # function f(x) given by the user in order to plot
        self.input_string = ""  # same as input defined above, but replacing X by self.x
        self.pending_x_update = False  # stores the state of if any update on x linspace is needed
        self.toolbar: QToolBar = self.addToolBar('test')
        self.load_button = QToolButton()
        self.load_button.setText('Load CSV file')
        self.toolbar.addWidget(self.load_button)
        self.csv_data = None
        self.x_csv = None
        self.y_csv = None
        self.curves = []  # keeps track of all the curves
        # -------------------------------------------------------------------------------------------------------------
        # Configure entities (in order of appearance)
        self.load_button.setText('Load CSV file')
        self.load_button.released.connect(self.load_curve)

        self.plot_widget.setMinimumSize(300, 300)

        self.v_layout.addWidget(self.plot_widget, alignment=Qt.Alignment())
        self.v_layout.addLayout(self.bottom_HLayout_1)
        self.v_layout.addLayout(self.bottom_HLayout_2)

        self.bottom_HLayout_1.setSizeConstraint(QLayout.SetMaximumSize)
        self.bottom_HLayout_1.addWidget(self.input_label, alignment=Qt.Alignment())
        self.bottom_HLayout_1.addWidget(self.function_input, alignment=Qt.Alignment())
        self.bottom_HLayout_1.addWidget(self.plot_button, alignment=Qt.Alignment())
        self.bottom_HLayout_1.addWidget(self.reset_button, alignment=Qt.Alignment())

        self.bottom_HLayout_2.addWidget(self.output_text_browser)
        self.bottom_HLayout_2.addLayout(self.bottom_FLayout_parameters)

        self.output_text_browser.setMaximumHeight(100)

        self.bottom_FLayout_parameters.addRow(self.label_Xrange_min, self.spinbox_Xrange_min)
        self.bottom_FLayout_parameters.addRow(self.label_Yrange_max, self.spinbox_Xrange_max)
        self.bottom_FLayout_parameters.addRow(self.label_data_points, self.spinbox_data_points)

        # TODO
        #   add dynamic range max/min

        self.spinbox_Xrange_min.setDecimals(3)  # adjusting precision
        self.spinbox_Xrange_max.setDecimals(3)  # adjusting precision

        self.spinbox_Xrange_min.setMinimumWidth(100)  # adjusting geometric width
        self.spinbox_Xrange_max.setMinimumWidth(100)  # adjusting geometric width
        self.spinbox_data_points.setMinimumWidth(100)  # adjusting geometric width

        self.spinbox_Xrange_min.setRange(-1e12, 1e12)  # setting absolute static limits
        self.spinbox_Xrange_max.setRange(-1e12, 1e12)  # setting absolute static limits
        self.spinbox_data_points.setRange(2, 100001)   # setting absolute static limits

        self.spinbox_Xrange_min.setValue(X_RANGE[0])  # setting initial value
        self.spinbox_Xrange_max.setValue(X_RANGE[1])  # setting initial value
        self.spinbox_data_points.setValue(X_DATA_POINTS)  # setting initial value




        # self.spinbox_Xrange_min.valueChanged.connect(
        #     lambda: self.spinbox_Xrange_max.setMinimum(self.spinbox_Xrange_min.value())
        # )
        self.spinbox_Xrange_min.valueChanged.connect(self.raise_flag_update_x)
        self.spinbox_Xrange_max.valueChanged.connect(self.raise_flag_update_x)
        self.spinbox_data_points.valueChanged.connect(self.raise_flag_update_x)

        self.plot_button.setFixedHeight(40)
        self.plot_button.released.connect(self.plot_text_input_data)

        self.reset_button.setFixedHeight(40)
        self.reset_button.released.connect(self.reset_plot)

        self.central_widget.setLayout(self.v_layout)
        self.setCentralWidget(self.central_widget)

        self.function_input.setMaximumHeight(40)
        self.function_input.setMinimumWidth(200)

        self.function_input.setDocument(self.QtText)
        self.function_input.textChanged.connect(self.on_input_change)
        self.function_input.setText(f"{VIEWBOX['ymax']}*sin(X)/X")

        self.QtText.setMaximumBlockCount(1)
        self.plot_canvas = self.plot_widget.addPlot()
        self.plot_canvas.setXRange(VIEWBOX['xmin'], VIEWBOX['xmax'], padding=0)
        self.plot_canvas.setYRange(VIEWBOX['ymin'], VIEWBOX['ymax'], padding=0)
        self.plot_canvas.showGrid(x=True, y=True, alpha=1)
        self.plot_canvas.setDownsampling(mode='mean', auto=True)  # 'peak', 'mean', 'subsample'
        self.plot_canvas.setClipToView(True)

        self.x = linspace(
            self.spinbox_Xrange_min.value(),
            self.spinbox_Xrange_max.value(),
            self.spinbox_data_points.value())
        self.y = None
        self.xy_limits = {"x": 1e6, "y": 1e6}  # in absolute value

    def raise_flag_update_x(self):
        """ The program waits for the plot method to update x. Triggered by spin boxes values changes """
        self.pending_x_update = True

    def update_x(self):
        """ Recreates the x linspace, only upon plotting, if flag is True"""
        self.x = linspace(
            self.spinbox_Xrange_min.value(),
            self.spinbox_Xrange_max.value(),
            self.spinbox_data_points.value())

        self.pending_x_update = False

    def print_output(self, message: str):
        """ Wrapper for printing text to the embedded console output"""
        self.output_text_browser.append(message)

    def plot_text_input_data(self) -> None:
        # if DEBUG: print(f'plotting init: from {self.x[0]} to {self.x[-1]}')

        if self.spinbox_Xrange_min.value() > self.spinbox_Xrange_max.value():  # crossed range limits
            start = self.spinbox_Xrange_min.value()
            end = self.spinbox_Xrange_max.value()
            self.print_output(f'Warning: limits mismatch. End x value {end} cannot be less than start x value {start}. End value changed to {start+1}.')
            self.spinbox_Xrange_max.setValue(self.spinbox_Xrange_min.value() + 1)

        if self.pending_x_update:
            self.update_x()
        # if DEBUG: print(f'plotting actually: from {self.x[0]} to {self.x[-1]}')
        try:
            self.y = eval(
                self.input_string
            )
            try:
                indexes_to_delete = []  # when operation results in either +- inf or nan, remove elements from arrays
                for index in range(len(self.y)):
                    if self.y[index] > self.xy_limits['y'] and self.y[index] != inf:
                        self.y[index] = self.xy_limits['y']
                    elif self.y[index] < -self.xy_limits['y'] and self.y[index] != -inf:
                        self.y[index] = -self.xy_limits['y']
                    elif -self.xy_limits['y'] < self.y[index] < self.xy_limits['y']:
                        pass
                    else:
                        indexes_to_delete.append(index)
                if indexes_to_delete:
                    self.y = delete(self.y, obj=indexes_to_delete)
                    self.x = delete(self.x, obj=indexes_to_delete)
            except IndexError:
                # when values from the indexed arrays are removed, and the array changes its size
                pass
            except TypeError:
                # when value given is not an array, but rather a single element.
                # may happen if given function is independent of X, that is, a constant. Ex: f(X) = 2
                if isinstance(self.y, (int, float)):
                    self.y *= ones(self.x.size)
                pass
            except ValueError:
                self.print_output('ValueError')
                pass
            # TODO: Optimize step size to improve performance.
            #   make step size vary with the derivative of the function (proportionally inverse?)
            #   X = linspace(-10,10,100001)  # this is evenly spaced, but very fine everywhere. Bad performance
            #   y=f(X) = 1/X        =>        y' = -1/X²        step = a * 1/y' = -X²
            #   Now make X = -10.....10 with varying step as calculated above, with
            #    fine steps around 0, gross steps at the edges (-10, 10). This spares samples and improves performance
            #   Finally, recalculate y with the new X

            # Finally, draw the function
            self.update_pen_color()
            self.plot_xy(self.x, self.y)

            if len(self.x) < X_DATA_POINTS:  # if x lost elements, resize it
                self.x = linspace(self.spinbox_Xrange_min.value(), self.spinbox_Xrange_max.value(), X_DATA_POINTS)
            self.print_output(f"Plotting {self.input}")
        except SyntaxError:
            self.print_output("SyntaxError")
        except NameError:
            self.print_output("NameError: use numpy syntax with uppercase X. Example: \n  sqrt(X)\n  exp(X)")
        except ZeroDivisionError:
            self.print_output("ZeroDivisionError")

    def plot_xy(self, x_array, y_array):
        # self.update_pen_color()
        self.plot_canvas.plot(
            x=x_array,
            y=y_array,
            pen=self.pen,
            connect='finite'
        )

    def update_pen_color(self):
        if self.color_counter >= len(COLORS):
            self.color_counter = 0
        # self.pen.setColor(COLORS[int(len(COLORS) - 1 & self.color_counter)])
        self.pen.setColor(COLORS[self.color_counter])
        self.color_counter += 1
        pass

    def reset_plot(self) -> None:
        self.output_text_browser.clear()
        self.color_counter = 0
        self.print_output("Plot reset")
        self.plot_canvas.clear()

        self.spinbox_Xrange_min.setValue(X_RANGE[0])
        self.spinbox_Xrange_max.setValue(X_RANGE[1])
        self.spinbox_data_points.setValue(X_DATA_POINTS)
        self.raise_flag_update_x()
        self.plot_canvas.setXRange(VIEWBOX['xmin'], VIEWBOX['xmax'], padding=0)
        self.plot_canvas.setYRange(VIEWBOX['ymin'], VIEWBOX['ymax'], padding=0)
        self.curves = []

    def on_input_change(self) -> None:
        self.input: str = self.function_input.toPlainText()
        self.input_string = self.input.replace('X', 'self.x')  # uppercase to avoid conflict with 'x' of "exp"
        self.input_string = self.input_string.replace('^', '**')
        for nth_power in {('⁰', '0'),
                          ('¹', '1'),
                          ('²', '2'),
                          ('³', '3'),
                          ('⁴', '4'),
                          ('⁵', '5'),
                          ('⁶', '6'),
                          ('⁷', '7'),
                          ('⁸', '8'),
                          ('⁹', '9')}:
            if nth_power[0] in self.input_string:
                self.input_string = self.input_string.replace(nth_power[0], '**'+nth_power[1])

    def load_curve(self):
        if DEBUG: print('loading curve')
        cv = CSVCurveLoader(None)
        self.csv_data: pd.DataFrame = cv.get_data_dataframe()
        # if DEBUG: print(f'loaded data: \n{self.csv_data}')
        if self.csv_data is not None:
            self.plot_csv()

    def plot_csv(self):
        self.csv_data: pd.DataFrame
        self.x_csv = self.csv_data.iloc[:, 0]
        self.print_output(f'Independent axis X from csv ranges from {self.x_csv.iloc[0]} to {self.x_csv.iloc[-1]}')
        for y_column in range(1,len(self.csv_data.columns)):
            self.print_output(f'    Plotting CSV curve {y_column}')
            self.y_csv = self.csv_data.iloc[:, y_column]
            self.update_pen_color()
            self.plot_xy(self.x_csv, self.y_csv)

            # TODO add legend!
    pass

# app = pg.Qt.QtGui.QApplication([])
app = QApplication([])
# app.setFont()
i = 0

window = MainWindow()
window.show()

# TODO (not urgent):
#   1) get DF from csvcurveloader.py
#   2) plot them!

if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        if DEBUG: print('Starting app')
        app.instance().exec_()
        if DEBUG: print('Quitting app')
    pass


