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

import asyncio
import csv
import logging
import math
import os
import sys
import time
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from asyncqt import QEventLoop, asyncSlot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt5 import QtCore, QtWidgets

matplotlib.use("Qt5Agg")
sns.set_theme(style="whitegrid")

COLUMNS = [
    "Vm_raman",
    "Vm_chla",
    "Vm_cdom",
    "Vm_raman_b",
    "Vm_chla_b",
    "Vm_cdom_b",
    "Raman",
    "Chla",
    "Cdom",
]


class DataHandler:
    def __init__(self, instrument, n_plots):
        n_data = 50
        self.instrument = instrument()
        self._xdata = [list(range(n_data)) for _ in range(n_plots)]
        self._ydata = [[0 for _ in range(n_data)] for _ in range(n_plots)]

        # Data saving
        data_dir = os.path.join(Path.home(), "liflidar_data")
        os.makedirs(data_dir, exist_ok=True)
        self.csv_file_path = os.path.join(data_dir, "data.csv")
        # Create the CSV file with headers if it does not exist
        if not os.path.isfile(self.csv_file_path):
            with open(self.csv_file_path, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(COLUMNS)

    # Function to append data to the CSV file
    def append_data(self, data):
        with open(self.csv_file_path, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(data)

    async def update_ydata(self):
        def _update_ydate():
            return self.instrument.measurement()

        ydata = await asyncio.get_running_loop().run_in_executor(None, _update_ydate)
        ydata = [0 if math.isnan(y) else y for y in ydata]
        self.append_data(ydata)
        combined_string = ", ".join([f"{name}: {value}" for name, value in zip(COLUMNS, ydata, strict=True)])
        logging.debug(combined_string)
        # Drop off the first y element, append a new one.
        for i, item in enumerate(ydata):
            self._ydata[i] = self._ydata[i][1:] + [item]

    def empty_axes_data(self):
        return self._xdata, self._ydata

    @property
    async def ydata(self):
        await self.update_ydata()
        return self._ydata


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, nrows=1, ncols=1):
        fig, self.axes = plt.subplots(nrows=nrows, ncols=ncols)
        super().__init__(fig)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, instrument, *args, **kwargs):
        super().__init__(*args, **kwargs)

        n_rows, n_cols = 3, 3
        n_plots = n_rows * n_cols
        self.data_handler = DataHandler(instrument, n_plots)  # get data handler instead of instrument

        self.setWindowTitle("Liflidar")
        self.setGeometry(100, 100, 800, 600)  # x pos, y pos, width, height

        self.canvas = MplCanvas(self, nrows=n_rows, ncols=n_cols)

        vbox = QtWidgets.QVBoxLayout()
        hbox = QtWidgets.QHBoxLayout()

        btn1 = QtWidgets.QPushButton("Button 1", self)
        btn2 = QtWidgets.QPushButton("Button 2", self)
        btn3 = QtWidgets.QPushButton("Button 3", self)

        # Add buttons to the horizontal layout
        hbox.addWidget(btn1)
        hbox.addWidget(btn2)
        hbox.addWidget(btn3)

        vbox.addLayout(hbox)
        vbox.addWidget(self.canvas)

        widget = QtWidgets.QWidget()
        widget.setLayout(vbox)
        self.setCentralWidget(widget)
        # self.setCentralWidget(self.canvas)

        # We need to store a reference to the plotted line
        # somewhere, so we can apply the new data to it.
        self._plot_refs = [None] * n_plots
        self.initial_plot()

        self.show()  # keep it to make maximized work
        self.showMaximized()
        # self.showFullScreen()

        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()
        self.update_flag = False

    def initial_plot(self):
        # First time we have no plot reference, so do a normal plot.
        # .plot returns a list of line <reference>s, as we're
        # only getting one we can take the first element.
        xdata, ydata = self.data_handler.empty_axes_data()
        for i, (ax, x, y, name) in enumerate(zip(self.canvas.axes.flatten(), xdata, ydata, COLUMNS, strict=True)):
            plot_ref = ax.plot(x, y, "r")
            ax.set_title(name, fontsize=13, color='blue', loc='left')
            ax.set_ylim(0, 10)
            # ax.set_aspect('equal', adjustable='box')
            self._plot_refs[i] = plot_ref[0]

    @asyncSlot()
    async def update_plot(self):
        if self.update_flag:
            return
        self.update_flag = True
        # We have a reference, we can use it to update the data for that line.

        start_time = time.perf_counter()
        ydata = await self.data_handler.ydata
        logging.debug(f"Data receiving took {time.perf_counter() - start_time:.4f}")

        start_time = time.perf_counter()
        for plot_ref, y in zip(self._plot_refs, ydata, strict=True):
            plot_ref.set_ydata(y)
        logging.debug(f"Data setting took {time.perf_counter() - start_time:.4f}")

        # Trigger the canvas to update and redraw.
        start_time = time.perf_counter()
        self.canvas.draw()
        logging.debug(f"Drawing data took {time.perf_counter() - start_time:.4f}")

        self.update_flag = False


def run_gui(instrument):
    app = QtWidgets.QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    _ = MainWindow(instrument)
    app.exec_()
