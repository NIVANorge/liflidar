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
import logging
import os
import struct
import sys
from datetime import datetime

import numpy as np
import pandas as pd
import pyqtgraph as pg
import serial
import serial.tools.list_ports
from ADCDifferentialPi import ADCDifferentialPi
from asyncqt import QEventLoop, asyncClose, asyncSlot
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QTabWidget,
    QTextEdit,
    QWidget,
)

fbox = {
    "salinity": 33.5,
    "temperature": 25.0,
    "longitude": 0.0,
    "latitude": 0.0,
    "pumping": None,
    'udp_ok': False
}


class TimeAxisItem(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        return [datetime.fromtimestamp(value) for value in values]


class testconnection:
    def __init__(self):
        pass

    def read(self,val):
        return b'\x07'

    def flushInput(self):
        pass


class pco2_instrument:
    def __init__(self, base_folderpath, panelargs):
        ports = list(serial.tools.list_ports.comports())
        # self.args = panelargs
        # if not self.args.localdev:
        # self.port = ports[0]

        self.base_folderpath = base_folderpath
        self.path = self.base_folderpath + "/data_pCO2/"

        self.co2 = 990
        self.co2_temp = 999
        self.buff = None
        # self.serial_data = pd.DataFrame

        # if not os.path.exists(self.path):
        #     os.mkdir(self.path)

        # try:
        #     # PJA: override self.port.device to serial0
        #     self.connection = serial.Serial(
        #         "/dev/serial0",
        #         baudrate=115200,
        #         timeout=5,
        #         parity=serial.PARITY_NONE,
        #         stopbits=serial.STOPBITS_ONE,
        #         bytesize=serial.EIGHTBITS,
        #         rtscts=False,
        #         dsrdtr=False,
        #         xonxoff=False,
        #     )
        #     # logging.debug(self.connection)
        # except:
        #     logging.debug("Was not able to find connection to the instrument")
        self.connection = None

        # f = config_file["pCO2"]

        # self.ship_code = config_file["Operational"]["Ship_Code"]
        # self.ppco2_string_version = f["PPCO2_STRING_VERSION"]

    async def save_pCO2_data(self, data, values):
        data["time"] = data["time"].dt.strftime("%Y%m%d_%H%M%S")

        columns1 = list(data.columns)
        row = list(data.iloc[0])

        logfile = os.path.join(self.path, "pCO2.log")
        columns2 = ["Lon", "Lat", "fb_temp", "fb_sal", "Tw", "Ta_mem", "Qw", "Pw", "Pa_env", "Ta_env"]
        columnss = columns1 + columns2

        self.pco2_df = pd.DataFrame(columns=columnss)
        pco2_row = row + [fbox["longitude"], fbox["latitude"], fbox["temperature"], fbox["salinity"]] + values

        self.pco2_df.loc[0] = pco2_row
        logging.debug("Saving pco2 data")

        if not os.path.exists(logfile):
            self.pco2_df.to_csv(logfile, index=False, header=True)
        else:
            self.pco2_df.to_csv(logfile, mode="a", index=False, header=False)

        return self.pco2_df


class test_pco2_instrument(pco2_instrument):
    def __init__(self, base_folderpath='', panelargs=''):
        super().__init__(base_folderpath, panelargs)

        self.connection = testconnection()
        print (self.connection)

    def get_Voltage(self, nAver, channel):
        v = 0
        for i in range(nAver):
            v += 0.6
        return v / nAver

    def close(self):
        print ('close connection, localtest')
        logging.debug('close connection, localtest')


# class only_pco2_instrument(pco2_instrument):
#     # Class for communication with Raspberry PI for the only pco2 case
#     def __init__(self, base_folderpath, panelargs):
#         super().__init__(base_folderpath, panelargs)
#         self.adc = ADCDifferentialPi(0x68, 0x69, 14)
#         self.adc.set_pga(1)
# 
#     def get_Voltage(self, nAver, channel):
#         v = 0.0000
#         for i in range(nAver):
#             v += self.adc.read_voltage(channel)
#         Voltage = round(v / nAver, prec["Voltage"])
#         # PJA 2021-04-16: to debug temperature values
#         # print("AI Channel {:-d}: {:5.2f}V".format(channel, Voltage))
#         return Voltage


class tab_pco2_class(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()

        groupbox = QGroupBox("Updates from pCO2")
        self.group_layout = QGridLayout()
        layout = QGridLayout()

        self.Tw_pco2_live = QLineEdit()
        self.Ta_mem_pco2_live = QLineEdit()
        self.Qw_pco2_live = QLineEdit()
        self.Pw_pco2_live = QLineEdit()
        self.Pa_env_pco2_live = QLineEdit()
        self.Ta_env_pco2_live = QLineEdit()
        self.CO2_pco2_live = QLineEdit()
        self.VP_Vout_live = QLineEdit()
        self.VT_Vout_live = QLineEdit()

        self.fbox_temp_live = QLineEdit()
        self.fbox_sal_live = QLineEdit()

        self.pco2_params = [
            self.Tw_pco2_live,
            self.Ta_mem_pco2_live,
            self.Qw_pco2_live,
            self.Pw_pco2_live,
            self.Pa_env_pco2_live,
            self.Ta_env_pco2_live,
            self.VP_Vout_live,
            self.VT_Vout_live,
            self.CO2_pco2_live,
        ]

        self.pco2_labels = [
            "Water_temperature",
            "Air_Temperature_membr",
            "Water_Flow",
            "Water_Pressure",
            "Air_Pressure_env",
            "Air_Temperature_env",
            "VP_Vout_live",
            "VT_Vout_live",
            "C02_ppm",
        ]

        # self.rbtns[0].setChecked(True)
        self.parameter_to_plot = "Water_temperature"
        [layout.addWidget(self.pco2_params[n], n, 1) for n in range(len(self.pco2_params))]
        [layout.addWidget(QLabel(self.pco2_labels[n]), n, 0) for n in range(len(self.pco2_params))]

        # layout.addWidget(QLabel(self.pco2_labels[-1]), 8, 0)
        layout.addWidget(QLabel("fbox_temp"), 9, 0)
        layout.addWidget(QLabel("fbox_sal"), 10, 0)
        layout.addWidget(self.fbox_temp_live, 9, 1)
        layout.addWidget(self.fbox_sal_live, 10, 1)

        # layout.addWidget(QLabel(self.pco2_labels[-3]), 6, 0)
        # layout.addWidget(QLabel(self.pco2_labels[-2]), 7, 0)
        groupbox.setLayout(layout)
        self.group_layout.addWidget(groupbox, 0, 0, 1, 2)

    def onClicked_radio(self):
        radioBtn = self.sender()

        if radioBtn.isChecked():
            self.parameter_to_plot = radioBtn.text()

    async def update_tab_ai_values(self, values):
        all_val = values
        [self.pco2_params[n].setText(str(all_val[n])) for n in range(len(values))]
        self.fbox_temp_live.setText(str(fbox["temperature"]))
        self.fbox_sal_live.setText(str(fbox["salinity"]))

    async def update_tab_serial_values(self, data):
        all_val = [data["VP"].values[0], data["VT"].values[0], data["ppm"].values[0]]
        [self.pco2_params[n].setText(str(v)) for n, v in enumerate(all_val, start=6)]


class Panel(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.measuring = False

        self.pco2_timeseries = pd.DataFrame(
            columns=[
                "times",
                "CO2_values",
                "Water_temperature",
                "Air_Temperature_membr",
                "Water_Pressure",
                "Air_Pressure_env",
                "Water_Flow",
                "Air_Temperature_env",
                "VP_Vout_live",
                "VT_Vout_live",
                "fbox_temp",
                "fbox_sal",
            ]
        )

        self.pco2_instrument = test_pco2_instrument()

        self.tabs = QTabWidget()
        self.tab_pco2 = tab_pco2_class()
        # self.tab_pco2_calibration = QWidget()
        self.tab_pco2_config = QWidget()

        layout = QGridLayout()
        self.clear_plot_btn = QPushButton("Clear plot")
        self.clear_plot_btn.clicked.connect(self.clear_plot_btn_clicked)
        layout.addWidget(self.clear_plot_btn)
        self.tab_pco2_config.setLayout(layout)

        self.tabs.addTab(self.tab_pco2, "pCO2")
        # self.tabs.addTab(self.tab_pco2_calibration, "Calibrate")
        self.tabs.addTab(self.tab_pco2_config, "Config")

        # self.make_tab_pco2_calibration()

        self.make_tab_plotwidget()
        hboxPanel = QGridLayout()
        hboxPanel.addWidget(self.plotwidget_pco2, 0, 0)
        hboxPanel.addWidget(self.plotwidget_var, 1, 0)
        hboxPanel.addWidget(self.plotwidget_var2, 2, 0)
        hboxPanel.addWidget(self.tabs, 0, 1, 3, 1)

        self.timerSave_pco2 = QtCore.QTimer()
        self.timerSave_pco2.timeout.connect(self.timer_finished)

        self.btn_measure = QPushButton("Measure")
        self.btn_measure.setCheckable(True)
        self.btn_measure.clicked[bool].connect(self.btn_measure_clicked)

        self.btn_measure_once = QPushButton("Measure Once")
        self.btn_measure_once.setCheckable(True)
        self.btn_measure_once.clicked[bool].connect(self.btn_measure_once_clicked)

        self.StatusBox = QTextEdit()
        self.StatusBox.setReadOnly(True)

        self.plotvar1_combo = QComboBox()
        [self.plotvar1_combo.addItem(str(item)) for item in self.tab_pco2.pco2_labels[:-1] + ["fbox_temp", "fbox_sal"]]
        self.plotvar2_combo = QComboBox()
        [self.plotvar2_combo.addItem(str(item)) for item in self.tab_pco2.pco2_labels[:-1] + ["fbox_temp", "fbox_sal"]]

        self.tab_pco2.group_layout.addWidget(QLabel("plot 2"), 1, 0)
        self.tab_pco2.group_layout.addWidget(self.plotvar1_combo, 1, 1)

        self.tab_pco2.group_layout.addWidget(QLabel("plot 3"), 2, 0)
        self.tab_pco2.group_layout.addWidget(self.plotvar2_combo, 2, 1)

        self.tab_pco2.group_layout.addWidget(self.btn_measure, 3, 0)
        self.tab_pco2.group_layout.addWidget(self.btn_measure_once, 3, 1)
        self.tab_pco2.group_layout.addWidget(self.StatusBox, 4, 0, 1, 1)

        self.no_serial = QPushButton("Ignore Serial Connection")
        self.no_serial.setCheckable(True)
        self.no_serial.setChecked(False)

        self.tab_pco2.group_layout.addWidget(self.no_serial, 4, 1, 1, 1)
        self.tab_pco2.setLayout(self.tab_pco2.group_layout)

        self.setLayout(hboxPanel)

    def close(self):
        self.pco2_instrument.connection.close()

    def valve_message(self, type="Confirm Exit"):
        msg = QMessageBox()

        image = "utils/pHox_question.png"

        pixmap = QPixmap(QPixmap(image)).scaledToHeight(100, QtCore.Qt.SmoothTransformation)

        msg.setIconPixmap(pixmap)
        msg.setWindowIcon(QIcon("utils/pHox_logo.png"))

        msg.setWindowTitle("Important")
        msg.setText("Are you sure you want to exit ?")

        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        return msg.exec_()

    @asyncSlot()
    async def btn_measure_once_clicked(self):
        self.btn_measure.setEnabled(False)
        await self.update_data()
        self.btn_measure.setEnabled(True)

    def btn_measure_clicked(self):
        if self.btn_measure.isChecked():
            self.btn_measure_once.setEnabled(False)
            interval = 1  # int(config_file["pCO2"]["interval"])
            self.timerSave_pco2.start(interval * 1000)
        else:
            self.btn_measure_once.setEnabled(True)
            self.timerSave_pco2.stop()

    def clear_plot_btn_clicked(self):
        self.pco2_timeseries = pd.DataFrame(columns=self.pco2_timeseries.columns)

    def make_tab_plotwidget(self):
        date_axis = TimeAxisItem(orientation="bottom")
        date_axis2 = TimeAxisItem(orientation="bottom")
        date_axis3 = TimeAxisItem(orientation="bottom")

        self.plotwidget_pco2 = pg.PlotWidget(axisItems={"bottom": date_axis})
        self.plotwidget_var = pg.PlotWidget(axisItems={"bottom": date_axis2})
        self.plotwidget_var2 = pg.PlotWidget(axisItems={"bottom": date_axis3})

        self.plotwidget_pco2.setMouseEnabled(x=False, y=False)
        self.plotwidget_var.setMouseEnabled(x=False, y=False)
        self.plotwidget_var2.setMouseEnabled(x=False, y=False)

        self.plotwidget_line2 = self.plotwidget_var2.plot()
        self.plotwidget_line2_avg = self.plotwidget_var2.plot()

        self.plotwidget_line = self.plotwidget_var.plot()
        self.plotwidget_line_avg = self.plotwidget_var.plot()

        self.pco2_data_line = self.plotwidget_pco2.plot()
        self.pco2_data_averaged_line = self.plotwidget_pco2.plot()

        self.plotwidget_pco2.setBackground("#19232D")
        self.plotwidget_pco2.showGrid(x=True, y=True)
        self.plotwidget_pco2.setTitle("pCO2 value time series")

        self.plotwidget_var.setBackground("#19232D")
        self.plotwidget_var.showGrid(x=True, y=True)
        self.plotwidget_var2.setBackground("#19232D")
        self.plotwidget_var2.showGrid(x=True, y=True)

        self.pen = pg.mkPen(width=0.3, style=QtCore.Qt.DashLine)
        self.pen_avg = pg.mkPen(width=0.7)
        self.symbolSize = 5

    # def make_tab_pco2_calibration(self):
    #     layout = QGridLayout()
    #     self.btns = [QPushButton("Point 1"), QPushButton("Point 2"), QPushButton("Point 3"), QPushButton("Point 4")]

    #     [layout.addWidget(v, k, 0) for k, v in enumerate(self.btns)]

    #     self.tab_pco2_calibration.setLayout(layout)

    def get_value_pco2_from_voltage(self, type):
        # channel = config_file["pCO2"][type]["Channel"]
        # coef = config_file["pCO2"][type]["Calibr"]
        # if self.args.localdev:
        x = np.random.randint(0, 100)
        # else:
        #     try:
        #         v = self.pco2_instrument.get_Voltage(2, channel)
        #         x = coef[0] * v + coef[1]
        #         x = round(x, 3)
        #     except Exception as e:
        #         print(e)
        #         x = -999
        return x

    @asyncSlot()
    async def timer_finished(self):
        if self.btn_measure.isChecked():
            if not self.measuring:
                await self.update_data()
            else:
                print("Skipping", datetime.now())
        else:
            self.timerSave_pco2.stop()

    async def update_data(self):
        self.measuring = True
        start = datetime.now()
        # UPDATE VALUES
        self.wat_temp = self.get_value_pco2_from_voltage(type="Tw")
        self.air_temp_mem = self.get_value_pco2_from_voltage(type="Ta_mem")
        self.wat_flow = self.get_value_pco2_from_voltage(type="Qw")
        self.wat_pres = self.get_value_pco2_from_voltage(type="Pw")
        self.air_pres = self.get_value_pco2_from_voltage(type="Pa_env")
        self.air_temp_env = self.get_value_pco2_from_voltage(type="Ta_env")

        values = [self.wat_temp, self.air_temp_mem, self.wat_flow, self.wat_pres, self.air_pres, self.air_temp_env]
        await self.tab_pco2.update_tab_ai_values(values)

        # F = False
        # if measure_co2:
        if not self.no_serial.isChecked():
            synced_serial = await self.get_pco2_values()
            if synced_serial:
                await self.tab_pco2.update_tab_serial_values(self.serial_data)
                await asyncio.sleep(0.0001)
                self.pco2_df = await self.update_pco2_plot()
                # await self.pco2_instrument.save_pCO2_data(self.serial_data, values)
                # await self.send_pco2_to_ferrybox()

            else:
                self.StatusBox.setText("Could not measure using serial connection")
                self.no_serial.setChecked(True)
        else:
            self.serial_data = pd.DataFrame(
                data={
                    "time": ["nan"],
                    "timestamp": ["nan"],
                    "ppm": ["nan"],
                    "type": ["nan"],
                    "range": ["nan"],
                    "sn": ["nan"],
                    "VP": ["nan"],
                    "VT": ["nan"],
                    "mode": ["nan"],
                }
            )

            self.serial_data["time"] = datetime.now()
            d = datetime.now().timestamp()
            self.serial_data["timestamp"] = [d]

            # await self.pco2_instrument.save_pCO2_data(self.serial_data, values)

        self.measuring = False
        # print ('measurement took', datetime.now() - start)

    async def sync_pco2(self):
        self.StatusBox.setText("Reading data from the serial")
        await asyncio.sleep(0.001)
        print(self.pco2_instrument.connection, "before")
        self.pco2_instrument.connection.flushInput()
        print(self.pco2_instrument.connection, "after")
        for n in range(100):
            if not self.btn_measure.isChecked() and not self.btn_measure_once.isChecked():
                return
            b = self.pco2_instrument.connection.read(1)
            print(b)
            if len(b) and (b[0] == b"\x07"[0]):
                return True
            if n > 2 and b == b"":
                return False
            if n == 99:
                return False

    async def get_pco2_values(self):
        self.serial_data = pd.DataFrame(columns=["time", "timestamp", "ppm", "type", "range", "sn", "VP", "VT", "mode"])

        self.serial_data["time"] = datetime.now()
        d = datetime.now().timestamp()
        self.serial_data["timestamp"] = [d]

        synced = await self.sync_pco2()  # False

        if synced:
            # if self.args.localdev:
            self.serial_data["CH1_Vout"] = 999
            import random

            self.serial_data["ppm"] = random.randint(400, 500)
            self.serial_data["raw_ppm"] = random.randint(400, 500)
            self.serial_data["type"] = 999
            self.serial_data["range"] = 999
            self.serial_data["sn"] = 999
            self.serial_data["VP"] = 999
            self.serial_data["VT"] = 999
            self.serial_data["mode"] = 999
            # else:
            #     try:
            #         # self.StatusBox.setText('Trying to read data')
            #         self.buff = self.pco2_instrument.connection.read(37)

            #         self.serial_data["CH1_Vout"] = struct.unpack("<f", self.buff[0:4])[0]

            #         self.serial_data["ppm"] = struct.unpack("<f", self.buff[4:8])[0]
            #         self.serial_data["raw_ppm"] = self.serial_data["ppm"]
            #         self.serial_data["ppm"] = self.serial_data["ppm"] * float(self.Co2_CalCoef[0]) + float(
            #             self.Co2_CalCoef[1]
            #         )

            #         self.serial_data["type"] = self.buff[8:9]
            #         self.serial_data["range"] = struct.unpack("<f", self.buff[9:13])[0]
            #         self.serial_data["sn"] = self.buff[13:27]
            #         self.serial_data["VP"] = struct.unpack("<f", self.buff[27:31])[0]
            #         self.serial_data["VT"] = struct.unpack("<f", self.buff[31:35])[0]
            #         self.serial_data["mode"] = self.buff[35:36]
            #         self.StatusBox.setText("Updated pco2 instrument values")
            #         await asyncio.sleep(0.001)
            #         if self.buff[8:9][0] != b"\x81"[0]:
            #             print("the gas type is not correct")
            #             synced = False
            #         # if self.serial_data['mode'][0] != b'\x80'[0]:
            #         #    raise ValueError('the detector mode is not correct')
            #     except:
            #         raise
            self.serial_data = self.serial_data.round({"CH1_Vout": 3, "ppm": 3, "range": 3, "VP": 3, "VT": 3})
        else:
            synced = False
            # raise ValueError('cannot sync to CO2 detector')
        if self.btn_measure_once.isChecked():
            self.btn_measure_once.setChecked(False)

        return synced

    # async def send_pco2_to_ferrybox(self):
    #     row_to_string = self.pco2_df.to_csv(index=False, header=False).rstrip()
    #     # TODO: add pco2 string version
    #     v = self.pco2_instrument.ppco2_string_version
    #     # udp.send_data("$PPCO2," + row_to_string + ",*\n", self.pco2_instrument.ship_code)

    async def update_pco2_plot(self):
        # UPDATE PLOT WIDGETS
        # only pco2 plot

        length = len(self.pco2_timeseries["times"])
        time_limit = 7000  # config_file["pCO2"]["timeaxis_limit"]

        self.par1_to_plot = self.plotvar1_combo.currentText()
        self.par2_to_plot = self.plotvar2_combo.currentText()

        self.plotwidget_var.setTitle(self.par1_to_plot)
        self.plotwidget_var2.setTitle(self.par2_to_plot)
        await asyncio.sleep(0.001)

        if length == 300:
            self.pen = pg.mkPen(None)
            self.symbolSize = 2

        if length > time_limit:
            self.pco2_timeseries = self.pco2_timeseries.drop([0], axis=0).reset_index(drop=True)

        row = [
            self.serial_data["timestamp"].values[0],
            self.serial_data["ppm"].values[0],
            self.wat_temp,
            self.air_temp_mem,
            self.wat_pres,
            self.air_pres,
            self.wat_flow,
            self.air_temp_env,
            self.serial_data["VP"].values,
            self.serial_data["VT"].values,
            fbox["temperature"],
            fbox["salinity"],
        ]

        # add one row with all values
        self.pco2_timeseries.loc[length] = row

        for n in [self.plotwidget_pco2, self.plotwidget_var, self.plotwidget_var2]:
            n.setXRange(self.pco2_timeseries["times"].values[0], self.pco2_timeseries["times"].values[-1])

        self.plotwidget_var2.setYRange(
            np.min(self.pco2_timeseries[self.par2_to_plot].values) - 0.001,
            np.max(self.pco2_timeseries[self.par2_to_plot].values) + 0.001,
        )
        self.plotwidget_var.setYRange(
            np.min(self.pco2_timeseries[self.par1_to_plot].values) - 0.001,
            np.max(self.pco2_timeseries[self.par1_to_plot].values) + 0.001,
        )

        self.pco2_data_line.setData(
            self.pco2_timeseries["times"].values,
            self.pco2_timeseries["CO2_values"].values,
            symbolBrush="w",
            alpha=0.3,
            size=1,
            symbol="o",
            symbolSize=1,
            pen=self.pen,
        )

        self.plotwidget_line.setData(
            self.pco2_timeseries["times"],
            self.pco2_timeseries[self.par1_to_plot],
            symbolBrush="w",
            alpha=0.3,
            size=1,
            symbol="o",
            symbolSize=1,
            pen=self.pen,
        )

        self.plotwidget_line2.setData(
            self.pco2_timeseries["times"],
            self.pco2_timeseries[self.par2_to_plot],
            symbolBrush="w",
            alpha=0.3,
            size=1,
            symbol="o",
            symbolSize=1,
            pen=self.pen,
        )

        if self.par1_to_plot == self.par2_to_plot:
            subset = self.pco2_timeseries[["times", "CO2_values", self.par1_to_plot]]
        else:
            subset = self.pco2_timeseries[["times", "CO2_values", self.par1_to_plot, self.par2_to_plot]]
        subset.set_index("times", inplace=True)

        self.pco2_timeseries_averaged = subset.rolling(10).mean().dropna()
        # print (self.pco2_timeseries_averaged)
        self.pco2_data_averaged_line.setData(
            self.pco2_timeseries_averaged.index.values,
            self.pco2_timeseries_averaged["CO2_values"].values,
            symbolBrush="y",
            alpha=0.5,
            size=2,
            symbol="o",
            symbolSize=self.symbolSize,
            pen=self.pen_avg,
        )

        self.plotwidget_line_avg.setData(
            self.pco2_timeseries_averaged.index.values,
            self.pco2_timeseries_averaged[self.par1_to_plot].values,
            symbolBrush="y",
            alpha=0.5,
            size=2,
            symbol="o",
            symbolSize=self.symbolSize,
            pen=self.pen_avg,
        )

        self.plotwidget_line2_avg.setData(
            self.pco2_timeseries_averaged.index.values,
            self.pco2_timeseries_averaged[self.par2_to_plot].values,
            symbolBrush="y",
            alpha=0.5,
            size=2,
            symbol="o",
            symbolSize=self.symbolSize,
            pen=self.pen_avg,
        )

    # def autorun(self):
    #     if self.args.noserial:
    #         self.no_serial.setChecked(True)
    #     self.btn_measure.setChecked(True)

    #     if fbox["pumping"] or fbox["pumping"] is None:
    #         self.btn_measure_clicked()


class boxUI(QMainWindow):
    def __init__(self, loop, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("Liflidar")
        self.main_widget = Panel(self)
        self.setCentralWidget(self.main_widget)

        self.showMaximized()
        # self.main_widget.autorun()

        with loop:
            sys.exit(loop.run_forever())

    def closeEvent(self, event):
        result = self.main_widget.valve_message("Confirm Exit")
        event.ignore()

        if result == QMessageBox.Yes:
            logging.info("The program was closed by user")

            self.main_widget.timerSave_pco2.stop()
            self.main_widget.btn_measure.setChecked(False)
            self.main_widget.close()
            QApplication.quit()
            sys.exit()


def run_gui(instrument):
    app = QApplication(sys.argv)

    with open("configs/styles.qss") as file:
        qss_file = file.read()
    app.setStyleSheet(qss_file)

    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    asyncio.events._set_running_loop(loop)
    boxUI(loop)
    app.exec()
