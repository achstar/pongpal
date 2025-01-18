import cv2
import numpy as np
from collections import deque

# camera 
cap = cv2.VideoCapture(1)  # camera settings

# positions queue
ball_positions = deque(maxlen=4)

# bounds 
upper_bound = 0
lower2_bound = 0
lower1_bound = 0
midpoint = 0

# states/bools
current_side = ""
above = False
touch = False
bounce = False

# cv setup
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
    # orange 
    lower_orange = np.array([10, 180, 200])  # Hue, Saturation, Value
    upper_orange = np.array([30, 255, 255])
    
    # red 1
    lower_red1 = np.array([0, 200, 200])    
    upper_red1 = np.array([10, 255, 255])
    # red 2 wraparound
    lower_red2 = np.array([170, 200, 200])  
    upper_red2 = np.array([180, 255, 255])
    # table blue
    lower_blue = np.array([100, 150, 50])  
    upper_blue = np.array([130, 255, 255])

    # masks
    red_mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    red_mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = red_mask1 | red_mask2

    table_mask = cv2.inRange(hsv, lower_blue, upper_blue) 
    ball_mask = cv2.inRange(hsv, lower_orange, upper_orange)

    # contours in the combined mask
    red_contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    table_contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    ball_contours, _ = cv2.findContours(ball_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    net_post_detected = False

    for contour in red_contours:
        area = cv2.contourArea(contour)

        if area > 100 and area < 300:  
            x, y, w, h = cv2.boundingRect(contour)
            net_post_x = x + w // 2  # x-coordinate of the net post
            net_post_detected = True

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(frame, f"area: {area}", (x, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # midpoint line (red)
            cv2.line(frame, (net_post_x, 0), (net_post_x, frame.shape[0]), (0, 0, 255), 2)
            midpoint = net_post_x
            center_y = y + h // 2 

            # center of net (upper lower bound for table) (yellow)
            cv2.line(frame, (0, center_y), (frame.shape[1], center_y), (0, 255, 255), 2)
            lower2_bound = center_y
            # upper bound line (magenta)
            cv2.line(frame, (0, y), (frame.shape[1], y), (255, 0, 255), 2)
            upper_bound = y
            break  # only the first (largest) red contour is used
    for contour in table_contours:
        area = cv2.contourArea(contour)

        if area > 1000:  
            x, y, w, h = cv2.boundingRect(contour)
            net_post_x = x + w // 2  
            net_post_detected = True

            # bottom of table?
            cv2.line(frame, (0, y + h), (frame.shape[1], y + h), (0, 255, 255), 2)
            lower1_bound = y + h
            cv2.putText(frame, f"area: {area}", (x, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
    for contour in ball_contours:
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)

        if perimeter == 0 or area < 50:  
            continue

        circularity = 4 * np.pi * (area / (perimeter ** 2))
        
        if 0.3 < circularity < 1.3:  
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)
            bottom = center[1] + radius
            cv2.circle(frame, center, radius, (0, 255, 0), 2)
            cv2.putText(frame, f"Ball", (center[0] - 10, center[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            # determine side
            if(center[0] > midpoint):
                current_side = "RIGHT"
            else:
                current_side = "LEFT"
            print(current_side)
            
            # logic for bounce upper bound
            if(bottom < upper_bound):
                above = True
                print("higher")
            else:
                above = False
            # logic for table touch
            if(bottom >= lower2_bound - 5 and bottom <= lower1_bound ):
                touch = True
                print("on table")
            else:
                touch = False
            ball_positions.append((above, touch))

            # FSM?? for bounce detection
            if(len(ball_positions) >= 4):
                last_above = ball_positions[2][0]
                last_touch = ball_positions[2][1]

                lastlast_above = ball_positions[1][0]
                lastlast_touch = ball_positions[1][1]

                if(lastlast_above and last_touch and above):
                    bounce = True
                else:
                    bounce = False
    if(bounce):
        print("BOUNCE YAY!")
    bounce = False
    cv2.imshow('test', frame)

    # q exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    print()
cap.release()
cv2.destroyAllWindows()
