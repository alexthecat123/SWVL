import serial
import argparse
import sys
import math
import os

# make homing commands block so that host knows when gimbal is homes

def homeBoth():
    os.system('clear')
    print('This command is currently not implemented in the hardware. Sending command HA anyway.')
    gimbal.write(bytes('HA', 'utf8'))
    print()
    input('Press return to continue...')
    mainMenu()

def homePan():
    os.system('clear')
    print('This command is currently not implemented in the hardware. Sending command HP anyway.')
    gimbal.write(bytes('HP', 'utf8'))
    print()
    input('Press return to continue...')
    mainMenu()

def homeTilt():
    os.system('clear')
    print('This command is currently not implemented in the hardware. Sending command 0000001000000000 anyway.')
    gimbal.write(bytes('HT', 'utf8'))
    print()
    input('Press return to continue...')
    mainMenu()

def movePan():
    os.system('clear')
    while True:
        stepCount = int(input('Enter the number of steps to pan the gimbal (positve for CW, negative for CCW): '))
        if abs(stepCount) < 32767:
            break
    if(stepCount < 0):
        print('Moving pan axis CCW by ' + str(abs(stepCount)) + ' steps. Command: PR' + str(stepCount))
    else:
        print('Moving pan axis CW by ' + str(abs(stepCount)) + ' steps. Command: PR' + str(stepCount))
    gimbal.write(bytes('PR', 'utf8'))
    gimbal.write(stepCount.to_bytes(2, byteorder='big', signed=True))
    print()
    input('Press return to continue...')
    mainMenu()

def moveTilt():
    os.system('clear')
    while True:
        stepCount = int(input('Enter the number of steps to tilt the gimbal (positve for up, negative for down): '))
        if abs(stepCount) < 32767:
            break
    if(stepCount < 0):
        print('Moving tilt axis down by ' + str(abs(stepCount)) + ' steps. Command: TR' + str(stepCount))
    else:
        print('Moving tilt axis up by ' + str(abs(stepCount)) + ' steps. Command: TR' + str(stepCount))
    gimbal.write(bytes('TR', 'utf8'))
    gimbal.write(stepCount.to_bytes(2, byteorder='big', signed=True))
    print()
    input('Press return to continue...')
    mainMenu()

def getPanAngle():
    os.system('clear')
    print('Requesting current pan angle from gimbal. Command: GP')
    gimbal.write(bytes('GP', 'utf8'))
    response = int.from_bytes(gimbal.read(2), "big", signed=True)
    print('Current pan angle is ' + str(response) + ' degrees.')
    print()
    input('Press return to continue.')
    mainMenu()

def getTiltAngle():
    os.system('clear')
    print('Requesting current tilt angle from gimbal. Command: GT')
    gimbal.write(bytes('GT', 'utf8'))
    response = gimbal.read(2)
    print('Current tilt angle is ' + response + ' degrees.')
    print()
    input('Press return to continue.')
    mainMenu()

def playSandstorm():
    os.system('clear')
    print('This command is currently not implemented in the hardware. Sending command PS anyway.')
    gimbal.write(bytes('PS', 'utf8'))
    print()
    input('Press return to continue...')
    mainMenu()

def stopSandstorm():
    os.system('clear')
    print('This command is currently not implemented in the hardware. Sending command SS anyway.')
    gimbal.write(bytes('SS', 'utf8'))
    print()
    input('Press return to continue...')
    mainMenu()

def mainMenu():
    os.system('clear')
    print('Main Menu')
    print('1 - Home Both Axes')
    print('2 - Home Pan Axis')
    print('3 - Home Tilt Axis')
    print('4 - Move Pan Axis')
    print('5 - Move Tilt Axis')
    print('6 - Get Current Pan Angle')
    print('7 - Get Current Tilt Angle')
    print('8 - Start Playing Sandstorm')
    print('9 - Stop Playing Sandstorm')
    print('A - Exit')
    print()
    print()
    choice = input('Please enter an option: ')
    match choice:
        case '1':
            homeBoth()
        case '2':
            homePan()
        case '3':
            homeTilt()
        case '4':
            movePan()
        case '5':
            moveTilt()
        case '6':
            getPanAngle()
        case '7':
            getTiltAngle()
        case '8':
            playSandstorm()
        case '9':
            stopSandstorm()
        case 'a':
            os.system('clear')
            sys.exit()
    mainMenu()

parser = argparse.ArgumentParser(prog='gimbalControllerTester', description='Some tests for the SWVL gimbal control hardware')
parser.add_argument('serialPort', help='the serial port that the gimbal is connected to')

args = parser.parse_args()

try:
    gimbal = serial.Serial(args.serialPort, 115200, timeout=1)
except:
    print('Failed to connect to gimbal!')
    sys.exit()

mainMenu()