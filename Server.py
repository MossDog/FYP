from flask import Flask, jsonify, request
from DbDao import DbDao
import numpy as np
import cv2 as cv
import threading
import requests
import time


# Initialize Flask Object
app = Flask(__name__)

# Initialize Database DAO Object
db = DbDao()

client_data  = {}

@app.route('/receive_data', methods=['POST'])
def receive_data():
    data = request.json  # Assuming the data is sent in JSON format

    # Extract data fields
    room_no = data.get('room_no')
    bpm = data.get('bpm')
    bpm_avg = data.get('bpm_avg')
    ir_c = data.get('ir_c')

    #Decide status
    status = decide_status(bpm, ir_c)

    print(f"Room: {room_no}\nBPM: {bpm}\nAverage BPM: {bpm_avg}\nIR Temp: {ir_c}")
    
    # Insert room data into the database if not exists
    room_result = db.get_room_by_id(room_no).fetchone()
    if not room_result:
        # FIGURE OUT WHAT TO DO WITH NAME/ROOMTABLE STUFF
        db.add_room(room_no, "PLACEHOLDER NAME")


    # Insert observation data into the database
    db.add_observation(room_no, bpm, bpm_avg, ir_c, status)


    print("Received data from client and stored in the database:", data)
    return "Data received and stored successfully"

@app.route('/connect', methods=['POST'])
def handle_connect():
    global client_data

    client_id = request.json.get('room_no')
    client_type = request.json.get('client_type')
    client_ip = request.remote_addr

    # Store client ips
    # client_data structure - {client id: (vitals ip, cameras ip)}
    if client_type == "vitals":
        print("here 1")
        if client_data and client_id in client_data:
            print("here 2")
            _, cameras_ip = client_data[client_id]
            client_data[client_id] = (client_ip, cameras_ip)
        else:
            print("here 3")
            client_data[client_id] = (client_ip, None)
    elif client_type == "cameras":
        if client_id in client_data:
            vitals_ip, _ = client_data[client_id]
            client_data[client_id] = (vitals_ip, client_ip)
        else:
            client_data[client_id] = (client_ip, None)

    print(f"Client {client_id} connected from {client_ip}")
    print(type(client_ip))

    # Start a separate thread to request data from clients
    print(client_data)
    if client_data[client_id][0] and client_data[client_id][1]:
        threading.Thread(target=request_data, args=(client_id,)).start()

    return jsonify({'message': f"Client {client_id} connected"}), 200


def request_data(client_id):
    global client_data
    while True:

        print("requesting vital data")
        vital_response = requests.get(f"http://{client_data[client_id][0]}:5000/request_data")
        print(vital_response.json())
        print("requesting camera data")
        camera_response = requests.get(f"http://{client_data[client_id][1]}:5000/request_data")
        data = camera_response.json()
        frame1_list = data.get('frame1')
        frame2_list = data.get('frame2')

        # Convert lists back to NumPy arrays
        frame1 = np.array(frame1_list, dtype=np.uint8)
        frame2 = np.array(frame2_list, dtype=np.uint8)
         # Process the data (e.g., display frames)
        cv.imshow('Frame 1', frame1)
        cv.imshow('Frame 2', frame2)
        cv.waitKey(0)
        cv.destroyAllWindows()
        status = decide_status(vital_response, camera_response)
        # store data in db here
        time.sleep(5)


def decide_status(bpm, ir_c):
    return None
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
