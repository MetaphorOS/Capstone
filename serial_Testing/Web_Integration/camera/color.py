from picamzero import Camera
import cv2
import numpy as np

# Image masking
# Here's where the feed from the camera would go, so far I've only tested with images but it should be able to track colored objects in real time too
# Just replace the placeholder with the path to the image to be analyzed. If you want camera feed operation lmk so I can tweak the code a bit
# Everything up to the dotted line is for color detection and bounding box drawing
# cam = Camera()
# cam.take_photo("/home/Zach/Desktop/image3.jpg")

# image = cv2.imread("/home/Zach/Desktop/image3.jpg",1)[448:1703, 225:2091]
# print(image.shape)
#cv2.imshow('final', image)

# path = "bads"
def detectValue(red_h_min, red_h_max, red_s_min, red_s_max, red_v_min, red_v_max, green_h_min, green_h_max, green_s_min, green_s_max, green_v_min, green_v_max):
    cam = Camera()
    cam.take_photo("/home/Zach/Desktop/image3.jpg")

    image = cv2.imread("/home/Zach/Desktop/image3.jpg",1)[448:1703, 225:2091]
    return detectColors(image, red_h_min, red_h_max, red_s_min, red_s_max, red_v_min, red_v_max, green_h_min, green_h_max, green_s_min, green_s_max, green_v_min, green_v_max)

def findDescriptor (imgs, orb):
    desList = []
    for img in imgs:
        kp, des = orb.detectAndCompute(img, None)
        desList.append(des)
    return desList

def findID(img, desList, orb):
    kp2, des2 = orb.detectAndCompute(img, None)
    bf = cv2.BFMatcher()
    matchList = []
    finalList = []
    try:
        for des in desList:
            matches = bf.knnMatch(des, des2,k=2)
            good_match = []
            for m,n in matches:
                if m.distance < 0.75*n.distance:
                    good_match.append([m])
            matchList.append(len(good_match))
    except:
        pass
    return matchList

def detectColors(image, red_h_min, red_h_max, red_s_min, red_s_max, red_v_min, red_v_max, green_h_min, green_h_max, green_s_min, green_s_max, green_v_min, green_v_max):
    down_width = 700
    down_height = 500
    down_points = (down_width, down_height)
    img = cv2.resize(image, down_points, interpolation= cv2.INTER_LINEAR)
    
    # cv2.imshow('test',img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    ripeStatus = 2

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    #Mask implementation V2
    #Here's where you can play around with threshold values for what the algo considers red and green in the red_upper/lower and green_upper/lower arrays
    red_lower = np.array([red_h_min, red_s_min, red_v_min], np.uint8) 
    red_upper = np.array([red_h_max, red_s_max, red_v_max], np.uint8) 
    red_mask = cv2.inRange(hsv, red_lower, red_upper) 

    green_lower = np.array([green_h_min, green_s_min, green_v_min], np.uint8) 
    green_upper = np.array([green_h_max, green_s_max, green_v_max], np.uint8) 
    green_mask = cv2.inRange(hsv, green_lower, green_upper) 

    # brown_lower = np.array([0, 49, 0], np.uint8) 
    # brown_upper = np.array([19, 200, 200], np.uint8) 
    # brown_mask = cv2.inRange(hsv, brown_lower, brown_upper) 

    red_result = cv2.bitwise_and(img, img, mask = red_mask)
    green_result = cv2.bitwise_and(img, img, mask = green_mask)
    # brown_result = cv2.bitwise_and(img, img, mask = brown_mask)

    #BBox drawing
    contours, _ = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for _, contour in enumerate(contours): 
        area = cv2.contourArea(contour) 
        if(area > 3500): 
            # x, y, w, h = cv2.boundingRect(contour) 
            # print(x,y,w,h)
            # img = cv2.rectangle(img, (x, y),  (x + w, y + h),  (0, 0, 255), 2) 
            # cv2.putText(img, "Red Detected", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255))
            # # The output is this flag here called "ripeStatus". It gets set to 1 if red is detected and is left at 0 if green is detected
            # # If you want it to output something else based on the color just put it in this if statement for triggering when red is detected
            ripeStatus = 0

    contours, _ = cv2.findContours(green_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for _, contour in enumerate(contours): 
        area = cv2.contourArea(contour) 
        if(area > 4000): 
            # x, y, w, h = cv2.boundingRect(contour) 
            # print(x,y,w,h)
            # img = cv2.rectangle(img, (x, y),  (x + w, y + h),  (0, 255, 0), 2) 
            # cv2.putText(img, "Green Detected", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0))
            # Put code here for output if green is detected
            ripeStatus = 1

    # contours, _ = cv2.findContours(brown_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # for _, contour in enumerate(contours): 
    #     area = cv2.contourArea(contour) 
    #     if(area > 4000): 
    #         # x, y, w, h = cv2.boundingRect(contour) 
    #         # print(x,y,w,h)
    #         # img = cv2.rectangle(img, (x, y),  (x + w, y + h),  (0, 255, 0), 2) 
    #         # cv2.putText(img, "Green Detected", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0))
    #         # Put code here for output if green is detected
    #         ripeStatus = 2

    # These are just debugging windows that show what the algo considers green and red in the test image, comment out if not helpful
    # while True:

    #     cv2.imshow('green', green_result)
    #     cv2.imshow('red', red_result)
    #     # cv2.imshow('brown', brown_result)
    #     cv2.imshow('final', img)

    #     if cv2.waitKey(1) == 27: break
    # sleep(5)
    # cv2.destroyAllWindows()
    return ripeStatus

#-------------------------------------------------------------------------------------------------------------------------------------------------
# Function that handles defect detection, not meant to work because reference images for the algo to know what a "bad" tomato is is not on Git
# We also havent tested this function yet with a real bad tomato because its hard to find one
def defectDetection(path, inputImg):
    #Initiate ORB detector
    orb = cv2.ORB_create(nfeatures = 1000)
    images = []
    classNames = []
    unique_tiles = 0
    myList = os.listdir(path)
    defectStatus = 0

    for cl in myList:
        imgCurrent = cv2.imread(f'{path}/{cl}', 0)
        images.append(imgCurrent)
        classNames.append(os.path.splitext(cl)[0])

    desList = findDescriptor(images, orb)
    featureList = findID(inputImg, desList, orb)

    print(f"Features found against training data: {featureList}")

    # Everything in this IF statement triggers when a sufficient number of detects are matched with the ones seen in the reference images.
    # Currently it just sets a flag called defectStatus to 1 if 12 defect features are matched with reference images
    if any(feature >= 12 for feature in featureList):
        print("Defect detected")
        cv2.putText(inputImg, "Result: Defect Detected", (50,50), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 1)
        defectStatus = 1
    # Everthing in the else statment triggers if a tomato is considered good (i.e. less than 12 defect features were matched)
    else:
        cv2.putText(inputImg, "Result: Good Tomato", (50,50), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 1)

    while True:
        cv2.imshow("img1", inputImg)
        if cv2.waitKey(1) == 27: break

    cv2.destroyAllWindows()
    return orb

# Calling both functions and storing the result in these variables
# ripeStatus = detectColors(image)
# print(ripeStatus)
# defectStatus = defectDetection(path, image)

def noop(x): return None

def debug():

    cam = Camera()
    cam.take_photo("/home/Zach/Desktop/image3.jpg")

    SET_MASK_WINDOW = "Set Mask"
    cv2.namedWindow(SET_MASK_WINDOW, cv2.WINDOW_AUTOSIZE)
    cv2.createTrackbar("Min Hue", SET_MASK_WINDOW, 0, 179, noop)
    cv2.createTrackbar("Max Hue", SET_MASK_WINDOW, 49, 179, noop)
    cv2.createTrackbar("Min Sat", SET_MASK_WINDOW, 19, 255, noop)
    cv2.createTrackbar("Max Sat", SET_MASK_WINDOW, 200, 255, noop)
    cv2.createTrackbar("Min Val", SET_MASK_WINDOW, 0, 255, noop)
    cv2.createTrackbar("Max Val", SET_MASK_WINDOW, 200, 255, noop)

    while True:
        ## 2. Read and convert image to HSV color space
        image = cv2.imread("/home/Zach/Desktop/image3.jpg",1)[448:1703, 225:2091]
        imageHsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        ## 3. Get min and max HSV values from Set Mask window
        minHue = cv2.getTrackbarPos("Min Hue", SET_MASK_WINDOW)
        maxHue = cv2.getTrackbarPos("Max Hue", SET_MASK_WINDOW)
        minSat = cv2.getTrackbarPos("Min Sat", SET_MASK_WINDOW)
        maxSat = cv2.getTrackbarPos("Max Sat", SET_MASK_WINDOW)
        minVal = cv2.getTrackbarPos("Min Val", SET_MASK_WINDOW)
        maxVal = cv2.getTrackbarPos("Max Val", SET_MASK_WINDOW)
        minHsv = np.array([minHue, minSat, minVal])
        maxHsv = np.array([maxHue, maxSat, maxVal])

        ## 4. Create mask and result (masked) image
        # params: input array, lower boundary array, upper boundary array
        mask = cv2.inRange(imageHsv, minHsv, maxHsv)
        # params: src1 array, src2 array, mask
        resultImage = cv2.bitwise_and(image, image, mask=mask)

        ## 5. Show images
        cv2.imshow("Input Image", image)
        # cv.imshow("Mask", mask)   # optional
        cv2.imshow("Result Image", resultImage)
        if cv2.waitKey(1) == 27: break   # Wait Esc key to end program

# print(detectValue())
# debug()