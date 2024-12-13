import cv2
import serial
import sys
import time
#from matplotlib import pyplot as plt

try:
    gimbal = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
except:
    print('Failed to connect to gimbal!')
    sys.exit()

cam = cv2.VideoCapture(3)

cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

deadzone_width = 150
deadzone_height = 150
step_size = 1

while True:
    ret, frame = cam.read()
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
    face_data = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

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

    cv2.imshow('Camera', frame)


    if cv2.waitKey(1) == ord('q'):
        gimbal.write(bytes('DS', 'utf8'))
        break


cam.release()
cv2.destroyAllWindows()