
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.backend_tools import ToolBase, ToolToggleBase
from matplotlib.backend_managers import ToolManager

from datetime import datetime
import PySimpleGUI as sg
import pyautogui as pag

from gbGFuncsV2 import*
from gbGRunV2 import*
from gbBaseV2 import*
from gbGSelectV2 import*
from gbUtilsV2 import*
#from gbGRButV2 import StgToggle

class StgToggle_old(ToolToggleBase) :
        """Show lines with a given gid."""
        default_keymap = 'S'
        description = 'Show Storage Levels'
        default_toggled = True

        def __init__(self, *args, gid, flag, **kwargs):
            self.gid = gid
            self.flag = flag
            super().__init__(*args, **kwargs)

        def enable(self, *args):
            self.flag = 'Y'
            print('Have set battery to  Y   ', self.flag, rfc[pfx+'show_battery'])

        def disable(self, *args):
            self.flag = 'N'
            print('Have set battery to  N   ', self.flag, rfc[pfx+'show_battery'])


import sys
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
 
class CustomToolbar(NavigationToolbar):
    def __init__(self, canvas, parent=None):
        super(CustomToolbar, self).__init__(canvas, parent)
 
        # Add "Graph Type" drop-down menu
        graph_types = ["Line Graph", "Bar Chart", "Scatter Plot"]
        self.graph_type_combobox = QComboBox(self)
        self.graph_type_combobox.addItems(graph_types)
        self.graph_type_combobox.currentIndexChanged.connect(self._on_graph_type_selected)
        self.addWidget(self.graph_type_combobox)
 
    def _on_graph_type_selected(self):
        # Create a new graph based on the selected type from the drop-down menu
        graph_type = self.graph_type_combobox.currentText()
        fig = self.canvas.figure
        n_plots = len(fig.get_axes())
 
        for ax in fig.get_axes():
            ax.remove()
 
        # Set the subplot grid to 1 row and 1 column
        n_new_rows, n_new_cols = 1, 1
 
        if graph_type == "Line Graph":
            new_ax = fig.add_subplot(n_new_rows, n_new_cols, 1)
            new_ax.plot([1, 2, 3], [4, 2, 6], color='blue')  # Set color to blue
            new_ax.set_title('Line Graph')
 
        elif graph_type == "Bar Chart":
            new_ax = fig.add_subplot(n_new_rows, n_new_cols, 1)
            bars = new_ax.bar(['A', 'B', 'C'], [3, 7, 2], color=['red', 'green', 'blue'])  # Set colors to red, green, and blue
            new_ax.set_title('Bar Chart')
 
        elif graph_type == "Scatter Plot":
            new_ax = fig.add_subplot(n_new_rows, n_new_cols, 1)
            new_ax.scatter([1, 2, 3], [4, 2, 6], color='orange')  # Set color to orange
            new_ax.set_title('Scatter Plot')
 
        fig.canvas.draw()
 
def plot_example():
    # Create the initial figure and axis with increased figsize
    fig, ax = plt.subplots(figsize=(10, 6))
 
    # Data for the initial line graph
    x_line = [1, 2, 3, 4]
    y_line = [1, 4, 2, 3]
    ax.plot(x_line, y_line, label='Line Graph 1', color='red')  # Set color to blue
 
    # Set the title, labels, and legend for the initial plot
    ax.set_title('Line Graph 1')
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.legend()
 
    # Create a QApplication and QMainWindow for the custom toolbar
    apps = QApplication(sys.argv)
    main_window = QMainWindow()
    main_window.setWindowTitle("Custom Navigation Toolbar")
    main_window.setGeometry(100, 100, 800, 600)  # Set window size
 
    # Create the central widget and layout
    central_widget = QWidget(main_window)
    layout = QVBoxLayout(central_widget)
 
    # Create a custom toolbar with the "Graph Type" drop-down menu
    canvas = FigureCanvas(fig)
    custom_toolbar = CustomToolbar(import sys
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
 
class CustomToolbar(NavigationToolbar):
    def __init__(self, canvas, parent=None):
        super(CustomToolbar, self).__init__(canvas, parent)
 
        # Add "Graph Type" drop-down menu
        graph_types = ["Line Graph", "Bar Chart", "Scatter Plot"]
        self.graph_type_combobox = QComboBox(self)
        self.graph_type_combobox.addItems(graph_types)
        self.graph_type_combobox.currentIndexChanged.connect(self._on_graph_type_selected)
        self.addWidget(self.graph_type_combobox)
 
    def _on_graph_type_selected(self):
        # Create a new graph based on the selected type from the drop-down menu
        graph_type = self.graph_type_combobox.currentText()
        fig = self.canvas.figure
        n_plots = len(fig.get_axes())
 
        for ax in fig.get_axes():
            ax.remove()
 
        # Set the subplot grid to 1 row and 1 column
        n_new_rows, n_new_cols = 1, 1
 
        if graph_type == "Line Graph":
            new_ax = fig.add_subplot(n_new_rows, n_new_cols, 1)
            new_ax.plot([1, 2, 3], [4, 2, 6], color='blue')  # Set color to blue
            new_ax.set_title('Line Graph')
 
        elif graph_type == "Bar Chart":
            new_ax = fig.add_subplot(n_new_rows, n_new_cols, 1)
            bars = new_ax.bar(['A', 'B', 'C'], [3, 7, 2], color=['red', 'green', 'blue'])  # Set colors to red, green, and blue
            new_ax.set_title('Bar Chart')
 
        elif graph_type == "Scatter Plot":
            new_ax = fig.add_subplot(n_new_rows, n_new_cols, 1)
            new_ax.scatter([1, 2, 3], [4, 2, 6], color='orange')  # Set color to orange
            new_ax.set_title('Scatter Plot')
 
        fig.canvas.draw()
 
def plot_example():
    # Create the initial figure and axis with increased figsize
    fig, ax = plt.subplots(figsize=(10, 6))
 
    # Data for the initial line graph
    x_line = [1, 2, 3, 4]
    y_line = [1, 4, 2, 3]
    ax.plot(x_line, y_line, label='Line Graph 1', color='red')  # Set color to blue
 
    # Set the title, labels, and legend for the initial plot
    ax.set_title('Line Graph 1')
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.legend()
 
    # Create a QApplication and QMainWindow for the custom toolbar
    apps = QApplication(sys.argv)
    main_window = QMainWindow()
    main_window.setWindowTitle("Custom Navigation Toolbar")
    main_window.setGeometry(100, 100, 800, 600)  # Set window size
 
    # Create the central widget and layout
    central_widget = QWidget(main_window)
    layout = QVBoxLayout(central_widget)
 
    # Create a custom toolbar with the "Graph Type" drop-down menu
    canvas = FigureCanvas(fig)
    custom_toolbar = CustomToolbar(import sys
                                   
                                   
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
 
class CustomToolbar(NavigationToolbar):
    def __init__(self, canvas, parent=None):
        super(CustomToolbar, self).__init__(canvas, parent)
 
        # Add "Graph Type" drop-down menu
        graph_types = ["Line Graph", "Bar Chart", "Scatter Plot"]
        self.graph_type_combobox = QComboBox(self)
        self.graph_type_combobox.addItems(graph_types)
        self.graph_type_combobox.currentIndexChanged.connect(self._on_graph_type_selected)
        self.addWidget(self.graph_type_combobox)
 
    def _on_graph_type_selected(self):
        # Create a new graph based on the selected type from the drop-down menu
        graph_type = self.graph_type_combobox.currentText()
        fig = self.canvas.figure
        n_plots = len(fig.get_axes())
 
        for ax in fig.get_axes():
            ax.remove()
 
        # Set the subplot grid to 1 row and 1 column
        n_new_rows, n_new_cols = 1, 1
 
        if graph_type == "Line Graph":
            new_ax = fig.add_subplot(n_new_rows, n_new_cols, 1)
            new_ax.plot([1, 2, 3], [4, 2, 6], color='blue')  # Set color to blue
            new_ax.set_title('Line Graph')
 
        elif graph_type == "Bar Chart":
            new_ax = fig.add_subplot(n_new_rows, n_new_cols, 1)
            bars = new_ax.bar(['A', 'B', 'C'], [3, 7, 2], color=['red', 'green', 'blue'])  # Set colors to red, green, and blue
            new_ax.set_title('Bar Chart')
 
        elif graph_type == "Scatter Plot":
            new_ax = fig.add_subplot(n_new_rows, n_new_cols, 1)
            new_ax.scatter([1, 2, 3], [4, 2, 6], color='orange')  # Set color to orange
            new_ax.set_title('Scatter Plot')
 
        fig.canvas.draw()
 
def plot_example():
    # Create the initial figure and axis with increased figsize
    fig, ax = plt.subplots(figsize=(10, 6))
 
    # Data for the initial line graph
    x_line = [1, 2, 3, 4]
    y_line = [1, 4, 2, 3]
    ax.plot(x_line, y_line, label='Line Graph 1', color='red')  # Set color to blue
 
    # Set the title, labels, and legend for the initial plot
    ax.set_title('Line Graph 1')
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.legend()
 
    # Create a QApplication and QMainWindow for the custom toolbar
    apps = QApplication(sys.argv)
    main_window = QMainWindow()
    main_window.setWindowTitle("Custom Navigation Toolbar")
    main_window.setGeometry(100, 100, 800, 600)  # Set window size
 
    # Create the central widget and layout
    central_widget = QWidget(main_window)
    layout = QVBoxLayout(central_widget)
 
    # Create a custom toolbar with the "Graph Type" drop-down menu
    canvas = FigureCanvas(fig)
    custom_toolbar = CustomToolbar(canvas, main_window)
    layout.addWidget(canvas)
    layout.addWidget(custom_toolbar)
 
    # Set the central widget and show the main window
    main_window.setCentralWidget(central_widget)
    main_window.show()
 
    # Run the Qt event loop
    sys.exit(apps.exec_())
 
# Call the function to create and show the plot with the custom toolbar
plot_example(), main_window)
    layout.addWidget(canvas)
    layout.addWidget(custom_toolbar)
 
    # Set the central widget and show the main window
    main_window.setCentralWidget(central_widget)
    main_window.show()
 
    # Run the Qt event loop
    sys.exit(apps.exec_())
 
# Call the function to create and show the plot with the custom toolbar
plot_example(), main_window)
    layout.addWidget(canvas)
    layout.addWidget(custom_toolbar)
 
    # Set the central widget and show the main window
    main_window.setCentralWidget(central_widget)
    main_window.show()
 
    # Run the Qt event loop
    sys.exit(apps.exec_())
 
# Call the function to create and show the plot with the custom toolbar
plot_example()