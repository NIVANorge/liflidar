#!/usr/bin/python3
import time

import numpy as np
import pandas as pd
from ADCDACPi import ADCDACPi
from ADCPi import ADCPi
from ExpanderPi import DAC

# initaialisation DAC  //// writing (turning on and off laser)
# set dac gain 
dac = DAC(2) # -> output (0-4V)
# set adresses for expender pi (RTC + DAC): 
# maybe default 0x68 and 0x69


# initaialisation ADC //// Reading photodiodes
# set adress for the ADC 8adress pin 1-4, adress pin 5-8, bit rate)
adc = ADCPi(0x6A, 0x6B, 16)
#12 bit (240SPS max)
#14 bit (60SPS max)
#16 bit (15SPS max)
#18 bit (3.75SPS max)

# set adc gain
adc.set_pga(1)

# set adc accuracy // speed
#adc.setBitRate(16)

# time it takes to read 3 channels on the adc (with 16bits config) (ms)
read_time = 200 # to be measured
# laser modulation frequency (Hz) (10-12Hz)
f_laser = 2 #Hz
#laser_wait = (1/f_laser)/2*1000 - read_time#(ms) T(period)/2 (s)
laser_wait = 2
### channel number photodiodes setup
ch_cdom = 3
ch_chla = 2
ch_raman = 1

## channel laser
ch_laser = 1

# sampling interval (s)
Samp_int = 20 
# nb measurements to be averaged for 1 observation
nb_meas = 5 

# read the last calibration value
d = pd.read_csv('../configs/lidar_cal.txt', delimiter="\t")
cal_chla = d.iloc[d.shape[0]-1, [1, 2]]
cal_cdom = d.iloc[d.shape[0]-1, [3, 4]]

done = False
## start measurements
while not done:
	try:
		n_cycle = 0
		V_raman = []
		V_chla = []
		V_cdom = []
		V_raman_b = []
		V_chla_b = []
		V_cdom_b = []

		date = time.strftime('%Y-%m-%d %H:%M:%S')
		start_time = time.perf_counter()
		#while (time.perf_counter() - start_time) < Samp_int:
		while n_cycle < nb_meas:
			n_cycle += 1

			#turn on laser (channel, Voltage (4 is the max - maybe))
			dac.set_dac_voltage(1, 4)
			# wait for fluorescence to reach max 
			time.sleep(laser_wait)
			# measure fluorescence
			V_raman += [adc.read_voltage(ch_raman)]
			V_chla += [adc.read_voltage(ch_chla)] 
			V_cdom += [adc.read_voltage(ch_cdom)] 
			
			# turn off lasser (chanel number, Voltage)
			dac.set_dac_voltage(1, 0)
			# wait for all fluorescence 
			time.sleep(laser_wait)
			# measure background
			V_raman_b += [adc.read_voltage(ch_raman)]
			V_chla_b += [adc.read_voltage(ch_chla)] 
			V_cdom_b += [adc.read_voltage(ch_cdom)] 
		#maybe too slow, then separate the 3 channels in 3 cycles.. but then raman from different sample...

		# average values
		Vm_raman = round(np.mean(V_raman, dtype=np.float32),5)
		Vm_chla = round(np.mean(V_chla, dtype=np.float32),5)
		Vm_cdom = round(np.mean(V_cdom, dtype=np.float32),5)
		Vm_raman_b = round(np.mean(V_raman_b, dtype=np.float32),5)
		Vm_chla_b = round(np.mean(V_chla_b, dtype=np.float32),5)
		Vm_cdom_b = round(np.mean(V_cdom_b, dtype=np.float32),5)
		
		# variances 
		Va_raman = round(np.var(V_raman, dtype=np.float32),5)
		Va_chla = round(np.var(V_chla, dtype=np.float32),5)
		Va_cdom = round(np.var(V_cdom, dtype=np.float32),5)
		Va_raman_b = round(np.var(V_raman_b, dtype=np.float32),5)
		Va_chla_b = round(np.var(V_chla_b, dtype=np.float32),5)
		Va_cdom_b = round(np.var(V_cdom_b, dtype=np.float32),5)
			
		# calculate absolute concentrations
		#chl-a, background chl- a, signal Raman, background Raman, signal CDOM, background CDOM, and estimation of:
		Raman = Vm_raman-Vm_raman_b
		Chla = cal_chla[0]*(np.log(Vm_chla-Vm_chla_b)/np.log(Raman))+cal_chla[1]
		Cdom = cal_cdom[0]*((Vm_cdom-Vm_cdom_b)/Raman)+cal_cdom[1]

        # print & save data
		print(date,"\t","Raman = ","{:.5f}".format(Raman),"\t","Chla = ","{:.5f}".format(Chla),"\t","cdom = ","{:.5f}".format(Cdom),"\n",
			"V_raman = ","{:.5f}".format(Vm_raman),"\t","V_chla = ","{:.5f}".format(Vm_chla),"\t","V_cdom = ","{:.5f}".format(Vm_cdom),"\n",
			"V_raman_back = ","{:.5f}".format(Vm_raman_b),"\t","V_chla_back = ","{:.5f}".format(Vm_chla_b),"\t","V_cdom_back = ","{:.5f}".format(Vm_cdom_b),"\n")

		print("Var_raman = ","{:.5f}".format(Va_raman),"\t","Var_chla = ","{:.5f}".format(Va_chla),"\t","Var_cdom = ","{:.5f}".format(Va_cdom),"\n",
			"Var_raman_back = ","{:.5f}".format(Va_raman_b),"\t","Var_chla_back = ","{:.5f}".format(Va_chla_b),"\t","Var_cdom_back = ","{:.5f}".format(Va_cdom_b),"\n")

		fp = open('data_LIDAR.txt', 'a')
		#header = ( "date", "Raman")
		fp.write(date + "\t"+ "{:.5f}".format(Raman)+"\t"+"{:.5f}".format(Chla)+"\t"+"{:.5f}".format(Cdom)+"\t"+
			"{:.5f}".format(Vm_raman)+"\t"+"{:.5f}".format(Vm_chla)+"\t"+"{:.5f}".format(Vm_cdom)+"\t"+
			"{:.5f}".format(Vm_raman_b)+"\t"+"{:.5f}".format(Vm_chla_b)+"\t"+"{:.5f}".format(Vm_cdom_b)+"\t"+
			"{:.5f}".format(Va_raman)+"\t"+"{:.5f}".format(Va_chla)+"\t"+"{:.5f}".format(Va_cdom)+"\t"+
			"{:.5f}".format(Va_raman_b)+"\t"+"{:.5f}".format(Va_chla_b)+"\t"+"{:.5f}".format(Va_cdom_b)+"\n")
		fp.close()
		#time.sleep(Samp_int*100-(time.perf_counter() - start_time)*100) # s?
		time.sleep(Samp_int*100)
	except KeyboardInterrupt:
		done = True
		

""" def read_V (chn,nb):
    Vs = []
    for n in range(nb):
        Vs += [adc.read_voltage(chn)]
    V=round(np.mean(Vs, dtype=np.float32),5)
    V_sd=round(np.std(Vs, dtype=np.float32),5)
    return V, V_sd """

