#!/usr/bin/env python3
import time
import os # For Raspberry Pi /dev/ttyAMC Ports
import random

import serial
# import serial.tools.list_ports as listPorts # For Windows COM ports

timeS = time.strftime("%Y-%m-%d-%H_%M_%S")

baudRate = 230400
loopExit = False

def confirm_comm(port):
	pong = False
	id = None
	attempts = 1
	print(f"Attempting to Connect to {port} via. Serial...")

	try:
		ser = serial.Serial(port, baudRate, timeout=1)
		#ser.reset_input_buffer()
		time.sleep(2)

		while (not pong):
			print(f"Connection Attempt {attempts}")
			
			ser.write("PING>\n".encode('utf-8'))
			
			serResp = getSerResp(ser, False)
			if "PONG1" in serResp:
				pong = True
				id = 0
			elif "PONG2" in serResp:
				pong = True
				id = 1

			if not pong:
				attempts += 1
			if attempts >= 11:
				ser.close()
				return False, id
			
			time.sleep(3)
		
		ser.close()
		return True, id
	except serial.serialutil.SerialException as e:
		print(f"{e}\n")
		# ser.close()
		return False, id


def detectArduino():
	arduinoPorts = [None, None]

	comPorts = os.listdir("/dev")

	for port in comPorts:
		strPort = str(port)
 
		if ("ACM" in strPort):
			splitPort = strPort.split(' ')
			portPath = f"/dev/{splitPort[0]}"
			portConn, id = confirm_comm(portPath)
		
			if portConn and (id is not None):
				arduinoPorts[id] = portPath

	return arduinoPorts

def getSerResp(ser = None, expectedData = False):
	if ser is None:
		return None
	
	serResp = None

	if not expectedData:
		time.sleep(0.1)
		while ser.in_waiting > 0:
			serResp = ser.readline().decode("utf-8")
	else:
		serResp = ser.readline().decode("utf-8")

	if serResp != '' and serResp is not None:
		print(f"Serial=>Comp: {serResp}")
		return serResp
	else:
		return "NaN"

if __name__ == '__main__':
	arduinoPorts = detectArduino()

	if None in arduinoPorts:
		print("Couldn't detect Arduino through COM Ports, aborting script.")
		exit(1)
	else:
		print (f"Conveyor : Sorting (Ports) - {arduinoPorts[0]} : {arduinoPorts[1]}")
		serConv = serial.Serial(arduinoPorts[0], baudRate, timeout=1)
		serSort = serial.Serial(arduinoPorts[1], baudRate, timeout=1)
		
		time.sleep(2)
		
		serConv.reset_input_buffer()
		serSort.reset_input_buffer()

	convData = ""
	sortData = ""

	convExit = False
	sortExit = False

	serConv.write(f"START\n".encode('utf-8'))
	serSort.write(f"START\n".encode('utf-8'))

	while True:
		try:
		# 	command = input("Command: ").upper()
		# 	if command == "EXIT" or command == "OFF":
		# 		serConv.write(f"OFF\n".encode('utf-8'))
		# 		serSort.write(f"OFF\n".encode('utf-8'))
		# 		print("Turning Motor OFF")
		# 		if command == "EXIT":
		# 			loopExit = True
		# 	elif command == "ON":
		# 		serConv.write(f"ON\n".encode('utf-8'))
		# 		serSort.write(f"ON\n".encode('utf-8'))
		# 		print("Turning Motor ON")
		# except KeyboardInterrupt:
		# 	serConv.write(f"OFF\n".encode('utf-8'))
		# 	serSort.write(f"OFF\n".encode('utf-8'))
		# 	print("Turning Motor OFF")
		# 	loopExit = True

			convData = getSerResp(serConv, False)
			sortData = getSerResp(serSort, False)

			#print(convData, sortData, "\n")

			if "NaN" not in convData and convData is not None:
				if ("OFF" in convData) and loopExit:
					convExit = True

				elif "Detected" in convData:
						r = random.randint(0,2)
						time.sleep(3)
						print(f"IT DETECTED {r}")
						serSort.write(f"Sort: {r}\n".encode('utf-8'))

				elif "STARTED" in convData:
					print("YEAH BABY LETS GOO") 

			if "NaN" not in sortData and sortData is not None:
				if ("OFF" in sortData) and loopExit:
					sortExit = True
				
				elif "Ready" in sortData:
					serConv.write(f"START\n".encode('utf-8'))
					print("YEAH BABY LETS GOO WOOO?")
				elif "Overweight" in sortData:
					serConv.write(f"OFF\n".encode('utf-8'))
					print("whoops")
				elif "Resuming" in sortData:
					serConv.write(f"START\n".encode('utf-8'))
					print("Run it Back")				
				elif "STARTED" in sortData:
					print("WOOOOO, YEAH BABY!!") 

			if convExit and sortExit:
				break
			
		except KeyboardInterrupt:
			serConv.reset_input_buffer()
			serSort.reset_input_buffer()

			serConv.write(f"OFF\n".encode('utf-8'))
			serSort.write(f"OFF\n".encode('utf-8'))
			
			loopExit = True

	serConv.close()
	serSort.close()
	exit(0)