import cv2
import sys
import numpy as np
import time
from statistics import median
from math import sqrt
PY3 = sys.version_info[0] == 3

FINDSHAPES = 0
CORNERSUBPIX = 1
image_filter = FINDSHAPES

CAMERA = 2
THREESQUARES = 3
FOURSQUARES = 4
THREESQUARESCENTER = 5
image_source = CAMERA

image_print = False

if PY3:
    xrange = range

def angle_cos(p0,p1,p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

def findShapes(img):
    squares = []
    coords = []
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
                    x,y,w,h = cv2.boundingRect(cnt)
                    cnt = cnt.reshape(-1, 2)
                    max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in xrange(4)])
                    if max_cos < 0.08:
                        found = False
                        for coord in coords:
                            if abs(coord[0] - x) < 50:
                                found = True
                        if not found or len(coords) == 0:
                            squares.append(cnt)
                            coords.append((x,y,w,h))
    return squares, coords

s = 0
if len(sys.argv) > 1:
    s = sys.argv[1]

win_cam = 'Camera Detection'
cv2.namedWindow(win_cam, cv2.WINDOW_NORMAL)
win_thresh = 'Threshhold View'
cv2.namedWindow(win_thresh, cv2.WINDOW_NORMAL)
win_draw = 'Object Drawing'
cv2.namedWindow(win_draw, cv2.WINDOW_NORMAL)

result = None
source = cv2.VideoCapture(s)

shape_cnt = 0
shape_cnt_history = []
shape_cnt_history_2nd_lvl = []

img_loc_3 = "C:/Users/ajroh/repos/opencv_new/module15/3squares.png"
img_loc_4 = "C:/Users/ajroh/repos/opencv_new/module15/4squares.png"
img_loc_3_centered = "C:/Users/ajroh/repos/opencv_new/module15/3squarescentered.png"

while True:
    time.sleep(0.03)
    
    if image_source == CAMERA:
        ok,frame = source.read()
        frame = cv2.flip(frame, 1) 
    elif image_source == THREESQUARES:
        frame = cv2.imread(img_loc_3, cv2.IMREAD_COLOR)
    elif image_source == FOURSQUARES:
        frame = cv2.imread(img_loc_4, cv2.IMREAD_COLOR)
    elif image_source == THREESQUARESCENTER:
        frame = cv2.imread(img_loc_3_centered, cv2.IMREAD_COLOR)

    frame_draw = np.copy(frame)
    
    num_rows, num_cols = frame_draw.shape[:2]
    img_center = (num_cols//2,num_rows//2)
    cv2.line(frame_draw, (num_cols//2,0), (num_cols//2,num_cols), (0,0,255), 3)
    cv2.line(frame_draw, (0,num_rows//2), (num_cols,num_rows//2), (0,0,255), 3)

    frame_blur = cv2.blur(frame, (13,13))

    frame_hsv = cv2.cvtColor(frame_blur, cv2.COLOR_BGR2HSV)

    frame_thresh = cv2.inRange(frame_hsv, (105,150,80), (130,255,255))

    try:
        if image_filter == CORNERSUBPIX:
            frame_dst = cv2.cornerHarris(frame_thresh, 5,3,0.04)
            ret,dst = cv2.threshold(frame_dst, 0.1*frame_dst.max(),255,0)
            dst=np.uint8(dst)

            ret,labels,stats,centroids = cv2.connectedComponentsWithStats(dst)
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
            corners = cv2.cornerSubPix(frame_thresh, np.float32(centroids), (5,5),(-1,-1), criteria)

            corners = corners.astype('intc')

            squareFromCorners = np.array([[corners[1],corners[2],corners[6],corners[5]],
                                    [corners[3],corners[4],corners[8],corners[7]],
                                    [corners[9],corners[10],corners[12],corners[11]]])
            cv2.drawContours(frame_draw, squareFromCorners, -1, (0,255,0), 3)
        elif image_filter == FINDSHAPES:
            shapes, coords = findShapes(frame_thresh)
            cv2.drawContours(frame_draw, shapes, -1, (0,255,0), 3) 
            centers = []
            for coord in coords:
                x = coord[0]
                y = coord[1]
                w = coord[2]
                h = coord[3]
                cv2.circle(frame_draw, (x,y), 5, (255,0,255), 3)
                cv2.circle(frame_draw, (x+w,y), 5, (255,0,255), 3)
                cv2.circle(frame_draw, (x+w,y+h), 5, (255,0,255), 3)
                cv2.circle(frame_draw, (x,y+h), 5, (255,0,255), 3)
                centers.append((x+w//2,y+h//2))
            centered = False
            if len(centers) > 0:
                sumx = 0
                sumy = 0
                for c in centers:
                    sumx += c[0]
                    sumy += c[1]
                sumx = sumx//len(centers)
                sumy = sumy//len(centers)
                cv2.circle(frame_draw, (sumx,sumy), 5, (255,255,0), 3)
                x_dist = abs(sumx-img_center[0])
                y_dist = abs(sumy-img_center[1])
                print((sumx,num_cols//15),(sumy,num_rows//15))
                if (x_dist < num_cols//15 and y_dist < num_rows//15):
                    centered = True
            #    if len(centers) == 1:
            #         do_nothing = True
            #     elif len(centers) == 2:
            #         do_nothing = True
            #     elif len(centers) == 3:
            #         tri_center = ((centers[0][0]+centers[1][0]+centers[2][0])//3,
            #                     (centers[0][1]+centers[1][1]+centers[2][1])//3)
                    
            #         x_dist = abs(tri_center[0]-img_center[0])
            #         y_dist = abs(tri_center[1]-img_center[1])
            #         if x_dist < num_cols//15 and y_dist < num_rows//15:
            #             centered = True
            #     else: 
            #         do_nothing = True
            if centered:
                cv2.putText(frame_draw, 'Centered', (25,25), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)
            else:
                cv2.putText(frame_draw, 'Not Centered', (25,25), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)
            if shape_cnt_history is None or len(shape_cnt_history) < 30:
                if (len(shapes) > 0):
                    shape_cnt_history.append(len(shapes))
            else:
                shape_cnt_history_2nd_lvl.append(np.uint(median(shape_cnt_history)))
                shape_cnt_history = []
            
    except:
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        print("Exception Found at " + current_time)

    if image_print:
        try:
            print(np.int32(median(shape_cnt_history_2nd_lvl)))
        except:
            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            print("Exception Found at " + current_time + " @ Print Exception")
    



    cv2.imshow(win_cam, frame)
    cv2.imshow(win_thresh, frame_thresh)
    cv2.imshow(win_draw, frame_draw)
    #wait key Q or q or Esc to exit
    key = cv2.waitKey(1)
    if key == ord('Q') or key == ord('q') or key == 27:
        break
    elif key == ord('C') or key == ord('c'):
        image_filter = CORNERSUBPIX
    elif key == ord('F') or key == ord('f'):
        image_filter = FINDSHAPES
    elif key == ord('2'):
        image_source = CAMERA
    elif key == ord('3'):
        image_source = THREESQUARES
    elif key == ord('4'):
        image_source = FOURSQUARES
    elif key == ord('5'):
        image_source = THREESQUARESCENTER
    elif key == ord('P') or key == ord('p'):
        image_print = not image_print
    

#release window and camera control
source.release()
cv2.destroyAllWindows()