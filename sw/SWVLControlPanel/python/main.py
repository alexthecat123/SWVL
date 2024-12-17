from flask import Flask, request
from flask_cors import CORS
import threading
import time
import cv2
import serial
import sys
import tracking
import queue

command_queue = queue.Queue()
receive_queue = queue.Queue()

tracking_thread = threading.Thread(target=tracking.tracking_loop, args=(command_queue, receive_queue, ))

app = Flask(__name__)
CORS(app)

@app.route("/test-function")
def test_function():
    string = request.args.get('string')
    return {"result": "The string you gave me was: " + string}

@app.route("/start-tracking")
def start_tracking(): # Starts tracking on the connected gimbal. Returns 0 on failure, 1 on success.
    command_queue.put('start_tracking')
    while receive_queue.qsize() == 0:
        pass
    result = receive_queue.get()
    if result == 1:
        print("Host program: 'Start tracking' command succeeded!")
        return "1"
    elif result == 0:
        print("Host progtam: 'Start tracking' command failed!")
        return "0"
    else:
        print("Host program: Something weird happened when sending the 'start tracking' command.")
        return "0"

@app.route("/stop-tracking")
def stop_tracking(): # Stops tracking on the connected gimbal. Returns 0 on failure, 1 on success.
    command_queue.put('stop_tracking')
    while receive_queue.qsize() == 0:
        pass
    result = receive_queue.get()
    if result == 1:
        print("Host program: 'Stop tracking' command succeeded!")
        return "1"
    elif result == 0:
        print("Host progtam: 'Stop tracking' command failed!")
        return "0"
    else:
        print("Host program: Something weird happened when sending the 'stop tracking' command.")
        return "0"

@app.route("/serial-connect")
def serial_connect(): # Tries to connect to a gimbal on port "port". Returns 0 on failure, 1 on success.
    port = request.args.get('port')
    command_queue.put("port")
    command_queue.put(port)
    while receive_queue.qsize() == 0:
        pass
    result = receive_queue.get()
    if result == 1:
        print("Host program: Gimbal connection succeeded!")
        return "1"
    elif result == 0:
        print("Host program: Gimbal connection failed or device wasn't actually a gimbal!")
        return "0"
    else:
        print("Host program: Something weird happened with trying to connect to the gimbal.")
        return "0"
    
@app.route("/serial-disconnect")
def serial_disconnect(): # Tries to disconnect from the gimbal. Returns 1 on success, 0 on failure
    command_queue.put("disconnect")
    while receive_queue.qsize() == 0:
        pass
    result = receive_queue.get()
    if result == 1:
        print("Host program: Gimbal disconnection succeeded!")
        return "1"
    elif result == 0:
        print("Host progtam: Gimbal disconnection failed!")
        return "0"
    else:
        print("Host program: Something weird happened with disconnecting the gimbal.")
        return "0"
    
@app.route("/connection-status")
def connection_status(): # Queries the serial connection status of the gimbal. Returns 0 if disconnected, 1 if connected
    command_queue.put("conn_status")
    while receive_queue.qsize() == 0:
        pass
    status = receive_queue.get()
    if status == 1:
        print("Host program: Gimbal status is 'connected'.")
        return "1"
    elif status == 0:
        print("Host progtam: Gimbal status is 'disconnected'.")
        return "0"
    else:
        print("Host program: Something weird happened with getting gimbal connection status.")
        return "0"


if __name__ == "__main__":
    tracking_thread.start()
    app.run(debug=False, host="0.0.0.0", port="5000")    