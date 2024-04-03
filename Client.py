import requests
import json
import time

# Function to send data to PC
def send_data(data):
    url = 'http://192.168.0.25:5000/receive_data'  # Replace <PC_IP_Address> with the IP address of your PC
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print("Response from PC:", response.text)



while True:
    # Your code to collect data from sensors on Raspberry Pi goes here
    # For example:
    # temperature = <function to get temperature data>
    # humidity = <function to get humidity data>
    # Example data to be sent
    data_to_send = {"room_id": 25, "pulse": 60, "temperature_c": 1, "body_temperature" : 1}

    # Send the data to the PC
    send_data(data_to_send)

    # Wait for some time before sending data again
    time.sleep(10)  # Wait for 10 seconds before sending data again
