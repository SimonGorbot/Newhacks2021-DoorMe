import PySimpleGUI as sg
import qrcode
import os
import shutil
import cv2
from pyzbar import pyzbar
import numpy as np
import serial
import time

# G U I   C O D E   S T A R T ==========================================================================================
sg.theme('Dark')
layout = [
    [sg.Text('Enter a folder path for the QR codes')],
    [sg.InputText()],
    [sg.Text('Welcome to ____ :) Please enter your guest list below.')],
    [sg.InputText(default_text="First Last, First Last, etc.", tooltip="First Last, First Last, etc.", expand_y=True)],
    [sg.Submit(button_text="Generate QR Codes")]
]
window = sg.Window('DoorMe', layout)
while True:
    event, values = window.read()
    if event == 'Generate QR Codes':
        file_path = values.get(0)
        guests = values.get(1)
        guest_list = list(map(str, guests.split(', ')))
        for name in guest_list:
            img_qrcode = qrcode.make(name)
            img_qrcode.save(name+".jpeg")
            project_path = os.path.dirname(os.path.abspath(f"{name}.jpeg"))
            shutil.move(project_path + "\\" + name + ".jpeg", file_path + "\\" + name + ".jpeg")
        break
    if event in sg.WIN_CLOSED:
        break
window.close()
# G U I   C O D E   E N D ==============================================================================================

acceptedNames = guest_list
print("connecting")
# define a video capture object
vid = cv2.VideoCapture("http://192.168.137.134:8080/video")
print("connected")
counter = 0

K = np.array([[550, 0., 500],
              [0., 550, 500],
              [0., 0., 1.]])

D = np.array([0., 0., 0., 0.])

# use Knew to scale the output
Knew = K.copy()
Knew[(0, 1), (0, 1)] = 0.4 * Knew[(0, 1), (0, 1)]
alternating = 0

serialPort = serial.Serial(
    port="COM4", baudrate=115200, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE
)
serialString = ""  # Used to hold data coming over UART
time.sleep(1)


def sendCommand(cmd):
    serialPort.write(bytes(cmd, 'utf-8'))
    time.sleep(1)


while serialPort.in_waiting > 0:
    # Wait until there is data waiting in the serial buffer

    # Read data out of the buffer until a carraige return / new line is found
    serialString = serialPort.readline()

    # Print the contents of the serial data
    try:
        print(serialString.decode("Ascii"))
    except:
        pass
sendCommand("U")
while True:
    ret, frame = vid.read()
    if alternating == 5:
        alternating = 0
    else:
        alternating += 1
        continue
    # Capture the video frame
    # by frame

    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE);

    frame = frame[500:500 + 1000, 100:100 + 1000]

    # Display the resulting frame

    frame = cv2.fisheye.undistortImage(frame, K, D=D, Knew=Knew)
    frame = frame[200:200 + 600, 200:200 + 600]

    barcodes = pyzbar.decode(frame)
    if len(barcodes) > 0:
        print(barcodes[0].data.decode('utf-8'))
        for i in acceptedNames:
            if barcodes[0].data.decode('utf-8') == i:
                sendCommand("U")
        if barcodes[0].data.decode('utf-8') == "Lock":
            sendCommand("L")
    cv2.imshow('corrected', frame)
    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vid.release()
cv2.destroyAllWindows()