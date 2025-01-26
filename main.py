# main.py
import pygame
import cv2
import mediapipe as mp
import math
import time
import Gesture_Judgement as gesture
import Hand_Click as handclick
import saveandload as sal
import draw, file
import os

# 初始化 PyGame 和画布
pygame.init()

screen = pygame.display.set_mode((800, 600), pygame.FULLSCREEN)
info = pygame.display.Info()  # 获取显示屏信息
screen_width, screen_height = info.current_w, info.current_h
canvas = pygame.Surface((1000, 750))  # 初始画布大小 (可以更大)
canvas.fill((255, 255, 255))  # 白色背景
shadow_layer = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)  # 专用阴影层

pygame.display.set_caption("Gesture Drawing")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1600)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)

# 初始化 MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# 帧率控制
clock = pygame.time.Clock()

# 当前模式：绘画、擦除或拖拽
x, y = 0, 0  # 当前食指指尖坐标
prev_x, prev_y = None, None
canvas_offset_x, canvas_offset_y = 0, 0  # 画布偏移
is_dragging = False  # 是否正在拖拽
drag_start_x, drag_start_y = 0, 0  # 拖拽起始坐标

# 初始化字体
pygame.font.init()
font = pygame.font.SysFont(None, 30)  # 使用系统默认字体，大小为30

# 替换准心图标
pen_image = pygame.image.load(handclick.asset_path + "pencil.ico")
rub_image = pygame.image.load(handclick.asset_path + "eraser.ico")
pen_image = pygame.transform.scale(pen_image, (30, 30))  # 调整为合适尺寸
rub_image = pygame.transform.scale(rub_image, (30, 30))

# 导入的文件列表
loaded_files = handclick.loaded_files

# 图片层
image_layer = pygame.Surface((1000, 750), pygame.SRCALPHA)  # 初始图片层大小 (可以更大)
image_layer.fill((0, 0, 0, 0))  # 透明背景

# 主循环
running = True
prev_time = time.time()

while running:
    # 注意，键盘按键需在英文输入法下进行！！！
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:  # 按 "S" 键保存
                sal.export_canvas_with_dialog(canvas)
                running = False
                print("保存画布")
            if event.key == pygame.K_q:  # 按 "Q" 键退出
                running = False
                print("退出程序")
    if handclick.mode == "save":
        sal.export_canvas_with_dialog(canvas)
        print("保存画布")
        running = False

    # 捕获摄像头图像
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    handclick.draw_buttons(screen, screen_width, screen_height)

    # 手势检测
    result = hands.process(rgb_frame)
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # 绘制手部关键点和连接线
            mp_drawing = mp.solutions.drawing_utils
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # 获取食指指尖坐标
            index_finger = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x, y = int(index_finger.x * screen_width), int(index_finger.y * screen_height)

            # 清空阴影层
            shadow_layer.fill((0, 0, 0, 0))

            # 绘制阴影
            draw.draw_shadow(shadow_layer, handclick.current_color, x, y, handclick.current_thickness)

            # 更新阴影坐标
            shadow_pos = (x, y)

            # 调用按钮点击处理函数
            handclick.handle_button_click(shadow_pos, canvas)

            if handclick.mode == "drag":  # drag 模式下
                if not gesture.operator(hand_landmarks):
                    is_dragging = False
                    prev_x, prev_y = None, None  # 停止拖拽时重置坐标
                elif gesture.operator(hand_landmarks) and not is_dragging:
                    # 手掌捏合时开始拖拽
                    is_dragging = True
                    drag_start_x, drag_start_y = x, y
                elif is_dragging:  # 如果正在拖拽，更新画布偏移
                    if any(file["rect"].collidepoint(x, y) for file in loaded_files):
                        for file in loaded_files:
                            if file["rect"].collidepoint(x, y):
                                file["rect"].x += x - drag_start_x
                                file["rect"].y += y - drag_start_y
                                drag_start_x, drag_start_y = x, y
                    else:
                        canvas_offset_x += x - drag_start_x
                        canvas_offset_y += y - drag_start_y
                        drag_start_x, drag_start_y = x, y  # 更新起始坐标
                        # 更新图片层的偏移
                        for file in loaded_files:
                            file["rect"].x += x - drag_start_x
                            file["rect"].y += y - drag_start_y

            # 绘画或擦除
            elif handclick.mode == "draw":
                if gesture.operator(hand_landmarks):
                    if prev_x is not None and prev_y is not None:
                        # 在前一个点和当前点之间插值，确保绘制平滑
                        steps = max(abs(x - prev_x), abs(y - prev_y)) // 2
                        if steps == 0:
                            steps = 1  # 至少画一个
                        for i in range(steps + 1):
                            interpolated_x = prev_x + (x - prev_x) * i // steps
                            interpolated_y = prev_y + (y - prev_y) * i // steps
                            # 计算缩放后的坐标
                            canvas_x = (interpolated_x - canvas_offset_x) / handclick.current_scale
                            canvas_y = (interpolated_y - canvas_offset_y) / handclick.current_scale
                            # 动态扩展画布以确保绘图范围足够
                            canvas, image_layer = draw.ensure_canvas_size(canvas, image_layer, x - canvas_offset_x, y - canvas_offset_y, handclick.current_scale)
                            # 在图片层上绘制
                            draw.draw_brush(image_layer, canvas_x, canvas_y,
                                            handclick.current_thickness, handclick.current_color)
                    prev_x, prev_y = x, y
                else:
                    prev_x, prev_y = None, None
            elif handclick.mode == "erase":
                if gesture.operator(hand_landmarks):
                    if prev_x is not None and prev_y is not None:
                        # 在前一个点和当前点之间插值，确保绘制平滑
                        steps = max(abs(x - prev_x), abs(y - prev_y)) // 2
                        if steps == 0:
                            steps = 1  # 至少画一个
                        for i in range(steps + 1):
                            interpolated_x = prev_x + (x - prev_x) * i // steps
                            interpolated_y = prev_y + (y - prev_y) * i // steps
                            # 计算缩放后的坐标
                            canvas_x = (interpolated_x - canvas_offset_x) / handclick.current_scale
                            canvas_y = (interpolated_y - canvas_offset_y) / handclick.current_scale
                            # 动态扩展画布以确保绘图范围足够
                            canvas, image_layer = draw.ensure_canvas_size(canvas, image_layer, x - canvas_offset_x, y - canvas_offset_y, handclick.current_scale)
                            # 在图片层上擦除
                            draw.draw_brush(image_layer, canvas_x, canvas_y,
                                            handclick.current_thickness, (0, 0, 0, 0))
                    prev_x, prev_y = x, y
                else:
                    prev_x, prev_y = None, None
            elif handclick.mode == "file":
                print("文件选择，功能待完成")

            else:
                # 当手指不再捏合时，重置 prev_x 和 prev_y
                prev_x, prev_y = None, None

    else:
        # 如果没有检测到手，重置坐标和拖拽状态
        prev_x, prev_y = None, None
        is_dragging = False

    # 在新窗口中显示手势检测画面
    #cv2.imshow("Gesture Detection", frame)  # 显示带关键点和连接线的手势检测画面

    screen.fill((255, 255, 255))

    # 绘制画布内容，考虑偏移
    scaled_width = int(canvas.get_width() * handclick.current_scale)
    scaled_height = int(canvas.get_height() * handclick.current_scale)
    scaled_canvas = pygame.transform.scale(canvas, (scaled_width, scaled_height))
    screen.blit(scaled_canvas, (canvas_offset_x, canvas_offset_y))
    
    # 绘制导入的文件
    for file in loaded_files:
        # 重新生成缩放后的图像
        scaled_image = pygame.transform.scale(file["original_image"], (int(file["original_image"].get_width() * file["scale"]), int(file["original_image"].get_height() * file["scale"])))
        file["image"] = scaled_image
        file["rect"] = scaled_image.get_rect(topleft=file["rect"].topleft)
        screen.blit(scaled_image, file["rect"].topleft)
        pygame.draw.rect(screen, (0, 255, 0), file["rect"], 2)  # 绿色边框

        # 绘制放大和缩小按钮
        plus_button_rect = pygame.Rect(file["rect"].topright[0] + 5, file["rect"].topright[1] - 15, 30, 30)
        minus_button_rect = pygame.Rect(file["rect"].topright[0] + 5, file["rect"].topright[1] + 5, 30, 30)
        pygame.draw.rect(screen, (0, 0, 255), plus_button_rect)
        pygame.draw.rect(screen, (255, 0, 0), minus_button_rect)

        # 检查按钮点击
        if plus_button_rect.collidepoint(shadow_pos):
            file["scale"] = min(file["scale"] + 0.1, 2.0)
        elif minus_button_rect.collidepoint(shadow_pos):
            file["scale"] = max(file["scale"] - 0.1, 0.5)

    # 绘制图片层内容，考虑偏移
    scaled_image_layer = pygame.transform.scale(image_layer, (scaled_width, scaled_height))
    screen.blit(scaled_image_layer, (canvas_offset_x, canvas_offset_y))

    # 绘制画布边界
    draw.draw_canvas_border(screen, canvas, canvas_offset_x, canvas_offset_y, handclick.current_scale)
    # 绘制阴影
    screen.blit(shadow_layer, (0, 0))
    # 绘制准心图标
    if handclick.mode == "draw":
        screen.blit(pen_image, (x - pen_image.get_width() // 2, y - pen_image.get_height() // 2))
    elif handclick.mode == "erase":
        screen.blit(rub_image, (x - rub_image.get_width() // 2, y - rub_image.get_height() // 2))
    #绘制按钮
    handclick.draw_buttons(screen, screen_width, screen_height)  # 绘制按钮

    # 绘制当前模式
    mode_text = font.render(f"Mode: {handclick.mode}", True, (0, 0, 0))  # 黑色文本
    screen.blit(mode_text, (600, 100))  # 在右上角显示模式
    # 显示当前颜色和粗细
    color_text = font.render(f"Color: {handclick.current_color}", True, (0, 0, 0))  # 黑色文本
    screen.blit(color_text, (600, 140))
    thickness_text = font.render(f"Thickness: {handclick.current_thickness}", True, (0, 0, 0))
    screen.blit(thickness_text, (600, 170))
    # 显示当前画布大小
    size_text = font.render(f"Canvas_Size: {canvas.get_width()}*{canvas.get_height()}", True, (0, 0, 0))
    screen.blit(size_text, (550, 230))
    # 显示当前缩放
    scale_text = font.render(f"Scale: {handclick.current_scale:.2f}", True, (0, 0, 0))
    screen.blit(scale_text, (600, 200))
    # 显示当前偏移
    offset_text = font.render(f"offset: {canvas_offset_x, canvas_offset_y}", True, (0, 0, 0))
    screen.blit(offset_text, (100, 570))
    # 显示当前坐标
    pos_text = font.render(f"pos: {x, y}", True, (0, 0, 0))
    screen.blit(pos_text, (100, 540))

    # 计算和显示帧率
    current_time = time.time()
    fps = 1 / (current_time - prev_time) if current_time - prev_time > 0 else 0
    prev_time = current_time
    fps_text = font.render(f"FPS: {fps:.2f}", True, (0, 0, 0))
    screen.blit(fps_text, (screen.get_width() - fps_text.get_width() - 10, screen.get_height() - fps_text.get_height() - 10))

    pygame.display.flip()

cap.release()
cv2.destroyAllWindows()  # 关闭所有OpenCV窗口
pygame.quit()