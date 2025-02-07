#main.py
import pygame
import cv2
import mediapipe as mp
import time
import Gesture_Judgement as gesture
import Hand_Click as handclick
import saveandload as sal
import draw, file

pygame.init()
# 设置窗口初始大小为800x600，并且可以调整大小
screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
screen_width, screen_height = screen.get_size()
canvas = pygame.Surface((1000, 750))
canvas.fill((255, 255, 255))
shadow_layer = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

pygame.display.set_caption("Gesture Drawing")
cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

clock = pygame.time.Clock()
x, y = 0, 0
prev_x, prev_y = None, None
canvas_offset_x, canvas_offset_y = 0, 0
is_dragging = False
drag_start_x, drag_start_y = 0, 0
font = pygame.font.SysFont(None, 30)
pen_image = pygame.image.load(handclick.asset_path + "pencil-black.png")
rub_image = pygame.image.load(handclick.asset_path + "eraser.png")
drag_image = pygame.image.load(handclick.asset_path + "mouse.png")
pen_image = pygame.transform.scale(pen_image, (30, 30))
rub_image = pygame.transform.scale(rub_image, (30, 30))
drag_image = pygame.transform.scale(drag_image, (30, 30))
loaded_files = handclick.loaded_files
image_layer = pygame.Surface((1000, 750), pygame.SRCALPHA)
image_layer.fill((0, 0, 0, 0))

running = True
prev_time = time.time()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            # 当窗口大小改变时，更新屏幕大小和shadow_layer
            screen_width, screen_height = event.w, event.h
            screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
            shadow_layer = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                handclick.handle_button_click(mouse_pos, canvas, image_layer, from_mouse=True)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False

    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    handclick.draw_buttons(screen, screen_width, screen_height)

    result = hands.process(rgb_frame)
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            index_finger = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x, y = int(index_finger.x * screen_width), int(index_finger.y * screen_height)

            shadow_layer.fill((0, 0, 0, 0))
            draw.draw_shadow(shadow_layer, handclick.current_color, x, y, handclick.current_thickness)
            handclick.handle_button_click((x, y), canvas, image_layer, from_mouse=False)

            if handclick.mode == "drag":
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

            elif handclick.mode in ["draw", "erase"]:
                if gesture.operator(hand_landmarks):
                    if prev_x is not None and prev_y is not None:
                        steps = max(abs(x - prev_x), abs(y - prev_y)) // 2
                        steps = steps if steps > 0 else 1
                        for i in range(steps + 1):
                            interpolated_x = prev_x + (x - prev_x) * i // steps
                            interpolated_y = prev_y + (y - prev_y) * i // steps
                            canvas_x = (interpolated_x - canvas_offset_x) / handclick.current_scale
                            canvas_y = (interpolated_y - canvas_offset_y) / handclick.current_scale
                            canvas, image_layer = draw.ensure_canvas_size(canvas, image_layer, x - canvas_offset_x, y - canvas_offset_y, handclick.current_scale)
                            if handclick.mode == "draw":
                                draw.draw_brush(image_layer, canvas_x, canvas_y, handclick.current_thickness, handclick.current_color)
                            else:
                                draw.draw_brush(image_layer, canvas_x, canvas_y, handclick.current_thickness, (0, 0, 0, 0))
                    prev_x, prev_y = x, y
                else:
                    prev_x, prev_y = None, None

    screen.fill((255, 255, 255))
    scaled_width = int(canvas.get_width() * handclick.current_scale)
    scaled_height = int(canvas.get_height() * handclick.current_scale)
    scaled_canvas = pygame.transform.scale(canvas, (scaled_width, scaled_height))
    screen.blit(scaled_canvas, (canvas_offset_x, canvas_offset_y))
    
    for file in loaded_files:
        scaled_image = pygame.transform.scale(file["original_image"], (int(file["original_image"].get_width() * file["scale"]), int(file["original_image"].get_height() * file["scale"])))
        file["image"] = scaled_image
        file["rect"] = scaled_image.get_rect(topleft=file["rect"].topleft)
        screen.blit(scaled_image, file["rect"].topleft)

    scaled_image_layer = pygame.transform.scale(image_layer, (scaled_width, scaled_height))
    screen.blit(scaled_image_layer, (canvas_offset_x, canvas_offset_y))
    draw.draw_canvas_border(screen, canvas, canvas_offset_x, canvas_offset_y, handclick.current_scale)
    screen.blit(shadow_layer, (0, 0))


    if handclick.mode == "erase":
        screen.blit(rub_image, (x - 15, y - 15))
    elif handclick.mode == "drag":
        screen.blit(drag_image, (x - 15, y - 15))

    handclick.draw_buttons(screen, screen_width, screen_height)
    mode_text = font.render(f"Mode: {handclick.mode}", True, (0, 0, 0))
    screen.blit(mode_text, (screen_width - 200, 10))

    current_time = time.time()
    fps = 1 / (current_time - prev_time) if current_time - prev_time > 0 else 0
    prev_time = current_time
    fps_text = font.render(f"FPS: {fps:.2f}", True, (0, 0, 0))
    screen.blit(fps_text, (screen_width - 120, screen_height - 40))

    pygame.display.flip()
    clock.tick(60)

cap.release()
cv2.destroyAllWindows()
pygame.quit()