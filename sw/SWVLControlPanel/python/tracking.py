import cv2
import serial
import sys
import os
import time
#from matplotlib import pyplot as plt

track_face = False
disconnect = False

def get_commands(commands, transmit):
        global track_face
        global disconnect
        if commands.qsize():
            command = commands.get()
            if command == "start_tracking":
                track_face = True
                transmit.put(1)
                print("Starting tracking!")
            elif command == "stop_tracking":
                track_face = False
                transmit.put(1)
                print("Stopping tracking!")
            elif command == "conn_status":
                print("Requesting connection status, which is 'connected'.")
                transmit.put(1)
            elif command == "disconnect":
                print("Disconnecting from gimbal.")
                disconnect = True
            elif command == "port":
                print("Got a serial connection request, but we're already connected!")
                while commands.qsize():
                    commands.get()
                transmit.put(0)


def tracking_loop(commands, transmit):
    global track_face
    global disconnect
    while True:
        track_face = False # default values after a reset
        disconnect = False
        if commands.qsize():
            command = commands.get()
            if command == "port":
                print("Got a gimbal connection command!")
                while commands.qsize() == 0:
                    pass
                port = commands.get()
                print("Gimbal is on port " + port)
                try:
                    print("Trying to connect to device...")
                    gimbal = serial.Serial(port, 115200, timeout=1)
                    print("Success!")
                    time.sleep(2)
                    gimbal.write(bytes('ID', 'utf8'))
                    ID = int(gimbal.read(2))
                    if(ID == 69):
                        print("And device is actually a gimbal!")
                        transmit.put(1)
                        break
                    else:
                        print("But device is NOT actually a gimbal! Disconnecting...")
                        gimbal.close()
                        transmit.put(0)
                except:
                    print('Failed! Waiting for another device connection command...')
                    transmit.put(0)
            else: # Any other command should return a 0 at this point; we can't do anything until we're connected!
                while commands.qsize():
                    commands.get()
                transmit.put(0)

    try:

        cam = cv2.VideoCapture(3)

        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        deadzone_width = 150
        deadzone_height = 150
        step_size = 1

        if getattr(sys, 'frozen', False): # pyinstaller puts files in a temp folder with path _MEIPASS, so we have to join that with our filename if we're in pyinstaller
            face_data = cv2.CascadeClassifier(os.path.join(sys._MEIPASS, "files/haarcascade_frontalface_default.xml"))
        else:
            face_data = cv2.CascadeClassifier("haarcascade_frontalface_default.xml") # else just load the file as normal


        while True:
            gimbal.write(bytes('DN', 'utf8')) # 'DoNothing', a stupid hack so that pyserial knows immediately when the gimbal disconects since we're always sending it a command
            get_commands(commands, transmit)
            if disconnect == True:
                disconnect = False
                gimbal.close()
                cam.release()
                cv2.destroyAllWindows()
                transmit.put(1)
                tracking_loop(commands, transmit)
            ret, frame = cam.read()
            if track_face:
                height, width = frame.shape[:2]
                height_center = int(height / 2)
                width_center = int(width / 2)
                # OpenCV opens images as BRG 
                # but we want it as RGB We'll 
                # also need a grayscale version
                img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Use minSize because for not 
                # bothering with extra-small 
                # dots that would look like STOP signs

                found = face_data.detectMultiScale(img_gray, 
                                            minSize =(20,20))

                # Don't do anything if there's 
                # no sign
                amount_found = len(found)
                
                if amount_found != 0:
                    face = found[0]
                    largest_area = 0
                    # There may be more than one
                    # sign in the image
                    for i, (x, y, width, height) in enumerate(found):
                        if width * height > largest_area:
                            largest_area = width * height 
                            face = found[i]
                        # We draw a green rectangle around
                        # every recognized sign
                        #cv2.rectangle(frame, (x, y), (x + height, y + width), (0, 255, 0), 5)
                    (x, y, width, height) = face

                    if x >= (width_center - deadzone_width) and y >= (height_center - deadzone_height) and (x + width) <= (width_center + deadzone_width) and (y + height) <= (height_center + deadzone_height):
                        print("In deadzone!")
                        delta_x = 0
                        delta_y = 0
                        cv2.rectangle(frame, (x, y), (x + height, y + width), (0, 255, 0), 5)
                    else:
                        delta_x = width_center - (x + (width/2))
                        delta_y = height_center - (y + (height/2))
                        print("Delta X: " + str(delta_x))
                        print("Delta Y: " + str(delta_y))
                        cv2.rectangle(frame, (x, y), (x + height, y + width), (0, 0, 255), 5)
                    if x >= (width_center - deadzone_width) and (x + width) <= (width_center + deadzone_width):
                        delta_x = 0
                    if y >= (height_center - deadzone_height) and (y + height) <= (height_center + deadzone_height):
                        delta_y = 0


                    if delta_x < 0:
                        gimbal.write(bytes('PR', 'utf8'))
                        gimbal.write(step_size.to_bytes(2, byteorder='big', signed=True))
                    elif delta_x > 0:
                        gimbal.write(bytes('PR', 'utf8'))
                        gimbal.write((-1*step_size).to_bytes(2, byteorder='big', signed=True))
                    if delta_y < 0:
                        gimbal.write(bytes('TR', 'utf8'))
                        gimbal.write(step_size.to_bytes(2, byteorder='big', signed=True))
                    elif delta_y > 0:
                        gimbal.write(bytes('TR', 'utf8'))
                        gimbal.write((-1*step_size).to_bytes(2, byteorder='big', signed=True))


                cv2.rectangle(frame, ((width_center - deadzone_width), (height_center - deadzone_height)), 
                                    ((width_center + deadzone_width), (height_center + deadzone_height)),
                                    (0, 0, 255), 5)
            else:
                gimbal.write(bytes('DS', 'utf8'))
            cv2.imshow('Camera', frame)

            if cv2.waitKey(1) == ord('q'):
                break
        cam.release()
        cv2.destroyAllWindows()

    except serial.serialutil.SerialException:
        print("Error: Serial port disconnected! Waiting for new connection.")
        gimbal.close()
        cam.release()
        cv2.destroyAllWindows()
        tracking_loop(commands, transmit)