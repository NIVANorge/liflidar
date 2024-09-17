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

import time
from datetime import datetime

import numpy as np
import pandas as pd
#from ADCPi import ADCPi
from ExpanderPi import DAC
from ExpanderPi import ADC

class Instrument:
    def __init__(self):
        # initaialisation DAC  //// writing (turning on and off laser)
        # set dac gain
        self.dac = DAC(2)  # -> output (0-4V)
        # set adresses for expender pi (RTC + DAC):
        # maybe default 0x68 and 0x69

        # initaialisation ADC //// Reading photodiodes
        # set adress for the ADC 8adress pin 1-4, adress pin 5-8, bit rate)
        #self.adc = ADCPi(0x6A, 0x6B, 12)
        # 12 bit (240SPS max)
        # 14 bit (60SPS max)
        # 16 bit (15SPS max)
        # 18 bit (3.75SPS max)
        # set adc gain
        #self.adc.set_pga(1)
        
        ### using pi expender 
        self.adc = ADC()
        # set adc accuracy // speed
        # adc.setBitRate(16)

        # time it takes to read 3 channels on the adc (with 16bits config) (ms)
        self.read_time = 0.02  # to be measured
        # laser modulation frequency (Hz) (10-12Hz)
        self.f_laser = 5  # Hz
        #self.laser_wait = (1 / self.f_laser) / 2 - self.read_time  # (ms) T(period)/2 (s)
        self.laser_wait = 0.1
        print(f" wait laser: {self.laser_wait}")

        # self.laser_wait = 0
        # channel number photodiodes setup
        self.ch_cdom = 5
        self.ch_chla = 8
        self.ch_raman = 1

        # channel laser
        self.ch_laser = 1

        # nb cycles ON/OFF laser to be averaged for 1 observation
        self.nb_cycle = 5
        # nb measurements to be averaged inside each ON and OFF of a cycle
        self.nb_meas = 3

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

        # date = time.strftime("%Y-%m-%d %H:%M:%S.%f")
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        while n_cycle < self.nb_cycle:
            start_time = time.perf_counter()
            n_cycle += 1

            # turn on laser (channel, Voltage (4 is the max - maybe))
            self.dac.set_dac_voltage(1, 4)
            # wait for fluorescence to reach max
            time.sleep(self.laser_wait)
            # measure fluorescence
            n_meas = 0
            while n_meas < self.nb_meas:
                n_meas += 1
                V_raman += [self.adc.read_adc_voltage(self.ch_raman,0)]
            n_meas = 0
            while n_meas < self.nb_meas:
                n_meas += 1
                V_chla += [self.adc.read_adc_voltage(self.ch_chla,0)]
            n_meas = 0
            while n_meas < self.nb_meas:
                n_meas += 1
                V_cdom += [self.adc.read_adc_voltage(self.ch_cdom,0)]

            # turn off lasser (chanel number, Voltage)
            self.dac.set_dac_voltage(1, 0)
            # wait for all fluorescence to disapear
            time.sleep(self.laser_wait)
            # measure background
            n_meas = 0
            while n_meas < self.nb_meas:
                n_meas += 1
                V_raman_b += [self.adc.read_adc_voltage(self.ch_raman,0)]
            n_meas = 0
            while n_meas < self.nb_meas:
                n_meas += 1
                V_chla_b += [self.adc.read_adc_voltage(self.ch_chla,0)]
            n_meas = 0
            while n_meas < self.nb_meas:
                n_meas += 1
                #start_read = time.perf_counter()
                V_cdom_b += [self.adc.read_adc_voltage(self.ch_cdom,0)]
                #print(f"A read: {time.perf_counter() - start_read}")
                
            print(f"A loop: {time.perf_counter() - start_time}")

        # average values
        #Vm_raman = round(np.mean(V_raman, dtype=np.float32), 5)
        #Vm_chla = round(np.mean(V_chla, dtype=np.float32), 5)
        #Vm_cdom = round(np.mean(V_cdom, dtype=np.float32), 5)
        #Vm_raman_b = round(np.mean(V_raman_b, dtype=np.float32), 5)
        #Vm_chla_b = round(np.mean(V_chla_b, dtype=np.float32), 5)
        #Vm_cdom_b = round(np.mean(V_cdom_b, dtype=np.float32), 5)
        
        Vm_raman = round(np.median(V_raman), 5)
        Vm_chla = round(np.median(V_chla), 5)
        Vm_cdom = round(np.median(V_cdom), 5)
        Vm_raman_b = round(np.median(V_raman_b), 5)
        Vm_chla_b = round(np.median(V_chla_b), 5)
        Vm_cdom_b = round(np.median(V_cdom_b), 5)
        
        print(f"V raman: {V_raman}")
        print(f"V cdom: {V_cdom}")
        print(f"V Chla: {V_chla}")
        # variances
        # Va_raman = round(np.var(V_raman, dtype=np.float32), 5)
        # Va_chla = round(np.var(V_chla, dtype=np.float32), 5)
        # Va_cdom = round(np.var(V_cdom, dtype=np.float32), 5)
        # Va_raman_b = round(np.var(V_raman_b, dtype=np.float32), 5)
        # Va_chla_b = round(np.var(V_chla_b, dtype=np.float32), 5)
        # Va_cdom_b = round(np.var(V_cdom_b, dtype=np.float32), 5)

        # calculate absolute concentrations
        # chl-a, background chl- a, signal Raman, background Raman, signal CDOM, background CDOM, and estimation of:
        Raman = Vm_raman - Vm_raman_b
        #Chla = self.cal_chla[0] * (np.log10(Vm_chla - Vm_chla_b) / np.log10(Raman)) + self.cal_chla[1]
        #Cdom = self.cal_cdom[0] * ((Vm_cdom - Vm_cdom_b) / Raman) + self.cal_cdom[1]
        Chla = Vm_chla - Vm_chla_b
        Cdom = Vm_cdom - Vm_cdom_b

        return (Vm_raman, Vm_chla, Vm_cdom, Vm_raman_b, Vm_chla_b, Vm_cdom_b, Raman, Chla, Cdom), date


if __name__ == "__main__":
    instrument = Instrument()
    instrument.measurement()
