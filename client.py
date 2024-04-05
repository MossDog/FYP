from flask import Flask, jsonify, request
from max30105 import MAX30105, HeartRate
from smbus2 import SMBus
from mlx90614 import MLX90614
import threading
import requests
import json
import time

# IP:port of server
SERVER_URL = 'http://192.168.0.25:5000' 

# Set up flask app
app = Flask(__name__)

# Set up temperature sensor
bus = SMBus(1)
sensor = MLX90614(bus, address=0x5A)

# Set up and configure pulse sensor
max30105 = MAX30105()
max30105.setup(leds_enable=2)

max30105.set_led_pulse_amplitude(1, 0.2)
max30105.set_led_pulse_amplitude(2, 12.5)
max30105.set_led_pulse_amplitude(3, 0)

max30105.set_slot_mode(1, 'red')
max30105.set_slot_mode(2, 'ir')
max30105.set_slot_mode(3, 'off')
max30105.set_slot_mode(4, 'off')

hr = HeartRate(max30105)

collected_data = None

'''
# Function to send data to PC
def send_data(data):
    url = 'http://192.168.0.25:5000/receive_data'  # IP:port/route of server
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print("Response from PC:", response.text)
'''


@app.route('/request_data', methods=['GET'])
def send_data():
	global collected_data
	return jsonify(collected_data)
	

def get_room_number():
	while True:
			room_no = input("Please enter the number of the room being monitored")
			while True:
				print(f"You entered: {room_no}")
				confirmation = input("Is this correct? (Y/N)").lower()
				if confirmation == "y":
					return room_no
				elif confirmation == "no":
					break
				else:
					print("Invalid input. Please enter 'y' or 'n'")


def connect_to_server(room_no, client_type):
	data = {"room_no":room_no, "client_type":client_type}
	response = requests.post(f"{SERVER_URL}/connect", json=data)
	print("Response from server: ", response.text)


def collect_data():
	global collected_data
	
	average_over=4
	delay=3
	bpm_vals = [0 for x in range(average_over)]
	last_beat = time.time()
	last_update = time.time()
	bpm = 0
	bpm_avg = 0
	beat_detected = False
	
	while True:
		t = time.time()

		# Ensure samples have been taken
		samples = hr.max30105.get_samples()
		if samples is None:
			continue

		for sample_index in range(0, len(samples), 2):
			sample = samples[sample_index + 1]
			if hr.check_for_beat(sample):
				delta = t - last_beat
				last_beat = t
				bpm = 60 / delta
				bpm_vals = bpm_vals[1:] + [bpm]
				bpm_avg = sum(bpm_vals) / average_over

		if t - last_update >= delay:
			# Get temperature data
			ir_c = (round(sensor.get_object_1(),2))
			contact_c = round(sensor.get_ambient(), 2) #\N{DEGREE SIGN}C is useful
		
			# Store data for request
			collected_data = {"bpm_avg": bpm_avg, "ir_c": ir_c}
				
			last_update = t
        
def main():
	room_no = get_room_number()
	connect_to_server(room_no, "vitals")
	collect_data()
	
	
		
if __name__ == "__main__":
	main_thread = threading.Thread(target=main)
	main_thread.start()
	
	app.run(host="0.0.0.0", port=5000)
