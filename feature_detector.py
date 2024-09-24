import cv2
import numpy
import os

path = 'bads'
test = cv2.imread("./badTest.jpg")

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

def findDescriptor (imgs):
    desList = []
    for img in imgs:
        kp, des = orb.detectAndCompute(img, None)
        desList.append(des)
    return desList

desList = findDescriptor(images)
# print(len(desList))

def findID(img, desList):
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

findDescriptor(images)
featureList = findID(test, desList)

print(featureList)

if any(feature >= 10 for feature in featureList):
    print("Defect detected")
    cv2.putText(test, "Defect Detected", (50,50), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 1)

cv2.imshow("img1", test)
cv2.waitKey(0)

cv2.destroyAllWindows()