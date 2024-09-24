#!/usr/bin/env python3
import serial
import serial.tools.list_ports as listPorts
import time

baudRate = 9600
loopExit = False

#ser0.flush()
#ser1.flush()
""" 
def confirm_comm():
	pong0 = False
#	pong1 = False    

	attempts = 1
	
	while ((pong0 == False)): # or (pong1 == False)):
		print(f"Connection Attempt {attempts}")
		
		ser0.write("PING\n".encode('utf-8'))
#		ser1.write("PING\n".encode('utf-8'))
		
		outSer0 = ''
#		outSer1 = ''
		
		time.sleep(0.01) # Needed if checking if input from Arduino received instead of knowing it will
		while ser0.in_waiting > 0:
			print(attempts)
			outSer0 = ser0.readline().decode("utf-8")
		if outSer0 != '' and outSer0 is not None:
			outSer0 = outSer0.replace('\r\n','')
			print(f"Arduino0=>pi: {outSer0}")
			if outSer0 == "PONG":
				pong0 = True
		
					
		#while ser1.in_waiting > 0:
		outSer1 = ser1.readline().decode("utf-8")	
		if outSer1 != '' and outSer1 is not None:
			outSer1 = outSer1.replace('\r\n','')
			print(f"Arduino1=>pi: {outSer1}")
			if outSer1 == "PONG":
				pong1 = True
		
		if ((pong0 == False)): # or (pong1 == False)):
			attempts += 1
		
		if attempts >= 11:
			return True
		
		time.sleep(1)
	return False
"""

def confirm_comm(port):
	pong = False
	id = None
	attempts = 1
	print(f"Attempting to Connect to {port} via. Serial...")

	try:
		ser = serial.Serial(port, baudRate, timeout=1)
		ser.reset_input_buffer()
		time.sleep(2)

		while (not pong):
			print(f"Connection Attempt {attempts}")
			
			ser.write("PING\n".encode('utf-8'))
			
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
			
			time.sleep(1)
		
		ser.close()
		return True, id
	except serial.serialutil.SerialException as e:
		print(f"{e}\n")
		# ser.close()
		return False, id


def detectArduino():
	arduinoPorts = [None, None]

	comPorts = listPorts.comports()

	for port in comPorts:
		strPort = str(port)
 
		if ("Arduino" in strPort):
			splitPort = strPort.split(' ')
			portConn, id = confirm_comm((splitPort[0]))
		
			if portConn:
				arduinoPorts[id] = (splitPort[0])

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

		serConv.reset_input_buffer()
		serSort.reset_input_buffer()
	

	convData = ""
	sortData = ""

	convExit = False
	sortExit = False

	while True:
		# try:
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


		serConv.reset_input_buffer()
		serSort.reset_input_buffer()

		convData = getSerResp(serConv, False)
		sortData = getSerResp(serSort, False)

		#print(convData, sortData)

		if "NaN" not in convData:
			if ("OFF STATE" in convData) and loopExit:
				convExit = True
		#print(convData, sortData)
		if "Tomato_Detected" in convData:
			serSort.write(f"Arm_True".encode('utf-8'))
			print("ITS DETECTED")

		if "Conveyor_started" in convData:
			print("YEAH BABY LETS GOO") 

		if "NaN" not in sortData:
			if ("OFF STATE" in sortData) and loopExit:
				sortExit = True
		
		if "Arm_Ready" in sortData:
			serConv.write(f"Arm_Done".encode('utf-8'))
			print("YEAH BABY LETS GOO WOOO?")


		if convExit and sortExit:
			break

	serConv.close()
	serSort.close()
	exit(0)

	"""
	else:
		ser0 = serial.Serial(arduinoPort1, baudRate, timeout=1)
		#ser1 = serial.Serial(arduinoPort2, baudRate, timeout=1)

	loopExit = False
	motor = False

	while True:
		command = input("Command: ").upper()
		if command == "EXIT":
			ser0.write(f"OFF\n".encode('utf-8'))
			print("Turning Motor OFF")
			loopExit = True
		else:
			ser0.write(f"{command}\n".encode('utf-8'))
		#ser1.write(f"{command}\n".encode('utf-8'))
		
		outSer0 = ''
		#outSer1 = ''
		
		time.sleep(0.01) # Needed if checking if input from Arduino received instead of knowing it will						
		while ser0.in_waiting > 0:
			outSer0 = ser0.readline().decode("utf-8")
		if outSer0 != '' and outSer0 is not None:
			outSer0 = outSer0.replace('\r\n','')
			print(f"Arduino0=>pi: {outSer0}")
			
			if outSer0 == "OFF STATE":
				motor = False
			elif outSer0 == "ON STATE":
				motor = True
					
					
		# while ser1.in_waiting > 0:
		# 	outSer1 = ser1.readline().decode("utf-8")
		# if outSer1 != '' and outSer1 is not None:
		# 	outSer1 = outSer1.replace('\r\n','')
		# 	print(f"Arduino1=>pi: {outSer1}")
		
		
		if loopExit and (not motor):
			break
	
	exit(0)
	"""