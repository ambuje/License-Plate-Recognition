##import numpy as np
##suzuki , eco , scoda
import cv2

cap = cv2.VideoCapture('eco.mp4')

car_cascade = cv2.CascadeClassifier('cars2.xml') 


while True: 


    ret, frames = cap.read() 


    gray = cv2.cvtColor(frames, cv2.COLOR_BGR2GRAY) 

    cars = car_cascade.detectMultiScale(gray, 1.1, 1) 


    for (x,y,w,h) in cars: 

        x=cv2.rectangle(frames,(x,y),(x+w,y+h),(255,255,255),2)
        ##s, im = cap.read()
        cv2.imwrite("test.bmp",x)

    cv2.imshow('frame', frames)

    if cv2.waitKey(33) == 27: 

        break

cap.release()

cv2.destroyAllWindows()

import main_main
main_main.main()
