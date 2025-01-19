import cv2
import numpy as np
from collections import deque
from enum import Enum

class State(Enum):
    START = 1
    LEFT_BOUNCE = 2
    RIGHT_BOUNCE = 3

curr_state = State.START
prev_frame_num = 0
threshold = 50

# Game state machine
def advance_state_machine(left_bounce, right_bounce, frame_num):
    left_point = False
    right_point = False
    prev_state = curr_state
    if (curr_state == State.START):
        prev_frame_num = frame_num
        if (left_bounce):
            curr_state = State.LEFT_BOUNCE
        elif (right_bounce):
            curr_state = State.RIGHT_BOUNCE
        else:
            curr_state = State.START # don't change state
    elif (curr_state == State.LEFT_BOUNCE):
        if (left_bounce): # double bounce case
            prev_frame_num = frame_num
            curr_state = State.START
            right_point = True
        elif (right_bounce):
            prev_frame_num = frame_num
            curr_state = State.RIGHT_BOUNCE
        else:
            if ((frame_num - prev_frame_num) < threshold):
                curr_state = State.LEFT_BOUNCE # don't change state
            else:
                right_point = True
                curr_state = State.START
    elif (curr_state == State.RIGHT_BOUNCE):
        if (right_bounce): # double bounce case
            prev_frame_num = frame_num
            curr_state = State.START
            left_point = True
        elif (left_bounce):
            prev_frame_num = frame_num
            curr_state = State.LEFT_BOUNCE
        else:
            if ((frame_num - prev_frame_num) < threshold):
                curr_state = State.RIGHT_BOUNCE # don't change state
            else:
                left_point = True
                curr_state = State.START
    if (prev_state != curr_state):
        print("Entered state: " + curr_state.name)
    return (left_point, right_point)

# camera 
cap = cv2.VideoCapture(1)  # camera settings
cv2.namedWindow('test', cv2.WINDOW_NORMAL)
# (Optional) Set the initial window size
cv2.resizeWindow('test', 800, 600)  # Width, Height
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1600)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)
cap.set(cv2.CAP_PROP_FPS, 30)
actual_fps = cap.get(cv2.CAP_PROP_FPS)
print(f"Camera FPS set to: {actual_fps}")
# positions queue
ball_positions = deque(maxlen=4)
frame_count = 0

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
prev_touch = False
prev_above = False

# cv setup
if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    ret, frame = cap.read()
    frame_count += 1
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
    lower_red1 = np.array([0, 200, 150])    
    upper_red1 = np.array([10, 255, 255])
    # red 2 wraparound
    lower_red2 = np.array([170, 200, 150])  
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
    if(frame_count < 100):
        for contour in red_contours:
            area = cv2.contourArea(contour)

            if area > 1100 and area < 1400:  
                x, y, w, h = cv2.boundingRect(contour)
                net_post_x = x + w // 2  # x-coordinate of the net post
                net_post_detected = True

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(frame, f"area: {area}", (x, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # midpoint line (red)
                # cv2.line(frame, (net_post_x, 0), (net_post_x, frame.shape[0]), (0, 0, 255), 2)
                midpoint = net_post_x
                center_y = y + h // 2 

                # center of net (upper lower bound for table) (yellow)
                # cv2.line(frame, (0, center_y), (frame.shape[1], center_y), (0, 255, 255), 2)
                lower2_bound = center_y
                # upper bound line (magenta)
                cv2.line(frame, (0, y), (frame.shape[1], y), (255, 0, 255), 2)
                upper_bound = y
                # break  # only the first (largest) red contour is used
        for contour in table_contours:
            area = cv2.contourArea(contour)

            if area > 1000:  
                x, y, w, h = cv2.boundingRect(contour)
                net_post_x = x + w // 2  
                net_post_detected = True
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                # bottom of table?
                lower1_bound = y + h
                cv2.putText(frame, f"area: {area}", (x, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.line(frame, (0, lower2_bound), (frame.shape[1], lower2_bound), (0, 255, 255), 2)        
    cv2.line(frame, (0, lower1_bound), (frame.shape[1], lower1_bound), (0, 255, 255), 2)    
    cv2.line(frame, (0, upper_bound), (frame.shape[1], upper_bound), (255, 0, 255), 2)    


    for contour in ball_contours:
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)

        if perimeter == 0 or area < 50:  
            continue

        circularity = 4 * np.pi * (area / (perimeter ** 2))
        
        if 0.1 < circularity:  
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)
            bottom = center[1] + radius
            # print(f"bottom: {bottom}")
            cv2.circle(frame, center, radius, (0, 255, 0), 2)
            cv2.putText(frame, f"Ball {circularity}", (center[0] - 10, center[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            # determine side
            if(center[0] > midpoint):
                current_side = 0 # right
            else:
                current_side = 1 # left
            # print(current_side)
            
            # logic for bounce upper bound
            if(bottom < upper_bound):
                above = True
                # print("higher")
            else:
                above = False
            # logic for table touch
            if(bottom >= lower2_bound - 60 and bottom <= lower1_bound + 60 ):
                touch = True
                # print("on table")
            else:
                touch = False
            ball_positions.append((above, touch))
            if(not prev_touch and touch):
                bounce = True
            else:
                bounce = False
            prev_above = above
            prev_touch = touch
            # FSM?? for bounce detection
    left_point = False
    right_point = False
    if(bounce and current_side == 0): # right
        print("BOUNCE RIGHT!")
        (left_point, right_point) = advance_state_machine(False, True, frame_count)
    elif(bounce and current_side == 1): # left
        print("BOUNCE LEFT!")
        (left_point, right_point) = advance_state_machine(False, True, frame_count)
    else:
        (left_point, right_point) = advance_state_machine(False, False, frame_count)
    bounce = False
    if (left_point)
        print("Increment left point")
    if (right_point)
        print("Increment right point")
    cv2.imshow('test', frame)

    # q exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
