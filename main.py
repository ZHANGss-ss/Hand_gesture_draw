import pygame
import cv2
import mediapipe as mp
import math
import time
import Gesture_Judgement as gesture
import Hand_Click as handclick
import draw


# 初始化 PyGame 和画布
pygame.init()
screen = pygame.display.set_mode((800, 600))
canvas = pygame.Surface((20000, 15000))  # 初始画布大小 (可以更大)
canvas.fill((255, 255, 255))  # 白色背景
shadow_layer = pygame.Surface((800, 600), pygame.SRCALPHA)  # 专用阴影层

pygame.display.set_caption("Gesture Drawing with Erase")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# 初始化 MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# 当前模式：绘画、擦除或拖拽

prev_x, prev_y = None, None
canvas_offset_x, canvas_offset_y = 0, 0  # 画布偏移
is_dragging = False  # 是否正在拖拽
drag_start_x, drag_start_y = 0, 0  # 拖拽起始坐标


# 初始化字体
pygame.font.init()
font = pygame.font.SysFont(None, 30)  # 使用系统默认字体，大小为10

# 主循环
running = True
prev_time = time.time()

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        

    # 捕获摄像头图像
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 手势检测
    result = hands.process(rgb_frame)
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:

            # 获取食指指尖坐标
            index_finger = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x, y = int(index_finger.x * 800), int(index_finger.y * 600)

            # 清空阴影层
            shadow_layer.fill((0, 0, 0, 0))

            # 绘制阴影
            draw.draw_shadow(shadow_layer, x, y, handclick.current_thickness)

            #更新阴影坐标
            shadow_pos = (x, y)

            # 调用按钮点击处理函数
            handclick.handle_button_click(shadow_pos)

            if handclick.mode == "drag": # drag 模式下
                if gesture.is_palm_open(hand_landmarks):
                     is_dragging = False
                     prev_x, prev_y = None, None  # 停止拖拽时重置坐标
                elif gesture.operator(hand_landmarks) and not is_dragging:
                     # 手掌捏合时开始拖拽
                    is_dragging = True
                    drag_start_x, drag_start_y = x, y
                elif is_dragging: # 如果正在拖拽，更新画布偏移
                    canvas_offset_x += x - drag_start_x
                    canvas_offset_y += y - drag_start_y
                    drag_start_x, drag_start_y = x, y  # 更新起始坐标

            # 绘画或擦除
            elif handclick.mode == "draw" and gesture.operator(hand_landmarks):
                if prev_x is not None and prev_y is not None:
                    # 在前一个点和当前点之间插值，确保绘制平滑
                    steps = max(abs(x - prev_x), abs(y - prev_y)) // 2
                    if steps == 0:
                        steps = 1  # 至少画一个
                    for i in range(steps + 1):
                        interpolated_x = prev_x + (x - prev_x) * i // steps
                        interpolated_y = prev_y + (y - prev_y) * i // steps
                        draw.draw_brush(canvas, interpolated_x - canvas_offset_x, interpolated_y - canvas_offset_y,
                                  handclick.current_thickness,handclick.current_color)
                prev_x, prev_y = x, y
            elif handclick.mode == "erase" and gesture.operator(hand_landmarks):
                if prev_x is not None and prev_y is not None:
                    # 在前一个点和当前点之间插值，确保绘制平滑
                    steps = max(abs(x - prev_x), abs(y - prev_y)) // 2
                    if steps == 0:
                        steps = 1  # 至少画一个
                    for i in range(steps + 1):
                        interpolated_x = prev_x + (x - prev_x) * i // steps
                        interpolated_y = prev_y + (y - prev_y) * i // steps
                        draw.draw_brush(canvas, interpolated_x - canvas_offset_x, interpolated_y - canvas_offset_y,
                                  handclick.current_thickness, (255, 255, 255))
                prev_x, prev_y = x, y
            else:
                # 当手指不再捏合时，重置 prev_x 和 prev_y
                prev_x, prev_y = None, None
            
    else:
        # 如果没有检测到手，重置坐标和拖拽状态
        prev_x, prev_y = None, None
        is_dragging = False

    screen.fill((255, 255, 255))

    # 绘制画布内容，考虑偏移
    screen.blit(canvas, (canvas_offset_x, canvas_offset_y))
    screen.blit(shadow_layer, (0, 0))

    handclick.draw_buttons(screen)  # 绘制按钮

    pygame.display.flip()

cap.release()
cv2.destroyAllWindows()  # 关闭所有OpenCV窗口
pygame.quit()
