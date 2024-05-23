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
import time

import numpy as np
import pandas as pd
from ADCPi import ADCPi
from ExpanderPi import DAC


class Instrument:
    def __init__(self):
        # initaialisation DAC  //// writing (turning on and off laser)
        # set dac gain
        self.dac = DAC(2)  # -> output (0-4V)
        # set adresses for expender pi (RTC + DAC):
        # maybe default 0x68 and 0x69

        # initaialisation ADC //// Reading photodiodes
        # set adress for the ADC 8adress pin 1-4, adress pin 5-8, bit rate)
        self.adc = ADCPi(0x6A, 0x6B, 16)
        # 12 bit (240SPS max)
        # 14 bit (60SPS max)
        # 16 bit (15SPS max)
        # 18 bit (3.75SPS max)

        # set adc gain
        self.adc.set_pga(1)

        # set adc accuracy // speed
        # adc.setBitRate(16)

        # time it takes to read 3 channels on the adc (with 16bits config) (ms)
        self.read_time = 200  # to be measured
        # laser modulation frequency (Hz) (10-12Hz)
        self.f_laser = 2  # Hz
        # laser_wait = (1/f_laser)/2*1000 - read_time#(ms) T(period)/2 (s)
        self.laser_wait = 2
        # channel number photodiodes setup
        self.ch_cdom = 3
        self.ch_chla = 2
        self.ch_raman = 1

        # channel laser
        self.ch_laser = 1

        # nb measurements to be averaged for 1 observation
        self.nb_meas = 5

        # read the last calibration value
        d = pd.read_csv("configs/lidar_cal.txt", delimiter="\t")
        self.cal_chla = d.iloc[d.shape[0] - 1, [1, 2]]
        self.cal_cdom = d.iloc[d.shape[0] - 1, [3, 4]]

    def measurement(self):
        n_cycle = 0
        V_raman = []
        V_chla = []
        V_cdom = []
        V_raman_b = []
        V_chla_b = []
        V_cdom_b = []

        # date = time.strftime("%Y-%m-%d %H:%M:%S")

        # start_time = time.perf_counter()
        # while (time.perf_counter() - start_time) < Samp_int:
        while n_cycle < self.nb_meas:
            n_cycle += 1

            # turn on laser (channel, Voltage (4 is the max - maybe))
            self.dac.set_dac_voltage(1, 4)
            # wait for fluorescence to reach max
            time.sleep(self.laser_wait)
            # measure fluorescence
            V_raman += [self.adc.read_voltage(self.ch_raman)]
            V_chla += [self.adc.read_voltage(self.ch_chla)]
            V_cdom += [self.adc.read_voltage(self.ch_cdom)]

            # turn off lasser (chanel number, Voltage)
            self.dac.set_dac_voltage(1, 0)
            # wait for all fluorescence
            time.sleep(self.laser_wait)
            # measure background
            V_raman_b += [self.adc.read_voltage(self.ch_raman)]
            V_chla_b += [self.adc.read_voltage(self.ch_chla)]
            V_cdom_b += [self.adc.read_voltage(self.ch_cdom)]

        # maybe too slow, then separate the 3 channels in 3 cycles.. but then raman from different sample...

        # average values
        Vm_raman = round(np.mean(V_raman, dtype=np.float32), 5)
        Vm_chla = round(np.mean(V_chla, dtype=np.float32), 5)
        Vm_cdom = round(np.mean(V_cdom, dtype=np.float32), 5)
        Vm_raman_b = round(np.mean(V_raman_b, dtype=np.float32), 5)
        Vm_chla_b = round(np.mean(V_chla_b, dtype=np.float32), 5)
        Vm_cdom_b = round(np.mean(V_cdom_b, dtype=np.float32), 5)

        # variances
        # Va_raman = round(np.var(V_raman, dtype=np.float32), 5)
        # Va_chla = round(np.var(V_chla, dtype=np.float32), 5)
        # Va_cdom = round(np.var(V_cdom, dtype=np.float32), 5)
        # Va_raman_b = round(np.var(V_raman_b, dtype=np.float32), 5)
        # Va_chla_b = round(np.var(V_chla_b, dtype=np.float32), 5)
        # Va_cdom_b = round(np.var(V_cdom_b, dtype=np.float32), 5)

        # calculate absolute concentrations
        # chl-a, background chl- a, signal Raman, background Raman, signal CDOM, background CDOM, and estimation of:
        Raman = random.randint(0, 10)  # Vm_raman - Vm_raman_b
        Chla = random.randint(0, 10)  # self.cal_chla[0] * (np.log(Vm_chla - Vm_chla_b) / np.log(Raman)) + self.cal_chla[1]
        Cdom = random.randint(0, 10)  # self.cal_cdom[0] * ((Vm_cdom - Vm_cdom_b) / Raman) + self.cal_cdom[1]

        return Raman, Chla, Cdom

        # print & save data
        # print(
        #     date,
        #     "\t",
        #     "Raman = ",
        #     f"{Raman:.5f}",
        #     "\t",
        #     "Chla = ",
        #     f"{Chla:.5f}",
        #     "\t",
        #     "cdom = ",
        #     f"{Cdom:.5f}",
        #     "\n",
        #     "V_raman = ",
        #     f"{Vm_raman:.5f}",
        #     "\t",
        #     "V_chla = ",
        #     f"{Vm_chla:.5f}",
        #     "\t",
        #     "V_cdom = ",
        #     f"{Vm_cdom:.5f}",
        #     "\n",
        #     "V_raman_back = ",
        #     f"{Vm_raman_b:.5f}",
        #     "\t",
        #     "V_chla_back = ",
        #     f"{Vm_chla_b:.5f}",
        #     "\t",
        #     "V_cdom_back = ",
        #     f"{Vm_cdom_b:.5f}",
        #     "\n",
        # )

        # print(
        #     "Var_raman = ",
        #     f"{Va_raman:.5f}",
        #     "\t",
        #     "Var_chla = ",
        #     f"{Va_chla:.5f}",
        #     "\t",
        #     "Var_cdom = ",
        #     f"{Va_cdom:.5f}",
        #     "\n",
        #     "Var_raman_back = ",
        #     f"{Va_raman_b:.5f}",
        #     "\t",
        #     "Var_chla_back = ",
        #     f"{Va_chla_b:.5f}",
        #     "\t",
        #     "Var_cdom_back = ",
        #     f"{Va_cdom_b:.5f}",
        #     "\n",
        # )

        # fp = open("data_LIDAR.txt", "a")
        # # header = ( "date", "Raman")
        # fp.write(
        #     date
        #     + "\t"
        #     + f"{Raman:.5f}"
        #     + "\t"
        #     + f"{Chla:.5f}"
        #     + "\t"
        #     + f"{Cdom:.5f}"
        #     + "\t"
        #     + f"{Vm_raman:.5f}"
        #     + "\t"
        #     + f"{Vm_chla:.5f}"
        #     + "\t"
        #     + f"{Vm_cdom:.5f}"
        #     + "\t"
        #     + f"{Vm_raman_b:.5f}"
        #     + "\t"
        #     + f"{Vm_chla_b:.5f}"
        #     + "\t"
        #     + f"{Vm_cdom_b:.5f}"
        #     + "\t"
        #     + f"{Va_raman:.5f}"
        #     + "\t"
        #     + f"{Va_chla:.5f}"
        #     + "\t"
        #     + f"{Va_cdom:.5f}"
        #     + "\t"
        #     + f"{Va_raman_b:.5f}"
        #     + "\t"
        #     + f"{Va_chla_b:.5f}"
        #     + "\t"
        #     + f"{Va_cdom_b:.5f}"
        #     + "\n"
        # )
        # fp.close()
