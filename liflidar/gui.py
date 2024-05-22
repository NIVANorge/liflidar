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

import random
import sys

import matplotlib

matplotlib.use("Qt5Agg")

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg  # , NavigationToolbar2QT
from PyQt5 import QtCore, QtWidgets


class DataHandler:
    def __init__(self, instrument):
        n_plots = 2
        n_data = 50
        self.instrument = instrument()
        self._xdata = [list(range(n_data)) for _ in range(n_plots)]
        self._ydata = [[0 for _ in range(n_data)] for _ in range(n_plots)]

    def update_ydata(self):
        # Drop off the first y element, append a new one.
        for i in range(len(self._ydata)):
            self._ydata[i] = self._ydata[i][1:] + [random.randint(0, 10)]

    def empty_axes_data(self):
        return self._xdata, self._ydata

    @property
    def ydata(self):
        self.update_ydata()
        return self._ydata


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=20, height=7, dpi=300):
        fig, self.axes = plt.subplots(nrows=1, ncols=2, figsize=(width, height))  # , dpi=dpi)
        super().__init__(fig)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, instrument, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data_handler = DataHandler(instrument)  # get data handler instead of instrument

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.setCentralWidget(self.canvas)

        # We need to store a reference to the plotted line
        # somewhere, so we can apply the new data to it.
        self._plot_refs = [None, None]
        self.initial_plot()
        self.show()

        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def initial_plot(self):
        # First time we have no plot reference, so do a normal plot.
        # .plot returns a list of line <reference>s, as we're
        # only getting one we can take the first element.
        xdata, ydata = self.data_handler.empty_axes_data()
        for i, (ax, x, y) in enumerate(zip(self.canvas.axes, xdata, ydata, strict=True)):
            plot_ref = ax.plot(x, y, "r")
            self._plot_refs[i] = plot_ref[0]

    def update_plot(self):
        # We have a reference, we can use it to update the data for that line.
        for plot_ref, ydata in zip(self._plot_refs, self.data_handler.ydata, strict=True):
            plot_ref.set_ydata(ydata)
        # Trigger the canvas to update and redraw.
        self.canvas.draw()


def run_gui(instrument):
    app = QtWidgets.QApplication(sys.argv)
    _ = MainWindow(instrument)
    app.exec_()
