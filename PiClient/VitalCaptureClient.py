from max30105 import MAX30105, HeartRate
from smbus2 import SMBus
from mlx90614 import MLX90614
import threading
import requests
import json
import time
import os

# IP:port of server
SERVER_URL = 'http://192.168.0.25:5000' 

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

sensor_data = None

# Function to load user data from file or prompt user for new data
def load_user_data():
	file_path = 'user_data.txt'
	if os.path.exists(file_path):
		data = read_user_data(file_path)
		if data and is_valid_data(data):
			print_user_data(data)
			if get_user_option() == 1:
				return data
	return gather_user_input()


# Function to read user data from file
def read_user_data(file_path):
	try:
		with open(file_path, 'r') as file:
			data = file.read().strip().split(',')
			return (int(data[0]), int(data[1])) if len(data) == 2 else None
	except Exception as e:
		print(f"Error reading user_data.txt: {e}")
		return None


# Function to check if user data is valid
def is_valid_data(data):
	return all(x > 0 for x in data)


# Function to print user data and options
def print_user_data(data):
	room_no, user_age = data
	print("\tCURRENT DATA ON FILE\t")
	print(f"Room Number: {room_no}, Person Age: {user_age}")
	print("\n1. Data is up to date\n2. Data is outdated")


# Function to gather new user input
def gather_user_input():
	while True:
		try:
			room_no = int(input("Please enter the room number being monitored: "))
			user_age = int(input("Please enter the age of the person in this room: "))
			if room_no > 0 and user_age > 0:
				print(f"You entered: Room Number: {room_no}, Person Age: {user_age}")
				confirmation = input("Is this correct? (Yes/No): ").lower()
				if confirmation == "yes":
					write_user_data('user_data.txt', room_no, user_age)
					return room_no, user_age
				elif confirmation != "no":
					print("Please enter 'yes' or 'no'")
			else:
				print("Room number and age must be positive integers.")
		except ValueError:
			print("Invalid input. Please enter a valid integer.")
			
			
# Function to get user option
def get_user_option():
	while True:
		try:
			option = int(input("Please select an option: "))
			if option in (1, 2):
				return option
			else:
				print("Invalid option. Please select either 1 or 2.")
		except ValueError:
			print("Invalid input. Please enter a valid integer.")


# Function to write user data to file
def write_user_data(file_path, room_no, user_age):
	with open(file_path, 'w') as file:
		file.write(f"{room_no},{user_age}")


def collect_data():
	global sensor_data
	
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
			
			# Get image data
			_, frame1 = cap1.read()
			_, frame2 = cap2.read()
			
			# Encode image data to send
			frame1_list = frame1.tolist()
			frame2_list = frame2.tolist()
		
			# Store data for processing
			data = {"bpm_avg": bpm_avg, "ir_c": ir_c, "frame1":frame1, "frame2":frame2}
				
			last_update = t
	
	
def send_data(room_no, user_age):
	global sensor_data
	while True:
		data = {"room_no":room_no, "user_age":user_age}
		data.update(sensor_data)
		response = requests.post(f"{SERVER_URL}/process_data", json=data)
		print(response.json().get('message'))
		delay = response.json().get('delay')
		time.sleep(delay)
		
		
def main():
	room_no, user_age = load_user_data()
	send_data(room_no, user_age)
		
				
if __name__ == "__main__":
	data_collection_thread = threading.Thread(target=collect_data)
	data_collection_thread.start()
	main()
	'''
	main_thread = threading.Thread(target=main)
	main_thread.start()
	
	app.run(host="0.0.0.0", port=5000)
	'''
