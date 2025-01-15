import pygame
import cv2
import mediapipe as mp
import math
import time
import Gesture_Judgement as gesture
import Hand_Click as handclick
import draw, file
import saveandload as sal
import os

# 初始化 PyGame 和画布
pygame.init()
screen = pygame.display.set_mode((800, 600))
canvas = pygame.Surface((1000, 750))  # 初始画布大小 (可以更大)
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

#帧率控制
clock = pygame.time.Clock()

# 当前模式：绘画、擦除或拖拽

x, y = 0, 0  # 当前食指指尖坐标
prev_x, prev_y = None, None
canvas_offset_x, canvas_offset_y = 0, 0  # 画布偏移
is_dragging = False  # 是否正在拖拽
drag_start_x, drag_start_y = 0, 0  # 拖拽起始坐标


# 初始化字体
pygame.font.init()
font = pygame.font.SysFont(None, 30)  # 使用系统默认字体，大小为10

# 初始化文件列表
file_button = pygame.Rect(150, 10, 50, 50)
show_file_list = False
file_list = []
selected_file_index = -1
supported_extensions = (".png", ".gif", ".jpg")

# 文件拖拽相关变量
dragging_file = False
dragged_file_rect = None
drag_file_path = None
drag_file_pos = (0, 0)

# 主循环
running = True
prev_time = time.time()

while running:

    #注意，键盘按键需在英文输入法下进行！！！
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:  # 按 "S" 键保存
                sal.export_canvas_with_dialog(canvas)
                print("保存画布")
            if event.key == pygame.K_q:  # 按 "Q" 键退出
                running = False
                print("退出程序")
            if event.key == pygame.K_l:  # 按 "L" 键导入画布
                sal.load_canvas_with_dialog(canvas)
                print("加载画布")

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

            # 绘制手部关键点和连接线
            mp_drawing = mp.solutions.drawing_utils
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)


            # 获取食指指尖坐标
            index_finger = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x, y = int(index_finger.x * 800), int(index_finger.y * 600)

            # 清空阴影层
            shadow_layer.fill((0, 0, 0, 0))

            # 绘制阴影
            draw.draw_shadow(shadow_layer, handclick.current_color, x, y, handclick.current_thickness)

            #更新阴影坐标
            shadow_pos = (x, y)

            # 调用按钮点击处理函数
            handclick.handle_button_click(shadow_pos, canvas)

            if handclick.mode == "drag": # drag 模式下
                if not gesture.operator(hand_landmarks):
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
                        # 动态扩展画布以确保绘图范围足够
                        canvas = draw.ensure_canvas_size(canvas, x-canvas_offset_x, y-canvas_offset_y)

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

            elif handclick.mode == "file" and gesture.operator(hand_landmarks):
                if not show_file_list:  # 点击按钮显示文件列表
                    file_list = file.get_files_in_directory(".", supported_extensions)
                    show_file_list = not show_file_list  # 切换显示状态

                # 检测文件列表项的触碰
                if show_file_list:
                    for i, file_name in enumerate(file_list):
                        file_rect = pygame.Rect(file_button.right + 10, file_button.top + i * 30, 200, 30)
                        if file_rect.collidepoint(x, y) and gesture.operator(hand_landmarks):  # 手势触碰文件项
                            selected_file_index = i
                            file.add_file_to_canvas(file_list[i], canvas, 50, 50)  # 添加文件到画布
                            show_file_list = False  # 隐藏文件列表
                            break

                # 拖拽文件
                if dragging_file:
                    dragged_file_rect.x = x - dragged_file_rect.width // 2
                    dragged_file_rect.y = y - dragged_file_rect.height // 2

                # 检查释放手势
                if not gesture.operator(hand_landmarks):
                    file.add_file_to_canvas(file_list[selected_file_index], canvas, dragged_file_rect.x, dragged_file_rect.y)  # 添加文件到画布
                    dragging_file = False
                    show_file_list = False

            else:
                # 当手指不再捏合时，重置 prev_x 和 prev_y
                prev_x, prev_y = None, None
            
    else:
        # 如果没有检测到手，重置坐标和拖拽状态
        prev_x, prev_y = None, None
        is_dragging = False

    # 在新窗口中显示手势检测画面
    cv2.imshow("Gesture Detection", frame)  # 显示带关键点和连接线的手势检测画面

    screen.fill((255, 255, 255))

    # 绘制画布内容，考虑偏移
    screen.blit(canvas, (canvas_offset_x, canvas_offset_y))
    screen.blit(shadow_layer, (0, 0))
    # 绘制画布边界
    draw.draw_canvas_border(screen, canvas, canvas_offset_x, canvas_offset_y)

    handclick.draw_buttons(screen)  # 绘制按钮

    # 绘制当前模式
    mode_text = font.render(f"Mode: {handclick.mode}", True, (0, 0, 0))  # 黑色文本
    screen.blit(mode_text, (600, 10))  # 在右上角显示模式
    # 显示当前颜色和粗细
    color_text = font.render(f"Color: {handclick.current_color}", True, (0, 0, 0))  # 黑色文本
    screen.blit(color_text, (600, 40))
    thickness_text = font.render(f"Thickness: {handclick.current_thickness}", True, (0, 0, 0))
    screen.blit(thickness_text, (600, 70))
    # 显示当前偏移
    offset_text = font.render(f"offset: {canvas_offset_x, canvas_offset_y}", True, (0, 0, 0))
    screen.blit(offset_text, (100, 570))
    # 显示当前坐标
    pos_text = font.render(f"pos: {x, y}", True, (0, 0, 0))
    screen.blit(pos_text, (100, 540))

    # 绘制文件列表
    if show_file_list:
        for i, file_name in enumerate(file_list):
            file_rect = pygame.Rect(file_button.right + 10, file_button.top + i * 30, 200, 30)
            pygame.draw.rect(screen, (200, 200, 200), file_rect)
            font = pygame.font.Font(None, 24)
            text = font.render(file_name, True, (0, 0, 0))
            screen.blit(text, file_rect.topleft)

    # 绘制拖动的文件项
    if dragging_file:
        pygame.draw.rect(screen, (200, 200, 200), dragged_file_rect)
        font = pygame.font.Font(None, 24)
        text = font.render(file_list[selected_file_index], True, (0, 0, 0))
        screen.blit(text, dragged_file_rect.topleft)
    # 计算和显示帧率
    current_time = time.time()
    fps = 1 / (current_time - prev_time) if current_time - prev_time > 0 else 0
    prev_time = current_time
    fps_text = font.render(f"FPS: {fps:.2f}", True, (0, 0, 0))
    screen.blit(fps_text, (screen.get_width() - fps_text.get_width() - 10, screen.get_height() - fps_text.get_height() - 10))

    pygame.display.flip()

    # 退出条件
    #if cv2.waitKey(1) & 0xFF == ord('q'):  # 按下 'q' 键退出
        #break

cap.release()
cv2.destroyAllWindows()  # 关闭所有OpenCV窗口
pygame.quit()
