from flask import Flask, render_template, redirect, url_for, jsonify, Response, request, send_file
import threading
import time
import sqlite3
from src.Serial import *
from camera.color import *
import cv2
import numpy as np

app = Flask(__name__)

write_lock = threading.Lock()
is_locked = False
stop = False
loopExit = False

Database = 'tomato.db'

red_hsv = {}
green_hsv = {}

file = open("val.txt", "r")
red_hsv["H_min"] = file.readline()
red_hsv["H_max"] = file.readline()
red_hsv["S_min"] = file.readline()
red_hsv["S_max"] = file.readline()
red_hsv["V_min"] = file.readline()
red_hsv["V_max"] = file.readline()

green_hsv["H_min"] = file.readline()
green_hsv["H_max"] = file.readline()
green_hsv["S_min"] = file.readline()
green_hsv["S_max"] = file.readline()
green_hsv["V_min"] = file.readline()
green_hsv["V_max"] = file.readline()

# red_hsv = {'H_min': 0, 'H_max': 10, 'S_min': 100, 'S_max': 255, 'V_min': 100, 'V_max': 255}
# green_hsv = {'H_min': 40, 'H_max': 80, 'S_min': 100, 'S_max': 255, 'V_min': 100, 'V_max': 255}


image_paths = [
    "static/images/green.jpg",
    "static/images/red.jpg",
    "static/images/brown.jpg"
]

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
						
						r = detectValue(red_hsv["H_min"], red_hsv["H_max"], red_hsv["S_min"], red_hsv["S_max"], red_hsv["V_min"], red_hsv["V_max"], green_hsv["H_min"], green_hsv["H_max"], green_hsv["S_min"], green_hsv["S_max"], green_hsv["V_min"], green_hsv["V_max"]) #randomAdd(batch_number)
						richard(batch_number, r)
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

def richard(batch_number, r):
	db = get_db()
	cursor = db.cursor()
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

@app.route("/settings")
def settings():
	global stop
	stop = True
	return render_template('settings.html')

def apply_hsv_filter(image, hsv_range):
    """Apply HSV filter to an image."""
    # Convert to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define lower and upper HSV bounds
    lower_bound = np.array([hsv_range['h_min'], hsv_range['s_min'], hsv_range['v_min']])
    upper_bound = np.array([hsv_range['h_max'], hsv_range['s_max'], hsv_range['v_max']])

    # Create the mask based on the HSV range
    mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
    
    # Apply the mask to the image
    filtered_image = cv2.bitwise_and(image, image, mask=mask)

    # Check if any pixels match the filter
    is_filter_present = np.any(mask > 0)

    # print(filtered_image)

    return filtered_image, int(is_filter_present)

@app.route("/startup", methods=["POST"])
def startup():
	try:
		global stop 
		stop = False
		return jsonify(success=True), 400
	except Exception as e:
		return jsonify(success=False), 500


@app.route("/filtered", methods=["POST"])
def filtered_image():
    print("YEAH")
    """Handle the POST request for filtered images."""
    data = request.get_json()

    # Log the received data to debug
    print("Received data:", data)

    # for field in required_fields:
    #     if field not in data:
    #         print(field)
    #         return jsonify({"error": f"Missing field: {field}"}), 400

    filter_type = data['filter_type']
    # image_id = data['image_id']

    # Validate image_id
    # if image_id < 1 or image_id > len(image_paths):
    #     return jsonify({"error": "Image ID out of range"}), 400

    # Get the current filter settings from the request
    hsv_range = {
        'h_min': int(data[f'{filter_type}-h-min']),
        'h_max': int(data[f'{filter_type}-h-max']),
        's_min': int(data[f'{filter_type}-s-min']),
        's_max': int(data[f'{filter_type}-s-max']),
        'v_min': int(data[f'{filter_type}-v-min']),
        'v_max': int(data[f'{filter_type}-v-max']),
    }

    # Load the original image based on image_id
    for i in range(len(image_paths)):
        image_path = image_paths[i]  # Subtract 1 to get the correct image index
        script_dir = os.path.dirname(__file__)
        image_path = os.path.join(script_dir, image_path)
        image = cv2.imread(image_path)

        if image is None:
            return jsonify({"error": "Image not found"}), 400

    # Apply the selected filter
        filtered_image, _ = apply_hsv_filter(image, hsv_range)

    # Save the filtered image temporarily
        output_path = f"static/temp/{filter_type}_filtered_{i+1}.jpg"
        output_path = os.path.join(script_dir, output_path)
    # os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, filtered_image)

    if filter_type == "red": 
        red_hsv["H_max"] = hsv_range["h_max"]
        red_hsv["H_min"] = hsv_range["h_min"]
        red_hsv["S_min"] = hsv_range["s_min"]
        red_hsv["S_max"] = hsv_range["s_max"]
        red_hsv["V_min"] = hsv_range["v_min"]
        red_hsv["V_max"] = hsv_range["v_max"]
    else:
        green_hsv["H_max"] = hsv_range["h_max"]
        green_hsv["H_min"] = hsv_range["h_min"]
        green_hsv["S_min"] = hsv_range["s_min"]
        green_hsv["S_max"] = hsv_range["s_max"]
        green_hsv["V_min"] = hsv_range["v_min"]
        green_hsv["V_max"] = hsv_range["v_max"]

    if os.path.exists("new.txt"):
        os.remove("new.txt")

    with open("val.txt", "w") as file:
        file.write(str(red_hsv["H_min"]) + "\n")
        file.write(str(red_hsv["H_max"]) + "\n")
        file.write(str(red_hsv["S_min"]) + "\n")
        file.write(str(red_hsv["S_max"]) + "\n")
        file.write(str(red_hsv["V_min"]) + "\n")
        file.write(str(red_hsv["V_max"]) + "\n")

        file.write(str(green_hsv["H_min"]) + "\n")
        file.write(str(green_hsv["H_max"]) + "\n")
        file.write(str(green_hsv["S_min"]) + "\n")
        file.write(str(green_hsv["S_max"]) + "\n")
        file.write(str(green_hsv["V_min"]) + "\n")
        file.write(str(green_hsv["V_max"]) + "\n")


    # Return the filtered image path and output values
    return jsonify({"success": "Filters applied and images saved."}), 200

#THIS IS A TEMP FUNCTION THIS NEEDS TO BE CHANGED TODAY
@app.route('/capture/<color>', methods=['GET'])
def capture_color(color):
    if color in ['red', 'green', 'blue']:
        return jsonify(success=True)
    else:
        return jsonify(success=False), 400

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
	# thread = threading.Thread(target=background_loop, daemon=True)
	# thread.start()
	app.run(debug=True, threaded=True)
