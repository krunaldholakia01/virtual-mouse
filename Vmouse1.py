import cv2
import numpy as np
import wx
from pynput.mouse import Button, Controller


mouse = Controller()
app = wx.App(False)
sx, sy = wx.GetDisplaySize()
capx, capy = 320, 240
lowerBound = np.array([30, 80, 40])
upperBound = np.array([80, 255, 255])

cap = cv2.VideoCapture(0)
cap.set(3, capx)
cap.set(4, capy)
kernelOpen = np.ones((5, 5))
kernelClose = np.ones((20, 20))

mLocOld = np.array([0, 0])
mouseLoc = np.array([0, 0])
DampingFactor = 3

pinchFlag = 0

openx, openy, openw, openh = 0, 0, 0, 0

while True:
    ret, img = cap.read()
    # img = cv2.resize(img, (340, 220))

    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(imgHSV, lowerBound, upperBound)
    maskOpen = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernelOpen)
    maskClose = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernelClose)

    maskFinal = maskClose

    _, conts, h = cv2.findContours(maskFinal.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if len(conts) == 2:

        if pinchFlag == 1:
            pinchFlag = 0
            mouse.release(Button.left)

        x1, y1, w1, h1 = cv2.boundingRect(conts[0])
        x2, y2, w2, h2 = cv2.boundingRect(conts[1])
        cv2.rectangle(img, (x1, y1), (x1 + w1, y1 + h1), (255, 0, 0), 2)
        cv2.rectangle(img, (x2, y2), (x2 + w2, y2 + h2), (255, 0, 0), 2)
        cx1 = x1 + int(w1 / 2)
        cy1 = y1 + int(h1 / 2)
        cx2 = x2 + int(w2 / 2)
        cy2 = y2 + int(h2 / 2)
        cx = int((cx1 + cx2) / 2)
        cy = int((cy1 + cy2) / 2)
        cv2.line(img, (cx1, cy1), (cx2, cy2), (255, 0, 0), 2)
        cv2.circle(img, (cx, cy), 2, (0, 0, 255), 2)

        mouseLoc = mLocOld + ((cx, cy) - mLocOld) / DampingFactor
        mouse.position = (sx - int(mouseLoc[0] * sx / capx), int(mouseLoc[1] * sy / capy))
        while mouse.position != (sx - int(mouseLoc[0] * sx / capx), int(mouseLoc[1] * sy / capy)):
            pass
        mLocOld = mouseLoc
        openx, openy, openw, openh = cv2.boundingRect(np.array([[x1, y1], [x1 + w1, y1 + h1], [x2, y2],
                                                                [x2 + w2, y2 + h2]]))

    elif len(conts) == 1:

        x, y, w, h = cv2.boundingRect(conts[0])

        if pinchFlag == 0:
            if abs((w * h - openw * openh) * 100 / (w * h)) < 30:
                pinchFlag = 1
                mouse.press(Button.left)
                openx, openy, openw, openh = 0, 0, 0, 0

        else:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cx = int(x + w / 2)
            cy = int(y + h / 2)
            cv2.circle(img, (cx, cy), int((w + h) / 4), (0, 0, 255), 2)

            mouseLoc = mLocOld + ((cx, cy) - mLocOld) / DampingFactor
            mouse.position = (sx - int(mouseLoc[0] * sx / capx), int(mouseLoc[1] * sy / capy))
            while mouse.position != (sx - int(mouseLoc[0] * sx / capx), int(mouseLoc[1] * sy / capy)):
                pass
            mLocOld = mouseLoc

    cv2.imshow("cap", img)

    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()
