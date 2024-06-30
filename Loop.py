# General processing import
import cv2
import numpy as np
# mediapipe import
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Event Manager import
from EventManager import EventManager

# Mouse
import pyautogui

# Drawing functions
MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54) # vibrant green

def draw_landmarks_on_image(rgb_image, detection_result):
  hand_landmarks_list = detection_result.hand_landmarks
  handedness_list = detection_result.handedness
  annotated_image = np.copy(rgb_image)

  # Loop through the detected hands to visualize.
  for idx in range(len(hand_landmarks_list)):
    hand_landmarks = hand_landmarks_list[idx]
    handedness = handedness_list[idx]

    # Draw the hand landmarks.
    hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    hand_landmarks_proto.landmark.extend([
      landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
    ])
    solutions.drawing_utils.draw_landmarks(
      annotated_image,
      hand_landmarks_proto,
      solutions.hands.HAND_CONNECTIONS,
      solutions.drawing_styles.get_default_hand_landmarks_style(),
      solutions.drawing_styles.get_default_hand_connections_style())

    # Get the top left corner of the detected hand's bounding box.
    height, width, _ = annotated_image.shape
    x_coordinates = [landmark.x for landmark in hand_landmarks]
    y_coordinates = [landmark.y for landmark in hand_landmarks]
    text_x = int(min(x_coordinates) * width)
    text_y = int(min(y_coordinates) * height) - MARGIN

    # Draw handedness (left or right hand) on the image.
    cv2.putText(annotated_image, f"{handedness[0].category_name}",
                (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

  return annotated_image

# Create an HandLandmarker object.
base_options = python.BaseOptions(model_asset_path='./Mediapipe/hand_landmarker.task')
options = vision.HandLandmarkerOptions(base_options=base_options,
                                       num_hands=1)
detector = vision.HandLandmarker.create_from_options(options)

# Capture Video
camera = cv2.VideoCapture(0)

# Create Event Manager
thumb_index_tip = EventManager("thumb and index tip", [4, 8])
thumb_middle_tip = EventManager("thumb and middle tip", [4, 12])

def click():
    pyautogui.click()

def double_click():
    pyautogui.doubleClick()

thumb_index_tip.setSingleTapCallback(click)
thumb_middle_tip.setSingleTapCallback(double_click)

while camera.isOpened():

    # Get camera resolution
    width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Read the current frame from the camera
    ret, frame = camera.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    
    # Convert the BGR image to RGB before processing.
    rgb_frame = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

    # Detect hand landmarks from the input image.
    detection_result = detector.detect(rgb_frame)

    # Show camera feed
    annotated_image = draw_landmarks_on_image(rgb_frame.numpy_view(), detection_result)
    

    # Create Hand Model
    if len(detection_result.hand_landmarks) > 0:
        thumb_index_tip.update(detection_result.hand_landmarks[0])
        thumb_middle_tip.update(detection_result.hand_landmarks[0])

        if thumb_index_tip.isDragging:
            origin = thumb_index_tip.dragOrigin

            # calculate vector between thumb and index tip
            current = thumb_index_tip.dragCurrent

            # Convert origin and current to pixel coordinates
            origin = origin * [width, height]
            current = current * [width, height]

            # Move mouse based of difference between origin and current
            pyautogui.moveRel((current[0] - origin[0]) * 0.25, (current[1] - origin[1]) * 0.25)

            # Draw a line between the thumb and index tip
            cv2.line(annotated_image, (int(origin[0]), int(origin[1])), (int(current[0]), int(current[1])), (0, 255, 0), 2)
        
        if thumb_middle_tip.isDragging:
            origin = thumb_middle_tip.dragOrigin

            # calculate vector between thumb and middle tip
            current = thumb_middle_tip.dragCurrent

            # Convert origin and current to pixel coordinates
            origin = origin * [width, height]
            current = current * [width, height]

            # Scroll based of difference between origin and current
            pyautogui.scroll(- (current[1] - origin[1]) * 0.05)

            # Draw a line between the thumb and middle tip
            cv2.line(annotated_image, (int(origin[0]), int(origin[1])), (int(current[0]), int(current[1])), (0, 0, 255), 2)
        
    cv2.imshow("Camera Feed", annotated_image)

    # Quit if 'q' is pressed
    if cv2.waitKey(1) == ord("q"):
        break

camera.release()