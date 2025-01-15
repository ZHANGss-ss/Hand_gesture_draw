import pygame
import cv2
import mediapipe as mp
import math
import time
import Gesture_Judgement as gesture
import Hand_Click as handclick
import draw
import file_handler

# 初始化 PyGame 和画布
pygame.init()
screen = pygame.display.set_mode((800, 600))
canvas = pygame.Surface((20000, 15000))  # 初始画布大小
canvas.fill((255, 255, 255))  # 白色背景
shadow_layer = pygame.Surface((800, 600), pygame.SRCALPHA)  # 专用阴影层

pygame.display.set_caption("Gesture Drawing with Files")

# 初始化文件处理器
file_handler = file_handler.FileHandler()

# 初始化摄像头
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

# 初始化变量
prev_x, prev_y = None, None
canvas_offset_x, canvas_offset_y = 0, 0  # 画布偏移
drawing_on_file = False  # 标记是否在文件上绘画

# 初始化字体
pygame.font.init()
font = pygame.font.SysFont(None, 30)

# 主循环
running = True
prev_time = time.time()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # 检测Ctrl+O组合键
            keys = pygame.key.get_pressed()
            if event.key == pygame.K_o and (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]):
                file_obj = file_handler.load_file()
                if file_obj:
                    file_handler.add_file_object(file_obj)

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

            # 检查是否悬停在按钮上
            handclick.check_button_hover((x, y))

            # 绘制阴影
            handclick.draw_shadow(shadow_layer, (x, y))

            if handclick.is_dragging():
                # 处理文件对象的拖拽和缩放
                file_handler.handle_event((x, y), gesture.operator(hand_landmarks))
            elif gesture.operator(hand_landmarks):
                if handclick.is_erasing():
                    # 尝试在文件上擦除
                    drawing_on_file = file_handler.draw_on_selected((x, y), (255, 255, 255, 0), handclick.current_thickness)
                    
                    # 如果不在文件上，则在画布上擦除
                    if not drawing_on_file and prev_x is not None and prev_y is not None:
                        steps = max(abs(x - prev_x), abs(y - prev_y)) // 2
                        if steps == 0:
                            steps = 1
                        for i in range(steps + 1):
                            interpolated_x = prev_x + (x - prev_x) * i // steps
                            interpolated_y = prev_y + (y - prev_y) * i // steps
                            draw.draw_brush(canvas, 
                                          interpolated_x - canvas_offset_x, 
                                          interpolated_y - canvas_offset_y,
                                          handclick.current_thickness,
                                          (255, 255, 255))
                else:
                    # 尝试在文件上绘画
                    drawing_on_file = file_handler.draw_on_selected((x, y), handclick.current_color, handclick.current_thickness)
                    
                    # 如果不在文件上，则在画布上绘画
                    if not drawing_on_file and prev_x is not None and prev_y is not None:
                        steps = max(abs(x - prev_x), abs(y - prev_y)) // 2
                        if steps == 0:
                            steps = 1
                        for i in range(steps + 1):
                            interpolated_x = prev_x + (x - prev_x) * i // steps
                            interpolated_y = prev_y + (y - prev_y) * i // steps
                            draw.draw_brush(canvas, 
                                          interpolated_x - canvas_offset_x, 
                                          interpolated_y - canvas_offset_y,
                                          handclick.current_thickness,
                                          handclick.current_color)
                prev_x, prev_y = x, y
            else:
                prev_x, prev_y = None, None
                drawing_on_file = False
    else:
        prev_x, prev_y = None, None
        drawing_on_file = False

    # 绘制界面
    screen.fill((255, 255, 255))
    
    # 绘制画布内容
    screen.blit(canvas, (canvas_offset_x, canvas_offset_y))
    
    # 绘制文件对象
    file_handler.draw(screen)
    
    # 绘制阴影层和按钮
    screen.blit(shadow_layer, (0, 0))
    handclick.draw_buttons(screen)

    # 显示FPS
    current_time = time.time()
    fps = 1 / (current_time - prev_time)
    prev_time = current_time
    fps_text = font.render(f'FPS: {int(fps)}', True, (0, 0, 0))
    screen.blit(fps_text, (10, 10))

    pygame.display.flip()

# 清理资源
cap.release()
cv2.destroyAllWindows()
pygame.quit()
