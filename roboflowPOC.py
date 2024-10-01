# Importing necessary libraries
from inference_sdk import InferenceHTTPClient
import cv2

# Defining API connection to roboflow platform
client = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="oyhttZJduhrKFlfI7p2t"
)

# Reading image
imgPath = "./tomato2.png"
image = cv2.imread(imgPath)

# Passing image through API to Roboflow for processing using the "cherry-tomatoes/1" model
results = client.infer(imgPath, model_id="cherry-tomatoes/1")
print(results)

# Parsing results into useful parts
x = int(results["predictions"][0]["x"])
y = int(results["predictions"][0]["y"])
h = int(results["predictions"][0]["width"])
w = int(results["predictions"][0]["height"])
# finalX = x - 200
# finalY = y - 250
conf = round(results["predictions"][0]["confidence"], 2)*100
print(x, y)

# Using API results to draw bounding rectangle around tomato and display the confidence level
# img = cv2.rectangle(image, (x, y), (x+w, y+h), (0,0,255), 2)
cv2.putText(image, f"Confidence: {conf}", (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0))

# Show final image
cv2.imshow('img', image)
cv2.waitKey(0)
cv2.destroyAllWindows()