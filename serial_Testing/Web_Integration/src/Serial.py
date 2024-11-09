import time
import os
import random
import serial

baudRate = 230400 # Baud Rate Specified on Arudinos
loopExit = False # Used to exit control loop when user exits program


def confirm_comm(port):
	"""
	Confirms if an Arduino can be found and can be communicated with at the specified port. An attempt to connect to the Arduino using PySerial is made
	assuming the Arduino Serial Interface is NOT being used by other processes (i.e.: Arduino IDE). When connected, a PING message is sent to the port
	being connected to, which should prompt the Arduino(s) to send a PONG message back. Depending on which Arudino is connected to the port, PONG1 and PONG2
	helps to identify which arduino controls the conveyor and input buffer (CONV) and which controls the sorting motors and weight sensors (SORT) respectively.
	If an Ardunio can successfully communicate within 10 tries, return True and the id of the arduino; otherwise return False and None.
	"""

	pong = False
	id = None
	attempts = 1
	print(f"Attempting to Connect to {port} via. Serial...")

	try:
		ser = serial.Serial(port, baudRate, timeout=1) # Connect to Arduino at port
		time.sleep(5) # Wait for connection to establish

		while (not pong):
			"""
			While the arduino has not confirmed proper connection, send PING. If a response is recieved, keep track of which Arduino sent response,
			and break loop; else, keep looping until 10 attmempts have been made.
			"""
			print(f"Connection Attempt {attempts}")
			
			ser.write("PING>\n".encode('utf-8')) # Send PING to port
			
			serResp = getSerResp(ser, False) # Recieve Response from Arduino, no expected value
			if "PONG1" in serResp: # If Conveyor Arduino Responds
				pong = True
				id = 0
			elif "PONG2" in serResp: # If Sorting Arduino Responds
				pong = True
				id = 1

			# If response not recieved, keep adding to attempt counter until 10 have failed.
			if not pong:
				attempts += 1
			if attempts >= 11:
				ser.close() # Close serial connections
				return False, id # Connection failed
			
			time.sleep(2)
		
		ser.close()  # Close serial connections
		return True, id  # Connection Failed
	
	# Exception - Serial Port being used by another process (Arduino IDE)
	except serial.serialutil.SerialException as e:
		print(f"{e}\n")
		return False, id


def detectArduino():
	"""
	Used to detect the Arduinos at the begining of execution. Function will go through ports connected to computer, and check for any that have Arduino (Windows)
	or ACM (Pi/Linux) within the name. If an Arduino is detected, run the confirm communications function to determine (1) if Arduino can communicate, and (2) which
	Arduino is detected (the ports change with every execution). Returns the ports of the Arduinos if successful, or None if not successful.
	"""

	arduinoPorts = [None, None] # Initialise return array
	
	comPorts = os.listdir("/dev") # For Linux, /dev is Arduino ports resign. This lists any directory and/or port found within the /dev path

	for port in comPorts:
		strPort = str(port) # Name of port
 
		# For Linux, if ACM is within the port name, that represents an Arduino being connected. Check port for communications, and assign the
		# Arduino Port Return Array with the port (at index 'ID') if successful
		if ("ACM" in strPort):
			# Attempts to connect to port found
			splitPort = strPort.split(' ')
			portPath = f"/dev/{splitPort[0]}"
			portConn, id = confirm_comm(portPath)
		
			# If connection was successful, assign port to return array
			if portConn and (id is not None):
				arduinoPorts[id] = portPath

	return arduinoPorts

def getSerResp(ser = None, expectedData = False):
	"""
	Used to get a response back from an Arduino via. PySerial. If the data is not expected (i.e.: For checking if there is communications), wait until the specified
	Arduino (serial) port returns something; otherwise, attempt to read what is sent. If the response is not blank, print the response to console and return it; otherwise,
	return NaN. NaN means there is something wrong with the communications.
	"""

	# If no serial port is specified, return None
	if ser is None:
		return None
	
	serResp = None

	"""
	'ser.in_waiting' is used to check whether or not something is being sent from the Arduino. if expectedData is false, that means we are not
	expecting any data to come back from the Arduino, which means the program will not get stuck should nothing get sent; otherwise, we attempt
	to read the data (regardless) if we are expecting data.
	"""
	if not expectedData:
		time.sleep(0.1)
		while ser.in_waiting > 0:
			serResp = ser.readline().decode("utf-8")
	else:
		serResp = ser.readline().decode("utf-8")

	# If the data returns properly, print out what was sent and return it; otherwise, return "NaN"
	if serResp != '' and serResp is not None:
		print(f"Serial=>Comp: {serResp}")
		return serResp
	else:
		return "NaN"