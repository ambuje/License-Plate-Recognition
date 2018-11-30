##import numpy as np
##suzuki , eco , scoda
import cv2
import serial
import gspread
from oauth2client.service_account import ServiceAccountCredentials

try:
    scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]

    credentials = ServiceAccountCredentials.from_json_keyfile_name("rushiliot-c0fef04930d0.json",scope)

    gc = gspread.authorize(credentials)

    wks = gc.open("rpi").sheet1
    try:
        wks.update_cell(1,2,"close")
        print("closed")
    except:
        print("some error in rpi")
except:
    print("some error in connection with gsuit")

try:
    arduinoData = serial.Serial("com8",9600)
except:
    print("port dekho")

while(1==1):
    mydata = (arduinoData.readline().strip())
    x=(int(mydata.decode('utf-8')))
    print(x)
    if(x>10 and x<=30):
        break


cap = cv2.VideoCapture('suzuki2.mp4')

car_cascade = cv2.CascadeClassifier('cars.xml') 



while True: 
    ##print("in loop")
    
    ret, frames = cap.read() 


    gray = cv2.cvtColor(frames, cv2.COLOR_BGR2GRAY) 

    cars = car_cascade.detectMultiScale(gray, 1.1, 1) 


    for (x,y,w,h) in cars: 

        x=cv2.rectangle(frames,(x,y),(x+w,y+h),(255,255,255),2)
        ##s, im = cap.read()
        ##cv2.imwrite("test.bmp",x)

    cv2.imshow('frame', frames)

    mydata = (arduinoData.readline().strip())
    rushil=(int(mydata.decode('utf-8')))
    print(rushil)

    if(rushil<=10):
        cv2.imwrite("test.bmp",x)
        break

    if cv2.waitKey(33) == 27: 
        cv2.imwrite("test.bmp",x)
        break

cap.release()

cv2.destroyAllWindows()

import main_main
main_main.main()
