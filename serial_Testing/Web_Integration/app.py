from flask import Flask, render_template, redirect, url_for, jsonify
import threading
import time
import sqlite3
from src.Serial import *

app = Flask(__name__)

write_lock = threading.Lock()
is_locked = False
stop = False
loopExit = False

Database = 'tomato.db'

def background_loop():
	global is_locked
	global stop
	global loopExit
	arduinoPorts = detectArduino()

	if None in arduinoPorts:
		print("Couldn't detect arduino through COM ports, aborting script")
		exit(1)
	else:
		print(f"Conveyor : Sorting (Ports) - {arduinoPorts[0]} : {arduinoPorts[1]}")
		serConv = serial.Serial(arduinoPorts[0], baudRate, timeout=1)
		serSort = serial.Serial(arduinoPorts[1], baudRate, timeout=1)
		time.sleep(5)
		serConv.reset_input_buffer()
		serSort.reset_input_buffer()
	
	convData = ""
	sortData = ""
	
	convExit = False
	sortExit = False

	serConv.write(f"START\n".encode('utf-8'))
	serSort.write(f"START\n".encode('utf-8'))
	while True:
		with open('checkBatch.sql', mode='r') as f:
			script = f.read()
		db = get_db()
		result = db.execute(script).fetchall()
		row = result[0]['result']
		if row:
			if row == "No data available":
				tomato = 0
			else:
				values = row.split(',')
				batch_number = int(values[0].strip())
				tomato = int(values[1].strip())

		if stop == True:
			print("it stopped :)")
			serConv.reset_input_buffer()
			serSort.reset_input_buffer()

			serConv.write(f"OFF\n".encode('utf-8'))
			serSort.write(f"OFF\n".encode('utf-8'))

			stop = True
								
			while stop == True:
				pass
			batch_number = add_new_row(batch_number)
			serConv.write(f"START\n".encode('utf-8'))
			serSort.write(f"START\n".encode('utf-8'))


		try:
			convData = getSerResp(serConv, False)
			sortData = getSerResp(serSort, False)

			if "NaN" not in convData and convData is not None:
				if ("OFF" in convData) and loopExit:
					convExit = True

				elif "Detected" in convData:
					with open('checkBatch.sql', mode='r') as f:
						script = f.read()
					
					db = get_db()
					result = db.execute(script).fetchall()
					row = result[0]['result']
					if row:
						if row == "No data available":
							batch_number = add_new_row(0)
						else:
							values = row.split(',')
							batch_number = int(values[0].strip())
							tomato = int(values[1].strip())
							# print(tomato)
						
						r = randomAdd(batch_number)
					db.close()
					time.sleep(3)
					print(f"IT DETECTED {r}")
					serSort.write(f"Sort: {r}\n".encode('utf-8'))  # Send sorting results to Sorting Arduino

				# If STARTED is received, Conveyor Arduino is confirmed to have started.
				elif "STARTED" in convData:
					print("YEAH BABY LET'S GOO") 

			# If there is a response from the Sorting Arduino, perform actions where applicable
			if "NaN" not in sortData and sortData is not None:
				# If OFF is received, Sorting Arduino is confirmed to be stopped, set exit loop variable to TRUE
				if ("OFF" in sortData) and loopExit:
					sortExit = True
					
				# If Ready is received, that means the Sorting Arduino is ready for the conveyance Arduino to move the tomato for sorting.
				# Send RESUME command to conveyor Arduino
				elif "Ready" in sortData:
					serConv.write(f"RESUME\n".encode('utf-8'))
					print("YEAH BABY LET'S GOO WOOO?")
					
				# If Overweight is received, weight sensors determined that 1+ containers are overweight. Send a stop command to the conveyance Arduino
				elif "Overweight" in sortData:
					serConv.write(f"OFF\n".encode('utf-8'))
					print("whoops")
					
				# If Resuming is received, weight sensors are now reset, and the process is resuming. Send RESUME command to conveyor Arduino
				elif "Resuming" in sortData:
					serConv.write(f"RESUME\n".encode('utf-8'))
					print("Run it Back")
					
				# If Emptied is received, that means the sorting queue in the sorting Arduino is emptied. Restart the input buffer by sending the BUFFER command to
				# the conveyance Arduino
				elif "Emptied" in sortData:
					if tomato >= 10:
						stop = True
					else:
						serConv.write(f"BUFFER\n".encode('utf-8'))
					
				# If STARTED is received, Sorting Arduino is confirmed to have started.
				elif "STARTED" in sortData:
					print("WOOOOO, YEAH BABY!!") 

				# If both Arduinos have confirmed to have stopped/turned off, break the control loop
			if convExit and sortExit:
				break
				
		except KeyboardInterrupt:
			serConv.reset_input_buffer()
			serSort.reset_input_buffer()

			serConv.write(f"OFF\n".encode('utf-8'))
			serSort.write(f"OFF\n".encode('utf-8'))
			
			loopExit = True

	# Close Arduino Serial Connections, and exit response 0
	serConv.close()
	serSort.close()

@app.route('/')
def dashboard():
	return render_template('index.html')

# @app.route('/inventory')
# def inventory():
# 	# if write_lock.locked():
# 	#     return redirect(url_for('/'))
# 	# else:
# 	return render_template('inventory.html', is_locked=is_locked)

@app.route('/debug')
def orders():
	return render_template('debug.html')

@app.route('/inventory')
def check():
	# db = get_db()
	# with open('check.sql', mode='r') as f:
	# 	query = f.read()
	
	# result = db.execute(query).fetchall()
	# db.close()
	# print(result)
	return render_template('inventory.html')

@app.route('/stop', methods=['POST'])
def stop():
	try:
		global stop
		stop = True
		return jsonify({"status": "success", "message": "Stop is true"})
	except Exception as e:
		return jsonify({"status": "error", "message": str(e)})

@app.route('/start_again', methods=['POST'])
def start_again():
	try:
		global stop
		stop = False
		return jsonify({"status": "success", "message": "New Batch started"})
	except Exception as e:
		return jsonify({"status": "error", "message": str(e)})

#simulate a tomato being found
@app.route('/sql_script', methods=['POST'])
def sql_script():
	try:
		with open('checkBatch.sql', mode='r') as f:
			script = f.read()
		
		db = get_db()
		result = db.execute(script).fetchall()
		row = result[0]['result']
		if row:
			if row == "No data available":
				batch_number = add_new_row(0)
			else:
				values = row.split(',')
				batch_number = int(values[0].strip())
				tomato = int(values[1].strip())
				# print(tomato)
				if tomato >= 10:
					batch_number = add_new_row(batch_number)
			# print(batch_number)
			r = randomAdd(batch_number)
			

		db.close()

		return jsonify({"status": "success", "message": "SQL script executed successfully"})
	except Exception as e:
		return jsonify({"status": "error", "message": str(e)})

#randomly adds 1 of the values to the database
def randomAdd(batch_number):
	db = get_db()
	cursor = db.cursor()
	r = random.randint(0,2)
	if r == 0:
		cursor.execute("UPDATE Batch_info SET tomato = tomato + 1 WHERE batch_number = " + str(batch_number))
		cursor.execute("UPDATE Ripe SET tomato = tomato + 1 WHERE batch_number = " + str(batch_number))
	elif r == 1:
		cursor.execute("UPDATE Batch_info SET tomato = tomato + 1 WHERE batch_number = " + str(batch_number))
		cursor.execute("UPDATE Unripe SET tomato = tomato + 1 WHERE batch_number = " + str(batch_number))
	elif r == 2:
		cursor.execute("UPDATE Batch_info SET tomato = tomato + 1 WHERE batch_number = " + str(batch_number))
		cursor.execute("UPDATE Twilight_zone SET tomato = tomato + 1 WHERE batch_number = " + str(batch_number))
	db.commit()
	db.close()
	return r

#add row when tomato counter for latest batch = 10
def add_new_row(batch_number):
	db = get_db()
	cursor = db.cursor()
	cursor.execute("INSERT INTO Batch_info (batch_number, tomato) VALUES (" + str(int(batch_number + 1)) + ", 0)")
	cursor.execute("INSERT INTO Unripe (batch_number, tomato) VALUES (" + str(int(batch_number + 1)) + ", 0)")
	cursor.execute("INSERT INTO Ripe (batch_number, tomato) VALUES (" + str(int(batch_number + 1)) + ", 0)")
	cursor.execute("INSERT INTO Twilight_zone (batch_number, tomato) VALUES (" + str(int(batch_number + 1)) + ", 0)")
	db.commit()
	db.close()

	return batch_number + 1

#Auto-update
@app.route('/get_tomato_batches')
def get_tomato_batches():
	db = get_db()
	with open('checkTomatos.sql', mode='r') as f:
		query = f.read()
	result = db.execute(query).fetchall()
	db.close()
	batches = [dict(row) for row in result]
	return jsonify(batches)

#Databse code
def get_db(): 
	db = sqlite3.connect(Database)
	db.row_factory= sqlite3.Row
	return db

def init_db():
	with app.open_resource('init_db.sql', mode='r') as f:
		print("YEP")
		db = get_db()
		db.cursor().executescript(f.read())
		db.commit()
	# with open('filldb.sql', mode='r') as f:
	# 	db = get_db()
	# 	db.cursor().executescript(f.read())
	# 	db.commit()

def initialize():
	if not os.path.isfile(Database):
		init_db()

if __name__ == '__main__':
	initialize()
	thread = threading.Thread(target=background_loop, daemon=True)
	thread.start()
	app.run(debug=True, threaded=True)
