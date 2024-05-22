# Copyright 2024 The Liflidar Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QMainWindow, QPushButton, QWidget

# from pyqtgraph import PlotWidget


# Define the main window class
class GraphInterface(QMainWindow):
    def init(self):
        super().init()

        self.setWindowTitle("Graph Interface")
        self.setGeometry(100, 100, 800, 600)  # Adjust size and position as needed

        # Central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        grid_layout = QGridLayout(central_widget)

        # Creating a 3x3 grid of placeholder widgets for the graphs
        for row in range(3):
            for col in range(3):
                graph_label = QLabel(f"Graph {row * 3 + col + 1}")  # Placeholder label
                graph_label.setStyleSheet("QLabel { background-color : white; border: 1px solid black; }")
                graph_label.setAlignment(Qt.AlignCenter)
                grid_layout.addWidget(graph_label, row, col)
                
                # In a real application, you would use a PlotWidget from pyqtgraph here instead of QLabel
                # graph_widget = PlotWidget()
                # grid_layout.addWidget(graph_widget, row, col)

        # Adding labels and buttons to the layout
        # On/Off labels and buttons at the top of each column
        on_off_labels = [QLabel("CN/OF"), QLabel("Laser ON/OFF"), QLabel("Sampling Interval Fast Only")]
        for i, label in enumerate(on_off_labels):
            label.setAlignment(Qt.AlignCenter)
            grid_layout.addWidget(label, 0, i, 1, 1)
            # Adding buttons right below the labels
            button = QPushButton("Toggle")
            grid_layout.addWidget(button, 1, i, 1, 1)

        # Dev mode label and button on the right side of the grid
        dev_mode_label = QLabel("Dev mode only")
        dev_mode_label.setAlignment(Qt.AlignCenter)
        grid_layout.addWidget(dev_mode_label, 0, 3, 1, 1)
        dev_mode_button = QPushButton("Toggle")
        grid_layout.addWidget(dev_mode_button, 1, 3, 1, 1)

# Note: The above code should be run in a Python environment with PyQt5 and optionally pyqtgraph installed.
# The buttons and graph widgets are placeholders and need to be connected to the appropriate event handlers
# to perform actual actions in a real application.


def run_gui(instrument):
    app = QApplication([])
    window = GraphInterface(instrument)
    window.show()
    app.exec()
