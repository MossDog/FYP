from flask import Flask, jsonify, request
from scipy.stats import linregress
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
    user_age = request.json.get('user_age')
    client_type = request.json.get('client_type')
    client_ip = request.remote_addr

    # Store client ips
    # client_data structure - {client id: (vitals ip, cameras ip)}
    if client_type == "vitals":

        if client_data and client_id in client_data:
            _, cameras_ip = client_data[client_id]
            client_data[client_id] = (client_ip, cameras_ip)
        else:
            client_data[client_id] = (client_ip, None)

    elif client_type == "cameras":

        if client_id in client_data:
            vitals_ip, _ = client_data[client_id]
            client_data[client_id] = (vitals_ip, client_ip)
        else:
            client_data[client_id] = (client_ip, None)

    print(f"Client {client_id} connected from {client_ip}")

    # Start a separate thread to request data from clients
    print(client_data)
    if client_data[client_id][0] and client_data[client_id][1]:
        threading.Thread(target=request_data, args=(client_id, user_age,)).start()

    return jsonify({'message': f"Client {client_id} connected"}), 200


def request_data(client_id, user_age):
    global client_data
    intervals = {'green':60, 'orange':20, 'red':5}
    while True:

        print("requesting vital data")
        vital_response = requests.get(f"http://{client_data[client_id][0]}:5000/request_data")
        vital_data = vital_response.json()

        bpm = vital_data.get('bpm_avg')
        temp_c = vital_data.get('ir_c')

        print("requesting camera data")
        camera_response = requests.get(f"http://{client_data[client_id][1]}:5000/request_data")
        camera_data = camera_response.json()
        frame1_list = camera_data.get('frame1')
        frame2_list = camera_data.get('frame2')

        # Convert lists back to NumPy arrays
        frame1 = np.array(frame1_list, dtype=np.uint8)
        frame2 = np.array(frame2_list, dtype=np.uint8)

        # Process frames
        points1 = process_frame(frame1)
        points2 = process_frame(frame2)

        angle1 = abs(calculate_trendline_angle(points1))
        angle2 = abs(calculate_trendline_angle(points2))

        fall = False
        # status is unchanged -- abs(angle1) > 40 OR abs(angle2) > 40
        if angle1 is not None and angle2 is not None:
            if abs(angle1) < 40 or abs(angle2) < 40:
                fall = True
        else:
            # Increase status if not enough info for decision
            # This creates bias towards false positives to avoid false negatives
            fall = True

        status = decide_status(bpm, temp_c, fall)
        
        store_observation(client_id, user_age, bpm, temp_c, fall, status)

        time.sleep(intervals[status])


def store_observation(room_no, user_age, bpm, temp, fall, status):
    # Insert room data into the database if not exists
    room_result = db.get_room_by_id(room_no).fetchone()
    if not room_result:
        db.add_room(room_no, user_age)


    # Insert observation data into the database
    db.add_observation(room_no, bpm, temp, fall, status)


def decide_status(bpm, temp_c, fall):
    status = 0

    # Status is unchanged -- 60 < BPM < 100
    if 50 < bpm < 60 or 100 < bpm < 150: # Bradycardia or tachycardia
        status += 1
    elif bpm < 50 or bpm > 150: # Extreme bradycardia or tachycardia
        status += 2

    # status is unchanged -- 19C < TEMP_C < 23C
    if 18 < temp_c < 24:
        status += 1
    elif 17 < temp_c < 25:
        status += 2

    if fall:
        status += 1
    
    # Return status
    if status == 0:
        return "green"
    elif status == 1:
        return "orange"
    else:
        return "red"


def calculate_trendline_angle(points):
    # Filter out points with null values
    filtered_points = [point for point in points if None not in point]

    if len(filtered_points) > (len(points) / 3) * 2: # more than 2/3 of points must be recognised to make prediction

        # Extract x and y coordinates from the filtered points
        x = np.array([point[0] for point in filtered_points])
        y = np.array([point[1] for point in filtered_points])

        # Perform linear regression to find the trendline
        slope, intercept, _, _, _ = linregress(x, y)

        # Calculate the angle of the trendline
        angle_radians = np.arctan(slope)

        # Convert angle from radians to degrees
        angle_degrees = np.degrees(angle_radians)

        return angle_degrees
    
    else:
        return None


def process_frame(frame):
    BODY_PARTS = { "Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
                "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
                "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
                "LEye": 15, "REar": 16, "LEar": 17, "Background": 18 }

    POSE_PAIRS = [ ["Neck", "RShoulder"], ["Neck", "LShoulder"], ["RShoulder", "RElbow"],
                ["RElbow", "RWrist"], ["LShoulder", "LElbow"], ["LElbow", "LWrist"],
                ["Neck", "RHip"], ["RHip", "RKnee"], ["RKnee", "RAnkle"], ["Neck", "LHip"],
                ["LHip", "LKnee"], ["LKnee", "LAnkle"], ["Neck", "Nose"], ["Nose", "REye"],
                ["REye", "REar"], ["Nose", "LEye"], ["LEye", "LEar"] ]
    
    threshold = 0.2
    frame_dim = 368

    net = cv.dnn.readNetFromTensorflow("graph_opt.pb")

    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]

    net.setInput(cv.dnn.blobFromImage(frame, 1.0, (frame_dim, frame_dim), (127.5, 127.5, 127.5), swapRB=True, crop=False))
    out = net.forward()
    out = out[:, :19, :, :]  # MobileNet output [1, 57, -1, -1], we only need the first 19 elements

    assert(len(BODY_PARTS) == out.shape[1])

    points = []
    for i in range(len(BODY_PARTS)):
        # Slice heatmap of corresponging body's part.
        heatMap = out[0, i, :, :]

        # Find global maxima
        _, conf, _, point = cv.minMaxLoc(heatMap)
        x = (frameWidth * point[0]) / out.shape[3]
        y = (frameHeight * point[1]) / out.shape[2]
        # Add a point if it's confidence is higher than threshold.
        points.append((int(x), int(y)) if conf > threshold else None)
        points[-1] = None
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
