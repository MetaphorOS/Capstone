import cv2
import numpy as np

# Image masking
image = cv2.imread("TEST_IMAGE_HERE",1)

def detectColors(image):
    down_width = 700
    down_height = 500
    down_points = (down_width, down_height)
    img = cv2.resize(image, down_points, interpolation= cv2.INTER_LINEAR)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    #Mask implementation V2
    red_lower = np.array([135, 57, 70], np.uint8) 
    red_upper = np.array([180, 255, 255], np.uint8) 
    red_mask = cv2.inRange(hsv, red_lower, red_upper) 

    green_lower = np.array([25, 52, 72], np.uint8) 
    green_upper = np.array([102, 255, 255], np.uint8) 
    green_mask = cv2.inRange(hsv, green_lower, green_upper) 

    red_result = cv2.bitwise_and(img, img, mask = red_mask)
    green_result = cv2.bitwise_and(img, img, mask = green_mask)

    #BBox drawing
    contours, hierarchy = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for pic, contour in enumerate(contours): 
        area = cv2.contourArea(contour) 
        if(area > 5000): 
            x, y, w, h = cv2.boundingRect(contour) 
            print(x,y,w,h)
            img = cv2.rectangle(img, (x, y),  (x + w, y + h),  (0, 0, 255), 2) 
            cv2.putText(img, "Red Detected", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255)) 

    contours, hierarchy = cv2.findContours(green_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for pic, contour in enumerate(contours): 
        area = cv2.contourArea(contour) 
        if(area > 5000): 
            x, y, w, h = cv2.boundingRect(contour) 
            print(x,y,w,h)
            img = cv2.rectangle(img, (x, y),  (x + w, y + h),  (0, 255, 0), 2) 
            cv2.putText(img, "Green Detected", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0)) 

    cv2.imshow('green', green_result)
    cv2.imshow('red', red_result)
    cv2.imshow('final', img)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

detectColors(image)