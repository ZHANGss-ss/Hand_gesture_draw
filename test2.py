import pygame
import cv2
import mediapipe as mp
import time
import Gesture_Judgement as gesture
import Hand_Click as handclick
import draw
import fitz  # 导入 PyMuPDF

# 常量定义
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
INITIAL_CANVAS_WIDTH = SCREEN_WIDTH  # 初始画布和屏幕一样大
INITIAL_CANVAS_HEIGHT = SCREEN_HEIGHT
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
EXTEND_MARGIN = 100 #画布扩展的边缘大小

# 初始化 Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
canvas = pygame.Surface((INITIAL_CANVAS_WIDTH, INITIAL_CANVAS_HEIGHT))  # 初始画布大小
canvas.fill(WHITE)
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
clock.tick(60)

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
pdf_surface = None  # 用于保存 PDF 的 Pygame Surface
pdf_scale = 1.0    # PDF 缩放比例

def load_pdf(pdf_path):
    global pdf_surface, canvas, canvas_width, canvas_height, canvas_offset_x, canvas_offset_y
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
        canvas = pygame.Surface((canvas_width, canvas_height))
        canvas.fill(WHITE) #  初始化画布颜色
        
        canvas_offset_x = 0 # 初始化偏移量
        canvas_offset_y = 0 

        global pdf_scale
        pdf_scale = 1.0 # 设置缩放为 1，不再缩放
        
        print(f"PDF loaded successfully. Dimensions: {pix.width}x{pix.height}")
    except Exception as e:
        print(f"Error loading PDF: {e}")
        pdf_surface = None

# def extend_canvas(x, y):
#     """动态扩展画布"""
#     #（省略 extend_canvas 代码）
#     pass

def draw_on_canvas(x, y, color, thickness):
    """在画布上绘制，并检查是否需要扩展画布"""
    global canvas
    # extend_canvas(x,y)
    draw.draw_brush(canvas, x - canvas_offset_x, y - canvas_offset_y, thickness, color)
    

# def handle_hand_tracking(frame):
#     """处理手部跟踪和绘制逻辑"""
#     #（省略 handle_hand_tracking 代码）
#     pass

# def handle_drag(hand_landmarks,x, y):
#    #（省略 handle_drag 代码）
#    pass
#
# def handle_draw_erase(hand_landmarks, x, y):
#     #（省略 handle_draw_erase 代码）
#     pass

def draw_ui(screen, fps):
    global canvas_width, canvas_height, pdf_surface, canvas_offset_x, canvas_offset_y

    screen.fill(WHITE)  # 先填充背景

    # # 绘制 PDF
    # if pdf_surface:
    #     scaled_pdf = pygame.transform.scale(pdf_surface, (int(pdf_surface.get_width() * pdf_scale), int(pdf_surface.get_height() * pdf_scale)))
    #     screen.blit(scaled_pdf, (0, 0))  # 使用绝对坐标 (0,0)
    
    # 在 PDF 之上绘制画布
    screen.blit(canvas, (canvas_offset_x, canvas_offset_y))
    # 绘制 PDF
    if pdf_surface:
        scaled_pdf = pygame.transform.scale(pdf_surface, (int(pdf_surface.get_width() * pdf_scale), int(pdf_surface.get_height() * pdf_scale)))
        screen.blit(scaled_pdf, (0, 0))  # 使用绝对坐标 (0,0)
        
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
pdf_path = "/Users/zhangss/Desktop/23120842.pdf"  #  PDF 路径
load_pdf(pdf_path)    # 加载 PDF
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.DROPFILE:  # 处理拖拽的文件
            pdf_path = event.file
            load_pdf(pdf_path)

    # ret, frame = cap.read()
    # if not ret:
    #     break
    # frame = cv2.flip(frame, 1)
    #
    # handle_hand_tracking(frame)
    #
    # cv2.imshow("Gesture Detection", frame)  # 显示检测画面

    current_time = time.time()
    fps = 1 / (current_time - prev_time) if current_time - prev_time > 0 else 0
    prev_time = current_time
    draw_ui(screen, fps)

    pygame.display.flip()
    clock.tick(FPS)

cap.release()
cv2.destroyAllWindows()
pygame.quit()