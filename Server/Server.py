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


@app.route('/process_data', methods=['POST'])
def process_data():
    print("processing data")
    intervals = {'green':60, 'orange':20, 'red':5}
    fall = False

    room_no = request.json.get('room_no')
    user_age = request.json.get('user_age')
    
    bpm = request.json.get('bpm')
    temp_c = request.json.get('temp')
    frame1_list = request.json.get('frame1')
    frame2_list = request.json.get('frame2')

    # Convert lists back to NumPy arrays
    frame1 = np.array(frame1_list, dtype=np.uint8)
    frame2 = np.array(frame2_list, dtype=np.uint8)

    # Process frames
    angle1 = process_frame(frame1)
    angle2 = process_frame(frame2)

    # status is unchanged -- abs(angle1) > 40 OR abs(angle2) > 40
    if angle1 is not None and angle2 is not None:
        if abs(angle1) < 40 or abs(angle2) < 40:
            fall = True
    else:
        # Increase status if not enough info for decision
        # This creates bias towards false positives to avoid false negatives
        fall = True
    
    status = decide_status(bpm, temp_c, fall)
        
    store_observation(room_no, user_age, bpm, temp_c, fall, status)
    print(f"Processed data | Room Number: {room_no}, User Age: {user_age}, BPM: {bpm}, Temperature: {temp_c}, Fall: {fall}, Status: {status}")

    return jsonify({'message': "Data successfully processed", "delay":intervals[status]}), 200


def store_observation(room_no, user_age, bpm, temp, fall, status):
    # Insert room data into the database if not exists
    room_result = db.get_room_by_no(room_no)
    if not room_result:
        db.add_room(room_no, user_age)


    # Insert observation data into the database
    db.add_observation(room_no, bpm, temp, fall, status)


def decide_status(bpm, temp_c, fall):
    print(f"DECIDING STATUS OF: {bpm}, {temp_c}, {fall}")
    status = 0

    # Status is unchanged -- 60 < BPM < 100
    if 50 < bpm < 60 or 100 < bpm < 150: # Bradycardia or tachycardia
        status += 1
    elif bpm < 50 or bpm > 150: # Extreme bradycardia or tachycardia
        status += 2

    # status is unchanged -- 19C < TEMP_C < 23C
    if 18 < temp_c < 19 or 23 < temp_c < 24: # Harmful temperature range
        status += 1
    elif 17 < temp_c < 18 or 24 < temp_c < 25: # More harmful temperature range
        status += 2

    if fall:
        status += 1
    
    print(f"STATUS: {status}")
    # Return status
    if status == 0:
        return "green"
    elif status == 1:
        return "orange"
    else:
        return "red"


def calculate_trendline_angle(points):
    print(f"POINTS: {points}")

    # Filter out points with null values
    filtered_points = [point for point in points if point is not None]

    if len(filtered_points) > (len(points) / 3) * 2: # more than 2/3 of points must be recognised to make prediction

        # Extract x and y coordinates from the filtered points
        x = np.array([point[0] for point in filtered_points])
        y = np.array([point[1] for point in filtered_points])

        # Perform linear regression to find the trendline
        slope, _, _, _, _ = linregress(x, y)

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
    return calculate_trendline_angle(points)
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
