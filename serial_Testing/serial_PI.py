#!/usr/bin/env python3
import time
import os # For Raspberry Pi /dev/ttyAMC Ports
import random

import serial
# import serial.tools.list_ports as listPorts # For Windows COM ports

# timeS = time.strftime("%Y-%m-%d-%H_%M_%S")

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

if __name__ == '__main__':
	arduinoPorts = detectArduino() # Checks for Arduino Connections.

	# If an Arduino fails to connect, the program exits with status 1. This means either another process is using the port, or something is wrong with the connection
	# If the Arduinos connect properly, assign the conveyor & input buffer port to the conveyor serial object and the sorting servo/weight sensor port to the sorting serial object
	if None in arduinoPorts:
		print("Couldn't detect Arduino through COM Ports, aborting script.")
		exit(1)
	else:
		print (f"Conveyor : Sorting (Ports) - {arduinoPorts[0]} : {arduinoPorts[1]}")
		serConv = serial.Serial(arduinoPorts[0], baudRate, timeout=1) # Connect to Conveyor Arduino
		serSort = serial.Serial(arduinoPorts[1], baudRate, timeout=1) # Connect to Sorting Arduino
		
		time.sleep(5) # Wait for connection to establish
		
		# Flushes both buffers after attempting to test connections (i.e.: Resets them for further processing)
		serConv.reset_input_buffer()
		serSort.reset_input_buffer()

	# Initialise data variables for both Arduinos
	convData = ""
	sortData = ""

	# Used to exit the control loop when user exits program
	convExit = False
	sortExit = False

	# Tell both Arduinos to start their respective processes
	serConv.write(f"START\n".encode('utf-8'))
	serSort.write(f"START\n".encode('utf-8'))

	# Main Control Loop
	while True:
		"""
		Main Control Loop

		First attempt to get a response from both Arduinos if there is one available. Then depending on if a response is recieved from the Arduinos, certain
		actions/commands take place. The following explains the main flow of control:
			- Both Arduinos are stated outside of loop. If successful, both send 'STARTED'
			- Conveyor Arduino Detects Tomato via. Proximety Sensor - Sends 'Detected'
			- When 'Detected', determine how Tomato is sorted, and send result to Sorting Arduino - Sort: {result}
			- Sorting Arduino recieves result and puts it in a sorting queue. When finished and sorting arm is in place, send 'Ready'
			- When Sorting Arduino is 'Ready', send a command to the conveyor arduino to 'RESUME' operations.
			- Conveyance Arduino restarts conveyor, and confirms this by sending 'STARTED'
			
			- If the Tomato is successfully sorted by Sorting Arduino and assuming no other tomatoes are in the sorting queue, feedback for queue being
			  'Emptied' is sent.
			- When 'Emptied' feedback is sent, a command to restart the Conveyor Arduino's Input Buffer ('BUFFER') is sent
			
			- If one of the Sorting Arduino's scales is overweight, an 'Overweight' response is sent, which halts the Conveyance Arduino's operations
			- When it is determined by the Sorting Arduino that no container/scale is overweight, a 'Resuming' response is sent, which in turn restarts
			  the Coneyor Arduino's processes

			- Upon Keyboardinterrupt, an 'OFF' command is sent to both Arduinos, signifying for both to stop what they are doing. When both Arduinos confirm
			  they have stopped by responding 'OFF', exit the control loop.
			- Close the serial ports upon exiting the loop, and return 0
		"""
		try:
			# Get responses from Arduinos if there is any
			convData = getSerResp(serConv, False)
			sortData = getSerResp(serSort, False)

			# If there is a response from the Conveyance Arduino, peform actions where applicable
			if "NaN" not in convData and convData is not None:
				# If OFF is recieved, Conveyor Arduino is confirmed to be stopped, set exit loop variable to TRUE
				if ("OFF" in convData) and loopExit:
					convExit = True

				# If Detected is recieved, determine how the Tomato should be sorted, and send the results to the Sorting Arduino
				elif "Detected" in convData:
					r = random.randint(0,2) # Placeholder for determining sorting
					time.sleep(3)
					print(f"IT DETECTED {r}")
					serSort.write(f"Sort: {r}\n".encode('utf-8')) # Send Sorting results to Sorting Arduino

				# If STARTED is recieved, Conveyor Arduino is confirmed to have started.
				elif "STARTED" in convData:
					print("YEAH BABY LETS GOO") 

			# If there is a response from the Sorting Arduino, peform actions where applicable
			if "NaN" not in sortData and sortData is not None:
				# If OFF is recieved, Sorting Arduino is confirmed to be stopped, set exit loop variable to TRUE
				if ("OFF" in sortData) and loopExit:
					sortExit = True
				
				# If Ready is recieved, that means the Sorting Arduino is ready for the conveyance arduino to move the tomato for sorting.
				# Send RESUME command to conveyor arduino
				elif "Ready" in sortData:
					serConv.write(f"RESUME\n".encode('utf-8'))
					print("YEAH BABY LETS GOO WOOO?")
				
				# If Overweight is recieved, weight sensors determined that 1+ containers are overweight. Send a stop command to the conveyance arduino
				elif "Overweight" in sortData:
					serConv.write(f"OFF\n".encode('utf-8'))
					print("whoops")
				
				# If Resuming is recieved, weight sensors are now reset, and the process is resuming. Send RESUME command to conveyor arduino
				elif "Resuming" in sortData:
					serConv.write(f"RESUME\n".encode('utf-8'))
					print("Run it Back")
				
				# If Emptied is recieved, that means the sorting queue in the sorting arduino is emptied. Restart the input buffer by sending the BUFFER command to
				# the conveyance arduino
				elif "Emptied" in sortData:
					serConv.write(f"BUFFER\n".encode('utf-8'))
				
				# If STARTED is recieved, Sorting Arduino is confirmed to have started.
				elif "STARTED" in sortData:
					print("WOOOOO, YEAH BABY!!") 

			# If both Arduinos have confirmed to have stopped/turned off, break the control loop
			if convExit and sortExit:
				break
		
		# On Keyboard interrupt, send an OFF command to BOTH Arduinos to stop the entire process. Set loopExit to True to make sure loop is exited when Arduinos stop
		except KeyboardInterrupt:
			serConv.reset_input_buffer()
			serSort.reset_input_buffer()

			serConv.write(f"OFF\n".encode('utf-8'))
			serSort.write(f"OFF\n".encode('utf-8'))
			
			loopExit = True

	# Close Arduino Serial Connections, and exit response 0
	serConv.close()
	serSort.close()
	exit(0)