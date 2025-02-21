import matplotlib.pyplot as plt
import numpy as np
import cv2
import torch
import math

class labelDetected:
  def __init__(self):
    self.arrCentx   = []
    self.arrCenty   = []
    self.arrWeight  = []
    self.arrHeight  = []
    self.count      = 0
    self.arrPrecis  = []
    self.arrValid   = []
  
  def defineCenter(self, posx1, posy1, posx2, posy2 ):

    self.arrCentx.append(int( 0.5*(posx1 + posx2)))
    self.arrCenty.append(int( 0.5*(posy1 + posy2)))
    self.arrWeight.append(posx2 - posx1)
    self.arrWeight.append(posy2 - posy1)
  
  def destroyObject(self):
    self.arrCentx   = []
    self.arrCenty   = []
    self.arrWeight  = []
    self.arrHeight  = []
    self.count      = 0
    self.arrPrecis  = []
    self.arrValid   = []

class trafficCamera():

  def __init__(self,  realScale, pointRef, labelUsed, limitReg1, limitReg2):
    self.carLabel     = labelDetected()
    self.motorLabel   = labelDetected()
    self.busLabel     = labelDetected()
    self.truckLabel   = labelDetected()
    self.labelUsed    = labelUsed
    self.limitReg1    = limitReg1
    self.limitReg2    = limitReg2
    self.realScale    = realScale
    self.pointRef     = pointRef

  def getCenter(self, frameDetect, arrIdlabel):
    
    resultPred = frameDetect.xyxy
    tensorDim = list(resultPred[0].size())

    #print('Result Prediction: ', resultPred[0])
    for i in range(0, tensorDim[0] ):
      if resultPred[0][i,5].item() == arrIdlabel[0]:
        self.carLabel.defineCenter(resultPred[0][i,0].item(), resultPred[0][i,1].item(), resultPred[0][i,2].item(), resultPred[0][i,3].item() )  
        
        self.carLabel.count = self.carLabel.count + 1
        self.carLabel.arrPrecis.append(resultPred[0][i,4].item())

      elif resultPred[0][i,5].item() == arrIdlabel[1]:
        self.truckLabel.defineCenter(resultPred[0][i,0].item(), resultPred[0][i,1].item(), resultPred[0][i,2].item(), resultPred[0][i,3].item() )  
        self.truckLabel.count = self.truckLabel.count + 1
        self.truckLabel.arrPrecis.append(resultPred[0][i,4].item())

      elif resultPred[0][i,5].item() == arrIdlabel[2]: 
        self.motorLabel.defineCenter(resultPred[0][i,0].item(), resultPred[0][i,1].item(), resultPred[0][i,2].item(), resultPred[0][i,3].item() )
        self.motorLabel.count = self.motorLabel.count + 1
        self.motorLabel.arrPrecis.append(resultPred[0][i,4].item())

      elif resultPred[0][i,5].item() == arrIdlabel[3]:
        self.busLabel.defineCenter(resultPred[0][i,0].item(), resultPred[0][i,1].item(), resultPred[0][i,2].item(), resultPred[0][i,3].item() )
        self.busLabel.count = self.busLabel.count + 1
        self.busLabel.arrPrecis.append(resultPred[0][i,4].item())

  def estimateDist(self, type, arrValp, posX, posY):
    
    if type == 0:
      distRealx = ( posX - self.pointRef[0] )*(posX - self.pointRef[0])
      distRealy = ( posY - self.pointRef[1] )*(posY - self.pointRef[1])
      distPoint = 1.0*self.realScale*math.sqrt( distRealx + distRealy ) 
        
      return distPoint 

    elif type == 1:
      arrDist = []
      
      for i in range(0, self.carLabel.count):
        distRealx = ( self.carLabel.arrCentx[i] - self.pointRef[0] )*(self.carLabel.arrCentx[i] - self.pointRef[0])
        distRealy = ( self.carLabel.arrCenty[i] - self.pointRef[1] )*(self.carLabel.arrCenty[i] - self.pointRef[1])
        arrDist.append( self.realScale*math.sqrt( distRealx + distRealy )  )
      
      for i in range(0, self.truckLabel.count):
        distRealx = ( self.truckLabel.arrCentx[i] - self.pointRef[0] )*(self.truckLabel.arrCentx[i] - self.pointRef[0])
        distRealy = ( self.truckLabel.arrCenty[i] - self.pointRef[1] )*(self.truckLabel.arrCenty[i] - self.pointRef[1])
        arrDist.append( self.realScale*math.sqrt( distRealx + distRealy )  )

      return arrDist
    
    elif type == 3:
      if( len(arrValp) == 1 ):
        distRealx = ( posX - self.pointRef[0] )*(posX - self.pointRef[0])
        distRealy = ( posY - self.pointRef[1] )*(posY - self.pointRef[1])
        distPoint = 1.0*self.realScale*math.sqrt( distRealx + distRealy ) 
        return distPoint

      elif ( len(arrValp) > 1 ):
        distRealx = ( posX - arrValp[-1]  )*(posX - arrValp[-1] )
        distRealy = ( posY - arrValp[-1]  )*(posY - arrValp[-1] )
        distPoint = 1.0*self.realScale*math.sqrt( distRealx + distRealy ) 
        return distPoint

  def putDistance(self, type, arrVp, posX, posY, frame):
    
    frameText = frame

    if type == 0:
      distP = self.estimateDist(0, arrVp, posX, posY)
      frameText = cv2.putText(img = frameText, text= str(distP), org = ( posX, posY), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale = 0.5, color=(0, 255, 0),thickness=1)
      return frameText, distP
    elif type == 1:
      
      distArr = self.estimateDist( 1, arrVp, 0, 0)
      for i in range(0, self.carLabel.count):
        frameText = cv2.putText(img = frameText, text= str(distArr[i]), org = ( self.carLabel.arrCentx[i], self.carLabel.arrCenty[i] ), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale = 0.5, color=(0, 255, 0),thickness=1)

      for i in range(0, self.truckLabel.count):
        frameText = cv2.putText(img = frameText, text= str(distArr[i+self.carLabel.count]), org = ( self.carLabel.arrCentx[i], self.carLabel.arrCenty[i] ), fontFace=cv2.FONT_HERSHEY_TRIPLEX, fontScale = 0.5, color=(0, 255, 0),thickness=1)
        return frameText
    

  def intoRegion(self, globalPos, limitReg ):

    dimLimit = len(limitReg)
    
    if( dimLimit == 2 ):
      into1Point = ((limitReg[1][0] - limitReg[0][0])*(globalPos[1] - limitReg[0][1]) - (limitReg[1][1] - limitReg[0][1])*(globalPos[0] - limitReg[0][0])) < 0  
      return into1Point

    elif( dimLimit >= 3 ):
      auxArr = []
      for i in range(0,dimLimit):
        into1Point = ((limitReg[(i+1)%dimLimit][0] - limitReg[i][0])*(globalPos[1] - limitReg[i][1]) - (limitReg[(i+1)%dimLimit][1] - limitReg[i][1])*(globalPos[0] - limitReg[i][0])) < 0 
        auxArr.append(int(into1Point))
      
      if( sum(auxArr) == dimLimit ):
        return True
      else:
        return False

  def addCiclec(self, image, circlex, circley ):
    
    imageC = cv2.circle(image, ( circlex, circley), radius = 3, color=(0, 0, 255), thickness=-1)
    return imageC

  def drawCenter(self, frame):

    validFrame = False
    arrCar = []
    arrTruck = []
    arrAux = []

    for i in range(0, self.carLabel.count):

      posX = self.carLabel.arrCentx[i]
      posY = self.carLabel.arrCenty[i]
      validFrame = self.intoRegion( ( posX, posY), self.limitReg1 )
      validFrame = self.intoRegion( ( posX, posY), self.limitReg1 ) and self.intoRegion( ( posX, posY), self.limitReg2 )
      
      if validFrame:
        frame = self.addCiclec( frame, posX, posY )
        frame, valC = self.putDistance(0, arrCar, posX, posY, frame)
        arrCar.append(valC)
        #plc2Sent.sendData()


    for i in range(0, self.truckLabel.count):
      
      posX = self.truckLabel.arrCentx[i]
      posY = self.truckLabel.arrCenty[i]
      validFrame = self.intoRegion( ( posX, posY), self.limitReg1 )
      validFrame = self.intoRegion( ( posX, posY), self.limitReg1 ) and self.intoRegion( ( posX, posY), self.limitReg2 )
      
      if validFrame:  
        frame = self.addCiclec( frame, posX, posY)
        frame,valTr = self.putDistance(0, arrTruck,posX, posY, frame)
        arrTruck.append(valTr)


    for i in range(0, self.motorLabel.count):
      
      posX = self.motorLabel.arrCentx[i]
      posY = self.motorLabel.arrCenty[i]
      validFrame = self.intoRegion( ( posX, posY), self.limitReg1 )
      validFrame = self.intoRegion( ( posX, posY), self.limitReg1 ) and self.intoRegion( ( posX, posY), self.limitReg2 )
    
      if validFrame:
        frame = self.addCiclec( frame, posX, posY)
        frame = self.putDistance(0, posX, posY, frame)
        frame,valTr = self.putDistance(0, posX, arrAux, posY, frame)
        arrTruck.append(valTr)

    for i in range(0, self.busLabel.count):
      
      posX = self.busLabel.arrCentx[i]
      posY = self.busLabel.arrCenty[i]
      validFrame = self.intoRegion( ( posX, posY), self.limitReg1 )
      validFrame = self.intoRegion( ( posX, posY), self.limitReg1 ) and self.intoRegion( ( posX, posY), self.limitReg2 )
      
      if validFrame:  
        frame = self.addCiclec( frame, posX, posY )
        frame = self.putDistance(0, posX, posY, frame)
        frame,valTr = self.putDistance(0, posX, arrAux, posY, frame)
        arrTruck.append(valTr)

    return frame, arrCar, arrTruck

  def createDatset(self, idStart, idEnd, pathStart, pathEnd):

    count = 0

    for i in range(idStart,idEnd):
      video = cv2.VideoCapture(pathStart + str(i) + '.mp4')
      
      while(video.isOpened()):
          ret, frame = video.read()
          cv2.imshow('frame', frame)

          if cv2.waitKey(10) == ord('s'):
            count = count + 1
            cv2.imwrite(pathEnd + str(count) + '.jpg' , frame)

          if cv2.waitKey(1) & 0xFF == ord('q'):
              break


      video.release()
      cv2.destroyAllWindows()


  def displayVideo(self, rawData, modelTorch):
    
    while(rawData.isOpened()):
      ret, frame    = rawData.read()
      frameDetect   = modelTorch(frame)
      #print('Result: ', frameDetect.xyxy)
      self.getCenter(frameDetect, self.labelUsed)
      framemodDetect  = np.squeeze(frameDetect.render())
      framemodCir = self.drawCenter(framemodDetect)

      self.carLabel.destroyObject()
      self.motorLabel.destroyObject()
      self.busLabel.destroyObject()
      self.truckLabel.destroyObject()

      cv2.imshow('Frame With Detection',framemodCir)

      if cv2.waitKey(25) & 0xFF == ord('q'):
          break
            
    rawData.release()
    cv2.destroyAllWindows()

