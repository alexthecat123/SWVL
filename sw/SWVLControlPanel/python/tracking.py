import cv2
import serial
import sys
import os
import time
from nmsupr import non_max_supp
from model import FaceDetector
import torch
from torchvision import transforms

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
device = torch.device('mps' if torch.backends.mps.is_available() else device)

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
                except Exception as e:
                    print('Failed! Waiting for another device connection command...')
                    print("Error: " + str(e))
                    transmit.put(0)
            else: # Any other command should return a 0 at this point; we can't do anything until we're connected!
                while commands.qsize():
                    commands.get()
                transmit.put(0)

    try:
        cam = cv2.VideoCapture(0)

        cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        deadzone = 50
        step_size = 1

        '''if getattr(sys, 'frozen', False): # pyinstaller puts files in a temp folder with path _MEIPASS, so we have to join that with our filename if we're in pyinstaller
            PATH_TO_MODEL = os.path.join(sys._MEIPASS, "files/mobileNetV3_backbone_test.pth")
        else:
            PATH_TO_MODEL = "mobileNetV3_backbone_test.pth" # else just load the file as normal'''
        
        #PATH_TO_MODEL = "mobileNetV3_backbone_test.pth"
        PATH_TO_MODEL = 'best_dev_loss0476_dsc.pth'

        model = FaceDetector()
        print('Loading model...')
        model.load_state_dict(torch.load(PATH_TO_MODEL, weights_only=True, map_location=torch.device('cpu')))
        print(f'Done! Using device {device}...')
        model = model.to(device)
        model.eval()

        transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize((448,448), antialias=True),  # Resize all images to same dimensions
        # transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        x, y, width, height = 0, 0, 0, 0
        firstTime = False
        while True:
            get_commands(commands, transmit)
            #gimbal.write(bytes('DN', 'utf8')) # 'DoNothing', a stupid hack so that pyserial knows immediately when the gimbal disconects since we're always sending it a command
            if disconnect == True:
                disconnect = False
                gimbal.close()
                cam.release()
                cv2.destroyAllWindows()
                transmit.put(1)
                tracking_loop(commands, transmit)
            ret, frame = cam.read()
            if track_face:
                startTime = time.time()
                if not firstTime:
                    gimbal.write(bytes('PR', 'utf8'))
                    gimbal.write((0).to_bytes(2, byteorder='big', signed=True))
                firstTime = True
                hei, wid = frame.shape[:2]
                height_center = int(hei / 2)
                width_center = int(wid / 2)
                
                frame_transform = transform(frame)
                frame_transform = frame_transform.unsqueeze(dim=0)
                frame_transform = frame_transform.to(device)
                preds = model(frame_transform)
                preds = preds.cpu()
                preds = preds.view(-1, 7, 7, 10)
                #can mess with confidence and iou thresholds for different results
                found = non_max_supp(preds, confidence_threshold = 0.5, iou_threshold=0.2, S=7, return_type='xyxy')

                # Don't do anything if there's 
                # no face detected
                amount_found = len(found[0])
                
                if amount_found != 0:
                    largest_area = 0
                    for i in found[0]:
                        conf, x1, y1, x2, y2 = i
                        xa, ya, w, h = x1*wid, y1*hei, x2*wid, y2*hei
                        #print(f'face found: {conf}, {xa}, {ya}, {w}, {h}')
                        if abs((w-x)*(h-y)) > largest_area:
                            largest_area = abs((w-x)*(h-y))
                            x, y, width, height = int(xa), int(ya), int(w), int(h)
                    print(f'Largest face found: x1 = {x}, y1 = {y}, x2 = {width}, y2 = {height}')

                    delta_x = width_center - (x + ((width-x)/2))
                    delta_y = height_center - (y + ((height-y)/2))

                    if abs(delta_x) <= deadzone and abs(delta_y) <= deadzone:
                        print("In deadzone!")
                        delta_x = 0
                        delta_y = 0
                        cv2.rectangle(frame, (x, y), (width, height), (0, 255, 0), 5)
                    else:
                        print("dX: " + str(delta_x))
                        print("dY: " + str(delta_y))
                        cv2.rectangle(frame, (x, y), (width, height), (0, 0, 255), 5)

                    if delta_x < 0:
                        gimbal.write(bytes('PR', 'utf8'))
                        gimbal.write(step_size.to_bytes(2, byteorder='big', signed=True))
                    elif delta_x > 0:
                        gimbal.write(bytes('PR', 'utf8'))
                        gimbal.write((-1*step_size).to_bytes(2, byteorder='big', signed=True))
                    if delta_y > 0:
                        gimbal.write(bytes('TR', 'utf8'))
                        gimbal.write(step_size.to_bytes(2, byteorder='big', signed=True))
                    elif delta_y < 0:
                        gimbal.write(bytes('TR', 'utf8'))
                        gimbal.write((-1*step_size).to_bytes(2, byteorder='big', signed=True))


                '''cv2.rectangle(frame, ((width_center - deadzone_width), (height_center - deadzone_height)), 
                                    ((width_center + deadzone_width), (height_center + deadzone_height)),
                                    (0, 0, 255), 5)'''
                cv2.circle(frame, (width_center, height_center), radius=5, color=(0, 0, 255), thickness=-1)
                frameRate = 1/(time.time() - startTime)
                print(f'Framerate: {frameRate:.2f} FPS')
            else:
                if firstTime:
                    gimbal.write(bytes('DS', 'utf8'))
                    firstTime = False
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