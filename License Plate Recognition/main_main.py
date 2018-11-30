import cv2
import numpy as np
import os

import DetectChars
import DetectPlates
import PossiblePlate

import pymysql
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# module level variables 
SCALAR_BLACK = (0.0, 0.0, 0.0)
SCALAR_WHITE = (255.0, 255.0, 255.0)
SCALAR_YELLOW = (0.0, 255.0, 255.0)
SCALAR_GREEN = (0.0, 255.0, 0.0)
SCALAR_RED = (0.0, 0.0, 255.0)

showSteps = False

def main():

    blnKNNTrainingSuccessful = DetectChars.loadKNNDataAndTrainKNN()         

    if blnKNNTrainingSuccessful == False:                               
        print("\nerror: KNN traning was not successful\n")  
        return                                                         

    imgOriginalScene  = cv2.imread("test.bmp")               

    if imgOriginalScene is None:                            
        print("\nerror: image not read from file \n\n")  
        os.system("pause")                                  
        return                                              
    # end if

    listOfPossiblePlates = DetectPlates.detectPlatesInScene(imgOriginalScene)           # detect plates

    listOfPossiblePlates = DetectChars.detectCharsInPlates(listOfPossiblePlates)        # detect chars in plates

    cv2.imshow("imgOriginalScene", imgOriginalScene)            

    if len(listOfPossiblePlates) == 0:                          
        print("\nno license plates were detected\n")  
    else:                                                       
               
        listOfPossiblePlates.sort(key = lambda possiblePlate: len(possiblePlate.strChars), reverse = True)

               
        licPlate = listOfPossiblePlates[0]

        cv2.imshow("imgPlate", licPlate.imgPlate)           
        cv2.imshow("imgThresh", licPlate.imgThresh)

        if len(licPlate.strChars) == 0:                     
            print("\nno characters were detected\n\n")  
            return                                          # and exit program
        

        drawRedRectangleAroundPlate(imgOriginalScene, licPlate)            

        print("\nlicense plate read from image = " + licPlate.strChars + "\n")  # write license plate text to std out
        print("----------------------------------------")

        writeLicensePlateCharsOnImage(imgOriginalScene, licPlate)       

        cv2.imshow("imgOriginalScene", imgOriginalScene)                

        cv2.imwrite("imgOriginalScene.png", imgOriginalScene)           # write image out to file

######################################################################### sql and rpi

    flag=0
    try:
        conn= pymysql.connect(host='localhost',user='root',password='root',db='pymysql')
    except:
        print("connection error - hostname or password incorrect")

    try:
        scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]

        credentials = ServiceAccountCredentials.from_json_keyfile_name("rushiliot-c0fef04930d0.json",scope)

        gc = gspread.authorize(credentials)

        wks = gc.open("rpi").sheet1
    except:
        print("connection error with rpi")

    a=conn.cursor()

    try:
        sql = 'Select * from car;'
        x=a.execute(sql)
    except:
        print("table doesn't exists")

    data = a.fetchall()

    for i in data:
  
        ##if(i[0]==shanmukha's code):
        if(i[0]==licPlate.strChars):
            c=i[1]+1
            m=0
            print(c)
            sql = 'update car set crossed ='+str(c)+' where car_no="'+licPlate.strChars+'";'
        ##sql = 'update car set crossed ='+str(c)+' where car_no="'+shanmukhas code+'";'
            a.execute(sql)
            try:
                wks.update_cell(1,2,"open")

            except:
                print("some error in rpi")

            flag=1
    if(flag==0):
        #sql = 'insert into car values("'+ shanmukha's code +'",1)'
        sql = 'insert into car values("'+licPlate.strChars+'",1)'
        ##print("ye chala")
        a.execute(sql)
        try:
            wks.update_cell(1,2,"open")
        except:
            print("some error in rpi")

    conn.commit()

    a.close()
    conn.close()
        
############################################################################
    ##cv2.waitKey(0)					

    return
# end main

def drawRedRectangleAroundPlate(imgOriginalScene, licPlate):

    p2fRectPoints = cv2.boxPoints(licPlate.rrLocationOfPlateInScene)            # get 4 vertices of rotated rect

    cv2.line(imgOriginalScene, tuple(p2fRectPoints[0]), tuple(p2fRectPoints[1]), SCALAR_RED, 2)         # draw 4 red lines
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[1]), tuple(p2fRectPoints[2]), SCALAR_RED, 2)
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[2]), tuple(p2fRectPoints[3]), SCALAR_RED, 2)
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[3]), tuple(p2fRectPoints[0]), SCALAR_RED, 2)
# end function

def writeLicensePlateCharsOnImage(imgOriginalScene, licPlate):
    ptCenterOfTextAreaX = 0                             
    ptCenterOfTextAreaY = 0

    ptLowerLeftTextOriginX = 0                          # this will be the bottom left of the area that the text will be written to
    ptLowerLeftTextOriginY = 0

    sceneHeight, sceneWidth, sceneNumChannels = imgOriginalScene.shape
    plateHeight, plateWidth, plateNumChannels = licPlate.imgPlate.shape

    intFontFace = cv2.FONT_HERSHEY_SIMPLEX                     
    fltFontScale = float(plateHeight) / 30.0                    
    intFontThickness = int(round(fltFontScale * 1.5))           # base font thickness on font scale

    textSize, baseline = cv2.getTextSize(licPlate.strChars, intFontFace, fltFontScale, intFontThickness)        # call getTextSize

            # unpack roatated rect into center point, width and height, and angle
    ( (intPlateCenterX, intPlateCenterY), (intPlateWidth, intPlateHeight), fltCorrectionAngleInDeg ) = licPlate.rrLocationOfPlateInScene

    intPlateCenterX = int(intPlateCenterX)              # make sure center is an integer
    intPlateCenterY = int(intPlateCenterY)

    ptCenterOfTextAreaX = int(intPlateCenterX)         # the horizontal location of the text area is the same as the plate

    if intPlateCenterY < (sceneHeight * 0.75):                                                  
        ptCenterOfTextAreaY = int(round(intPlateCenterY)) + int(round(plateHeight * 1.6))      
    else:                                                                                       
        ptCenterOfTextAreaY = int(round(intPlateCenterY)) - int(round(plateHeight * 1.6))      
    

    textSizeWidth, textSizeHeight = textSize                # unpack text size width and height

    ptLowerLeftTextOriginX = int(ptCenterOfTextAreaX - (textSizeWidth / 2))           
    ptLowerLeftTextOriginY = int(ptCenterOfTextAreaY + (textSizeHeight / 2))          

            # write the text on the image
    cv2.putText(imgOriginalScene, licPlate.strChars, (ptLowerLeftTextOriginX, ptLowerLeftTextOriginY), intFontFace, fltFontScale, SCALAR_YELLOW, intFontThickness)



if __name__ == "__main__":
    main()
