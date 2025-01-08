import math
import cv2
import mediapipe as mp

# 初始化 MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def calculate_distance(point1, point2):
    """计算两点之间的欧几里得距离"""
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

def is_palm_open(hand_landmarks, threshold=0.2):
    """判断手掌是否完全张开"""
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
    fingers = [
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP,
        mp_hands.HandLandmark.THUMB_TIP
    ]
    open_count = sum(calculate_distance(
        (hand_landmarks.landmark[f].x, hand_landmarks.landmark[f].y),
        (wrist.x, wrist.y)
    ) > threshold
    and operator(hand_landmarks) != True for f in fingers)
    return open_count == 5

def operator(hand_landmarks, threshold1=0.1, threshold2=0.03):
    """判断拇指和食指是否靠拢"""
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]  # 拇指指尖
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]  # 食指指尖
    index_pip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]  # 食指自上而下第二个关键点

    distance_tip = calculate_distance((thumb_tip.x, thumb_tip.y), (index_tip.x, index_tip.y))
    distance_pip = calculate_distance((thumb_tip.x, thumb_tip.y), (index_pip.x, index_pip.y))

    return distance_tip < threshold1 or distance_pip < threshold2  # 判断两指是否靠拢