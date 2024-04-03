from flask import Flask, jsonify, request
from DbDao import DbDao
import threading
import requests
import time


# Initialize Flask Object
app = Flask(__name__)

# Initialize Database DAO Object
db = DbDao()

connected_clients = {}


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
    client_id = request.json.get('room_no')
    client_ip = request.remote_addr
    if client_id:
        connected_clients[client_id] = client_ip
        print(f"Client {client_id} connected from {client_ip}")
        print(type(client_ip))

        # Start a separate thread for the client to send requests
        threading.Thread(target=request_data, args=(client_ip,)).start()

        return jsonify({'message': f"Client {client_id} connected"}), 200
    else:
        return jsonify({'error': 'Client ID not provided'}), 400
    

def request_data(client_ip):
    while True:
        print("requesting data")
        response = requests.get(f"http://{client_ip}:5000/request_data")
        print(response.json())
        time.sleep(5)


def decide_status(bpm, ir_c):
    return None
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
