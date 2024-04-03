from flask import Flask, jsonify, request
import cv2 as cv
import threading
import requests


app = Flask(__name__)
SERVER_URL = 'http://192.168.0.25:5000' # IP:port of server
cap1 = cv.VideoCapture(0)
cap2 = cv.VideoCapture(1)
collected_data = None

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

    while True:
        _, frame1 = cap1.read()
        _, frame2 = cap2.read()
        collected_data = (frame1, frame2)


def main():
    room_no = get_room_number()
    connect_to_server(room_no, "cameras")
    collect_data()

if __name__ == "__main__":
    main_thread = threading.Thread(target=main)
    main_thread.start()
    app.run(host="0.0.0.0", port=5000)