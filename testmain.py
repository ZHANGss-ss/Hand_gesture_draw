import pygame
import cv2
import mediapipe as mp
import time
import Gesture_Judgement as gesture
import Hand_Click as handclick
import draw
import fitz  # 导入 PyMuPDF
import adjust_canvas_size

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
INITIAL_CANVAS_WIDTH = SCREEN_WIDTH  # 初始画布和屏幕一样大
INITIAL_CANVAS_HEIGHT = SCREEN_HEIGHT
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
EXTEND_MARGIN = 100  # 画布扩展的边缘大小

# 初始化 Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
background_layer = pygame.Surface((INITIAL_CANVAS_WIDTH, INITIAL_CANVAS_HEIGHT)) # 背景层
background_layer.fill(WHITE) # 初始化背景为白色
drawing_layer = pygame.Surface((INITIAL_CANVAS_WIDTH, INITIAL_CANVAS_HEIGHT), pygame.SRCALPHA)  # 线条层
shadow_layer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
pygame.display.set_caption("Gesture Drawing with Erase")

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

# 帧率控制
clock = pygame.time.Clock()

# 初始状态
prev_x, prev_y = None, None
canvas_offset_x, canvas_offset_y = 0, 0
is_dragging = False
drag_start_x, drag_start_y = 0, 0
canvas_width = INITIAL_CANVAS_WIDTH  # 当前画布宽度
canvas_height = INITIAL_CANVAS_HEIGHT  # 当前画布高度

# 初始化字体
pygame.font.init()
font = pygame.font.SysFont(None, 30)

# PDF 相关
pdf_scale = 0.8  # PDF 缩放比例

def load_pdf(pdf_path):
    global background_layer, canvas_width, canvas_height, canvas_offset_x, canvas_offset_y
    try:
        print(f"Attempting to load PDF from: {pdf_path}")
        pdf_document = fitz.open(pdf_path)
        first_page = pdf_document[0]
        pix = first_page.get_pixmap()
        image_data = pix.samples
        image_width = pix.width
        image_height = pix.height

        pdf_surface = pygame.image.frombuffer(image_data, (image_width, image_height), "RGB")

        # 直接设置画布大小，与PDF尺寸一致
        canvas_width = image_width
        canvas_height = image_height
        
        new_background_layer = pygame.Surface((canvas_width, canvas_height))
        new_background_layer.fill(WHITE) # 初始化背景为白色
        
        # 将PDF绘制到背景层上
        new_background_layer.blit(pdf_surface, (0,0))
       
        background_layer = new_background_layer
        
        new_drawing_layer = pygame.Surface((canvas_width, canvas_height), pygame.SRCALPHA) # 创建新的线条层

        global drawing_layer
        drawing_layer = new_drawing_layer
        
        canvas_offset_x = 0  # 初始化偏移量
        canvas_offset_y = 0

        global pdf_scale
        pdf_scale = 1.0  # 设置缩放为 1，不再缩放

        print(f"PDF loaded successfully. Dimensions: {pix.width}x{pix.height}")
    except Exception as e:
        print(f"Error loading PDF: {e}")

def extend_canvas(x, y):
    """动态扩展画布"""
    global background_layer, drawing_layer, canvas_width, canvas_height, canvas_offset_x, canvas_offset_y

    # 检查是否需要扩展画布
    if x - canvas_offset_x < EXTEND_MARGIN:
        expand_left = True
    else:
        expand_left = False

    if y - canvas_offset_y < EXTEND_MARGIN:
        expand_top = True
    else:
        expand_top = False

    if x - canvas_offset_x > canvas_width - EXTEND_MARGIN:
        expand_right = True
    else:
        expand_right = False

    if y - canvas_offset_y > canvas_height - EXTEND_MARGIN:
        expand_bottom = True
    else:
        expand_bottom = False

    if expand_left or expand_right or expand_top or expand_bottom:
        new_canvas_width = canvas_width
        new_canvas_height = canvas_height
        new_canvas_offset_x = canvas_offset_x
        new_canvas_offset_y = canvas_offset_y

        if expand_left:
            new_canvas_width += EXTEND_MARGIN
            new_canvas_offset_x -= EXTEND_MARGIN
        if expand_right:
            new_canvas_width += EXTEND_MARGIN
        if expand_top:
            new_canvas_height += EXTEND_MARGIN
            new_canvas_offset_y -= EXTEND_MARGIN
        if expand_bottom:
            new_canvas_height += EXTEND_MARGIN

        new_background_layer = pygame.Surface((new_canvas_width, new_canvas_height))
        new_background_layer.fill(WHITE) # 初始化为白色
        new_background_layer.blit(background_layer, (-new_canvas_offset_x + canvas_offset_x, -new_canvas_offset_y + canvas_offset_y))
        background_layer = new_background_layer

        new_drawing_layer = pygame.Surface((new_canvas_width, new_canvas_height), pygame.SRCALPHA)
        new_drawing_layer.blit(drawing_layer, (-new_canvas_offset_x + canvas_offset_x, -new_canvas_offset_y + canvas_offset_y))
        drawing_layer = new_drawing_layer

        canvas_width = new_canvas_width
        canvas_height = new_canvas_height
        canvas_offset_x = new_canvas_offset_x
        canvas_offset_y = new_canvas_offset_y


def draw_on_canvas(x, y, color, thickness):
    """在画布上绘制，并检查是否需要扩展画布"""
    global drawing_layer
    extend_canvas(x, y)
    draw.draw_brush(drawing_layer, x - canvas_offset_x, y - canvas_offset_y, thickness, color)

def handle_hand_tracking(frame):
    """处理手部跟踪和绘制逻辑"""
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    global prev_x, prev_y, is_dragging, drag_start_x, drag_start_y, canvas_offset_x, canvas_offset_y

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing = mp.solutions.drawing_utils
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            index_finger = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x, y = int(index_finger.x * SCREEN_WIDTH), int(index_finger.y * SCREEN_HEIGHT)

            shadow_layer.fill((0, 0, 0, 0))
            draw.draw_shadow(shadow_layer, handclick.current_color, x, y, handclick.current_thickness)
            shadow_pos = (x, y)
            handclick.handle_button_click(shadow_pos, drawing_layer)

            if handclick.mode == "drag":
                handle_drag(hand_landmarks, x, y)

            elif handclick.mode in ("draw", "erase"):
                handle_draw_erase(hand_landmarks, x, y)
            else:
                prev_x, prev_y = None, None
    else:
        prev_x, prev_y = None, None
        is_dragging = False

def handle_drag(hand_landmarks, x, y):
    global is_dragging, drag_start_x, drag_start_y, canvas_offset_x, canvas_offset_y, prev_x, prev_y
    if not gesture.operator(hand_landmarks):
        is_dragging = False
        prev_x, prev_y = None, None
    elif gesture.operator(hand_landmarks) and not is_dragging:
        is_dragging = True
        drag_start_x, drag_start_y = x, y
    elif is_dragging:
        canvas_offset_x += x - drag_start_x
        canvas_offset_y += y - drag_start_y
        drag_start_x, drag_start_y = x, y

def handle_draw_erase(hand_landmarks, x, y):
    global prev_x, prev_y
    if gesture.operator(hand_landmarks):
        if prev_x is not None and prev_y is not None:
            steps = max(abs(x - prev_x), abs(y - prev_y)) // 2
            if steps == 0:
                steps = 1
            for i in range(steps + 1):
                interpolated_x = prev_x + (x - prev_x) * i // steps
                interpolated_y = prev_y + (y - prev_y) * i // steps
                color = handclick.current_color if handclick.mode == "draw" else (0,0,0,0)
                if handclick.mode == "erase":
                  draw.draw_brush(drawing_layer, interpolated_x - canvas_offset_x, interpolated_y - canvas_offset_y, handclick.current_thickness, (0,0,0,0))
                else:
                  draw_on_canvas(interpolated_x, interpolated_y, color, handclick.current_thickness)
        prev_x, prev_y = x, y
    else:
        prev_x, prev_y = None, None

def draw_ui(screen, fps):
    """绘制 UI 元素"""
    global  background_layer, drawing_layer, canvas_width, canvas_height, canvas_offset_x, canvas_offset_y

    screen.fill(WHITE)

    # 先绘制背景层
    screen.blit(background_layer, (canvas_offset_x, canvas_offset_y))
    # 再绘制线条层
    screen.blit(drawing_layer, (canvas_offset_x, canvas_offset_y))

    screen.blit(shadow_layer, (0, 0))
    handclick.draw_buttons(screen)

    mode_text = font.render(f"Mode: {handclick.mode}", True, BLACK)
    screen.blit(mode_text, (600, 10))
    color_text = font.render(f"Color: {handclick.current_color}", True, BLACK)
    screen.blit(color_text, (600, 40))
    thickness_text = font.render(f"Thickness: {handclick.current_thickness}", True, BLACK)
    screen.blit(thickness_text, (600, 70))
    offset_text = font.render(f"offset: {canvas_offset_x, canvas_offset_y}", True, BLACK)
    screen.blit(offset_text, (50, 570))

    fps_text = font.render(f"FPS: {fps:.2f}", True, BLACK)
    screen.blit(fps_text, (screen.get_width() - fps_text.get_width() - 10,
                             screen.get_height() - fps_text.get_height() - 10))

    # 绘制当前画布大小
    canvas_size_text = font.render(f"Canvas Size: {canvas_width}x{canvas_height}", True, BLACK)
    screen.blit(canvas_size_text, (10, SCREEN_HEIGHT - canvas_size_text.get_height() - 40))

# 主循环
running = True
prev_time = time.time()
pdf_path = ""  # PDF 路径
load_pdf(pdf_path)  # 加载 PDF
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.DROPFILE:  # 处理拖拽的文件
            pdf_path = event.file
            load_pdf(pdf_path)

    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)

    handle_hand_tracking(frame)

    cv2.imshow("Gesture Detection", frame)  # 显示检测画面

    current_time = time.time()
    fps = 1 / (current_time - prev_time) if current_time - prev_time > 0 else 0
    prev_time = current_time
    draw_ui(screen, fps)

    pygame.display.flip()
    clock.tick(FPS)  # 控制帧率

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pygame.quit()