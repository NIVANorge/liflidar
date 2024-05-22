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

matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg  # , NavigationToolbar2QT
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtWidgets


class DataHandler:

    def __init__(self, instrument):
        n_data = 50
        self.instrument = instrument()
        self._xdata = list(range(n_data))
        self._ydata = [0 for _ in range(n_data)]

    def update_ydata(self):
        # Drop off the first y element, append a new one.
        self._ydata = self._ydata[1:] + [random.randint(0, 10)]
    
    def empty_axes_data(self):
        return self._xdata, self._ydata
    
    @property
    def ydata(self):
        self.update_ydata()
        return self._ydata

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, instrument, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data_handler = DataHandler(instrument)

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.setCentralWidget(self.canvas)

        # We need to store a reference to the plotted line
        # somewhere, so we can apply the new data to it.
        self._plot_ref = None
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
        plot_refs = self.canvas.axes.plot(xdata, ydata, 'r')
        self._plot_ref = plot_refs[0]

    def update_plot(self):
        # We have a reference, we can use it to update the data for that line.
        self._plot_ref.set_ydata(self.data_handler.ydata)
        # Trigger the canvas to update and redraw.
        self.canvas.draw()


def run_gui(instrument):
    app = QtWidgets.QApplication(sys.argv)
    _ = MainWindow(instrument)
    app.exec_()
