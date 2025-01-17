import cv2
import numpy as np

cap = cv2.VideoCapture(1)  # camera settings

if not cap.isOpened():
    print("Cannot open camera")
    exit()

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
    upper_orange = np.array([30, 255, 255])

    lower_green = np.array([35, 50, 50])  
    upper_green = np.array([85, 255, 150])
 

    mask = cv2.inRange(hsv, lower_green, upper_green)
    # fill in holes/lines for ball --> detected objects are white, bg black
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, np.ones((5, 5), np.uint8))

    # retr_external -- outermost contours
    # chain_approx_simple -- faster??? read that somewhere
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # cv2.drawContours(frame, contours, -1, blue, 2)
    for contour in contours:
        area = cv2.contourArea(contour) # area of contour
        perimeter = cv2.arcLength(contour, True)

        # div by 0
        if perimeter == 0:
            continue
        # 1 = perfect circle
        circularity = 4 * np.pi * (area / (perimeter ** 2))

        if area > 300 and area < 1200:
            # fit a circle around the contour
            (x, y), radius = cv2.minEnclosingCircle(contour)
            
            center = (int(x), int(y))
            radius = int(radius)

            cv2.drawContours(frame, [contour], -1, (255, 0, 0), 2)
            cv2.circle(frame, center, radius, (0, 0, 255), 2)
            cv2.putText(frame, f"{circularity:.2f} {area}", (center[0]-20, center[1]-20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.imshow('test', frame)

    # q exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
