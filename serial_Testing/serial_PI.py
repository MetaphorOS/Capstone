#!/usr/bin/env python3
import serial
import time
 
ser0 = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
#ser1 = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
 
ser0.flush()
#ser1.flush()
 
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
		
		"""			
		#while ser1.in_waiting > 0:
		outSer1 = ser1.readline().decode("utf-8")	
		if outSer1 != '' and outSer1 is not None:
			outSer1 = outSer1.replace('\r\n','')
			print(f"Arduino1=>pi: {outSer1}")
			if outSer1 == "PONG":
				pong1 = True
		"""
		if ((pong0 == False)): # or (pong1 == False)):
			attempts += 1
		
		if attempts >= 11:
			return True
		
		time.sleep(1)
	return False
 
if __name__ == '__main__':
	if confirm_comm():
		exit(1)
	else:
		ser0.flush()
	#	ser1.flush()
	
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
					
		"""			
		while ser1.in_waiting > 0:
			outSer1 = ser1.readline().decode("utf-8")
		if outSer1 != '' and outSer1 is not None:
			outSer1 = outSer1.replace('\r\n','')
			print(f"Arduino1=>pi: {outSer1}")
		"""
		
		if loopExit and (not motor):
			break
	
	exit(0)
 
