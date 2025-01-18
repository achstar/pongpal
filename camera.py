import cv2
import numpy as np

cap = cv2.VideoCapture(1)  # camera settings

if not cap.isOpened():
    print("Cannot open camera")
    exit()
fgbg = cv2.createBackgroundSubtractorMOG2(history=200, varThreshold=25, detectShadows=False)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    # hsv conversion
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    blue = (255, 0, 0)
    green = (0, 255, 0)
    # define red color range
    lower_orange = np.array([10, 150, 150])  # Hue, Saturation, Value
    upper_orange = np.array([35, 255, 255])

    lower_green = np.array([35, 50, 50])  
    upper_green = np.array([85, 255, 150])
 

    color_mask = cv2.inRange(hsv, lower_orange, upper_orange)

    # Find contours in the combined mask
    contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)

        if perimeter == 0 or area < 150:  
            continue

        circularity = 4 * np.pi * (area / (perimeter ** 2))

        if 0.3 < circularity < 1.3:  
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)

           
            cv2.circle(frame, center, radius, (0, 255, 0), 2)
            cv2.putText(frame, f"Ball", (center[0] - 10, center[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.imshow('test', frame)

    # q exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
