import cv2
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import HTML
import urllib

PREVIEW = 0
BLUR = 1
FEATURES = 2
CANNY = 3
BLUE_DETECT = 4

feature_params = dict(  maxCorners = 4,
                        qualityLevel = 0.2,
                        minDistance = 15,
                        blockSize = 9)

def drawRectangle(frame, bbox):
    p1 = (int(bbox[0]), int(bbox[1]))
    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
    cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)

def displayRectangle(frame, bbox):
    plt.figure(figsize=(20,10))
    frameCopy = frame.copy()
    drawRectangle(frameCopy, bbox)
    frameCopy = cv2.cvtColor(frameCopy, cv2.COLOR_RGB2BGR)
    plt.imshow(frameCopy); plt.axis('off')    

def drawText(frame, txt, location, color = (50,170,50)):
    cv2.putText(frame, txt, location, cv2.FONT_HERSHEY_SIMPLEX, 1, color, 3)

if not os.path.isfile('goturn.prototxt') or not os.path.isfile('goturn.caffemodel'):
    print("Downloading GOTURN model zip file")
    urllib.request.urlretrieve('https://www.dropbox.com/sh/77frbrkmf9ojfm6/AACgY7-wSfj-LIyYcOgUSZ0Ua?dl=1', 'GOTURN.zip')
    
    # Uncompress the file
    os.system("tar -xvf GOTURN.zip")

    # Delete the zip fileq
    os.remove('GOTURN.zip')

tracker = cv2.TrackerGOTURN_create()
s = 0

if len(sys.argv) > 1:
    s = sys.argv[1]

image_filter = PREVIEW
alive = True

win_name = 'Camera Detection'
cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
cv2.namedWindow('Threshhold View', cv2.WINDOW_NORMAL)
result = None

source = cv2.VideoCapture(s)

ok, frame = source.read()
ok, frame = source.read()
ok, frame = source.read()
frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
if not ok:
    print('Cannot read video file')
    sys.exit()

while True:
    ok, frame = source.read()
    frame = cv2.flip(frame, 1)
    frame_blur = cv2.blur(frame, (13, 13))
    frame_hsv = cv2.cvtColor(frame_blur, cv2.COLOR_BGR2HSV)
    frame_thresh = cv2.inRange(frame_hsv, (105,150,80), (130,255,255))
    frame_dst = cv2.cornerHarris(frame_thresh, 5,3,0.04)
    ret, dst = cv2.threshold(frame_dst,0.1*frame_dst.max(),255,0)
    dst = np.uint8(dst)
    ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    corners = cv2.cornerSubPix(frame_thresh,np.float32(centroids),(5,5),(-1,-1),criteria)
    # for i in range(1, len(corners)):
    #     print(corners[i])
    frame[dst>0.1*dst.max()]=[0,0,255]
    cv2.imshow(win_name, frame)
    cv2.imshow('Threshhold View', frame_thresh)
    key = cv2.waitKey(1)
    if key == ord('Q') or key == ord('q') or key == 27:
        break


source.release()
cv2.destroyWindow(win_name)


# ok = tracker.init(frame, bbox)

# while alive:
#     has_frame, frame = source.read()
#     if not has_frame:
#         break

#     frame = cv2.flip(frame, 1)
#     frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     if image_filter == BLUE_DETECT:
#         ok, bbox = tracker.update(frame)
#         if (ok):
#             drawRectangle(frame, bbox)
#         else:
#             drawText(frame, "Tracking failure detected", (80,140), (0, 0, 255))
#         result = frame
#     else:
#         result = frame
    
#     cv2.imshow(win_name, result)

#     key = cv2.waitKey(1)
#     if key == ord('Q') or key == ord('q') or key == 27:
#         alive = False
#     elif key == ord('C') or key == ord('c'):
#         image_filter = CANNY
#     elif key == ord('B') or key == ord('b'):
#         image_filter = BLUR
#     elif key == ord('F') or key == ord('f'):
#         image_filter = FEATURES
#     elif key == ord('P') or key == ord('p'):
#         image_filter = PREVIEW
#     elif key == ord('T') or key == ord('t'):
#         image_filter = BLUE_DETECT


# if image_filter == PREVIEW:
#         result = frame
#         cv2.imwrite('result.png', result)
#     elif image_filter == CANNY:
#         result = cv2.Canny(frame, 140, 150)
#     elif image_filter == BLUR:
#         result = cv2.blur(frame, (13,13))
#     elif image_filter == FEATURES:
#         result = frame
#         frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         corners = cv2.goodFeaturesToTrack(frame_gray, **feature_params)
#         if corners is not None:
#             for x,y in np.float32(corners).reshape(-1,2):
#                 cv2.circle(result, (int(x), int(y)), 10, (0, 255, 0), 1)
#     el

# corners = cv2.goodFeaturesToTrack(frame_thresh, **feature_params)
#         if corners is not None:
#             if len(corners) > 3:
#                 if not init:
#                     x_min = int(min(corners[0][0][1], corners[3][0][1]))
#                     y_min = int(min(corners[0][0][0], corners[1][0][0]))
#                     width = int(corners[3][0][1]-corners[1][0][1])
#                     height = int(corners[0][0][0]-corners[1][0][0])
#                     bbox = (x_min, y_min, abs(width), abs(height))
#                     ok = tracker.init(frame_thresh, bbox)
#                     init = True
#                 print(bbox)
#                 cv2.imshow(win_name, frame_thresh)
#                 # ok, bbox = tracker.update(frame_thresh)
#                 # if ok:
#                 #     drawRectangle(frame, bbox)
#                 # else:
#                 #     drawText(frame, "Tracking failure detected", (80,140), (0, 0, 255))
#                 result = frame_thresh
#                 #print(corners)