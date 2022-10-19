import cv2
import matplotlib as plt
import numpy as np
from statistics import mean
from math import sqrt
import sys
from time import sleep
PY3 = sys.version_info[0] == 3

if PY3:
    xrange = range

def angle_cos(p0,p1,p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

def findShapes(img):
    squares = []
    for gray in cv2.split(img):
        for thrs in xrange(0,255,26):
            if thrs == 0:
                bin = cv2.Canny(gray, 0, 50, apertureSize=5)
                bin = cv2.dilate(bin, None)
            else:
                _retval, bin = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
            contours, _hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                cnt_len = cv2.arcLength(cnt, True)
                cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
                if len(cnt) == 4 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt):
                    cnt = cnt.reshape(-1, 2)
                    max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in xrange(4)])
                    ## TODO:
                    # Change here for how accurate to a REAL square it should find
                    if max_cos < 0.7:
                        squares.append(cnt)
    return squares

s = 0
if len(sys.argv) > 1:
    s = sys.argv[1]


camera_det = 'Camera Detection'
thresh_view = 'Threshhold View'
translation_view = 'Translation View'
cv2.namedWindow(camera_det, cv2.WINDOW_NORMAL)
cv2.namedWindow(thresh_view, cv2.WINDOW_NORMAL)
result = None

source = cv2.VideoCapture(s)

#read initial frames
ok, frame = source.read()
ok, frame = source.read()
ok, frame = source.read()
if not ok:
    print('Cannot read video file')
    sys.exit()

while True:
    ## TODO:
    # Edit if polling rate of camera and calculations needs to be reduced
    #sleep(0.03)

    ok, frame = source.read()
    frame = cv2.flip(frame,1)
    frame_blur = cv2.blur(frame, (13,13))
    frame_hsv = cv2.cvtColor(frame_blur, cv2.COLOR_BGR2HSV)
    ## TODO:
    # Change here for what color to find in the hsv spectrum
    frame_thresh = cv2.inRange(frame_hsv, (105,150,80), (130,255,255))

    shapes = findShapes(frame_thresh)
    #cv2.drawContours(frame, shapes, -1, (0,255,0), 3)

    centers = []
    for shape in shapes:
        left_mid = (mean([shape[0][0], shape[3][0]]), mean([shape[0][1], shape[3][1]]))
        right_mid = (mean([shape[1][0], shape[2][0]]), mean([shape[1][1], shape[2][1]]))
        top_mid = (mean([shape[0][0], shape[1][0]]), mean([shape[0][1], shape[1][1]]))
        bot_mid = (mean([shape[2][0], shape[3][0]]), mean([shape[2][1], shape[3][1]]))
        #cv2.line(frame, left_mid, right_mid, (255,0,255), 3)
        #cv2.line(frame, top_mid, bot_mid, (255,0,255), 3)
        center = (mean([left_mid[0], right_mid[0]]), mean([top_mid[1], bot_mid[1]]))
        centers.append(center)
        cv2.circle(frame, center, 4, (0,255,255), 3)

    # The number of pixels
    num_rows, num_cols = frame.shape[:2]

    img_center = (num_rows//2, num_cols//2)

    cv2.line(frame, (img_center[1],0), (img_center[1],num_rows), (255,0,255), 3)
    cv2.line(frame, (0,img_center[0]), (num_cols,img_center[0]), (255,0,255), 3)

    min = -1
    indx = -1

    for idx,c in enumerate(centers):    
        row_dist = img_center[1] - c[0]
        col_dist = img_center[0] - c[1]
        if min == -1:
            min = sqrt(row_dist**2 + col_dist**2)
        else:
            dist = sqrt(row_dist**2 + col_dist**2)
            if dist < min:
                min = dist
                indx = idx

    if indx != -1:
        row_dist = img_center[1] - centers[indx][0]
        col_dist = img_center[0] - centers[indx][1]
        ## TODO:
        # Change here for what distance from center point it should recorrect itself
        if sqrt(row_dist**2 + col_dist**2) > 6:
            ## TODO:
            # Sent over UART to MSP distances from center and calculated recorrecting steps
            print((row_dist, col_dist))
        # # Creating a translation matrix
        # translation_matrix = np.float32([ [1,0,row_dist], [0,1,col_dist] ])

        # # Image translation
        # img_translation = cv2.warpAffine(frame, translation_matrix, (num_cols,num_rows))

        # cv2.line(img_translation, (600,0), (600,1200), (255,0,255), 3)
        # cv2.line(img_translation, (0,600), (1200,600), (255,0,255), 3)

    cv2.imshow(camera_det, frame)
    cv2.imshow(thresh_view, frame_thresh)

    #wait key Q or q or Esc to exit
    key = cv2.waitKey(1)
    if key == ord('Q') or key == ord('q') or key == 27:
        break

#release window and camera control
source.release()
cv2.destroyAllWindows()
