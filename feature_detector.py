import cv2
import numpy
import os

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

def defectDetection(path, inputImg):
    #Initiate ORB detector
    orb = cv2.ORB_create(nfeatures = 1000)
    images = []
    classNames = []
    unique_tiles = 0
    myList = os.listdir(path)

    for cl in myList:
        imgCurrent = cv2.imread(f'{path}/{cl}', 0)
        images.append(imgCurrent)
        classNames.append(os.path.splitext(cl)[0])
# print(classNames)

# print(len(desList))

    # findDescriptor(images, orb)
    desList = findDescriptor(images, orb)
    featureList = findID(inputImg, desList, orb)

    print(f"Features found against training data: {featureList}")

    if any(feature >= 12 for feature in featureList):
        print("Defect detected")
        cv2.putText(inputImg, "Result: Defect Detected", (50,50), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 1)
    else:
        cv2.putText(inputImg, "Result: Good Tomato", (50,50), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 1)

    cv2.imshow("img1", inputImg)
    cv2.waitKey(0)

    cv2.destroyAllWindows()
    return orb

# Path to reference images for feature detector
# path = 'bads'

# Temporary testing image, will be replaced with feed from RPi camera in production
# test = cv2.imread("./badTest2.png")
# defectDetection(path, test)