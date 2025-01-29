#Hand_Click.py
import pygame
import time
import file

asset_path = "./png/"

# 工具栏设置
toolbar_width = 60
toolbar_height = 400
toolbar_x = 20
toolbar_y = 100
is_dragging_toolbar = False
toolbar_drag_start = (0, 0)  # 初始化为元组

# 按钮定义
def draw_buttons(surface, screen_width, screen_height):
    """绘制悬浮工具栏和按钮"""
    global buttons, images, toolbar_x, toolbar_y, is_dragging_toolbar, toolbar_drag_start

    # 处理工具栏拖动
    mouse_pos = pygame.mouse.get_pos()
    mouse_pressed = pygame.mouse.get_pressed()[0]
    
    if mouse_pressed:
        toolbar_rect = pygame.Rect(toolbar_x, toolbar_y, toolbar_width, toolbar_height)
        if toolbar_rect.collidepoint(mouse_pos):
            if not is_dragging_toolbar:
                is_dragging_toolbar = True
                toolbar_drag_start = (mouse_pos[0] - toolbar_x, mouse_pos[1] - toolbar_y)
    else:
        is_dragging_toolbar = False

    if is_dragging_toolbar:
        toolbar_x = mouse_pos[0] - toolbar_drag_start[0]
        toolbar_y = mouse_pos[1] - toolbar_drag_start[1]

    # 确保工具栏不会超出屏幕边界
    toolbar_x = max(0, min(toolbar_x, screen_width - toolbar_width))
    toolbar_y = max(0, min(toolbar_y, screen_height - toolbar_height))

    # 绘制半透明背景
    toolbar_surface = pygame.Surface((toolbar_width, toolbar_height), pygame.SRCALPHA)
    pygame.draw.rect(toolbar_surface, (240, 240, 240, 230), (0, 0, toolbar_width, toolbar_height), border_radius=10)
    surface.blit(toolbar_surface, (toolbar_x, toolbar_y))

    # 定义按钮位置
    button_spacing = 50
    buttons = [
        {"rect": pygame.Rect(toolbar_x + 10, toolbar_y + 10, 40, 40), "action": "color", "value": (255, 0, 0), "image": asset_path + "pencil-red.png"},
        {"rect": pygame.Rect(toolbar_x + 10, toolbar_y + 10 + button_spacing, 40, 40), "action": "color", "value": (0, 255, 0), "image": asset_path + "pencil-blue.png"},
        {"rect": pygame.Rect(toolbar_x + 10, toolbar_y + 10 + button_spacing * 2, 40, 40), "action": "color", "value": (0, 0, 255), "image": asset_path + "pencil-yellow.png"},
        {"rect": pygame.Rect(toolbar_x + 10, toolbar_y + 10 + button_spacing * 3, 40, 40), "action": "color", "value": (0, 0, 0), "image": asset_path + "pencil-black.png"},
        {"rect": pygame.Rect(toolbar_x + 10, toolbar_y + 10 + button_spacing * 4, 40, 40), "action": "decrease_thickness", "image": asset_path + "-.png"},
        {"rect": pygame.Rect(toolbar_x + 10, toolbar_y + 10 + button_spacing * 5, 40, 40), "action": "increase_thickness", "image": asset_path + "+.png"},
        {"rect": pygame.Rect(toolbar_x + 10, toolbar_y + 10 + button_spacing * 6, 40, 40), "action": "toggle_drag", "image": asset_path + "mouse.png"},
        {"rect": pygame.Rect(toolbar_x + 10, toolbar_y + 10 + button_spacing * 7, 40, 40), "action": "toggle_erase", "image": asset_path + "eraser.png"},
        # 其他按钮保持不变
        {"rect": pygame.Rect(600, 10, 40, 40), "action": "file", "image": asset_path + "file.png"},
        {"rect": pygame.Rect(660, 10, 40, 40), "action": "save", "image": asset_path + "save.png"},
        {"rect": pygame.Rect(screen_width - 80, screen_height - 50, 30, 50), "action": "clear_canvas", "image": asset_path + "clean.png"},
        {"rect": pygame.Rect(screen_width - 200, screen_height - 50, 30, 30), "action": "minus", "image": asset_path + "zoom-.png"},
        {"rect": pygame.Rect(screen_width - 140, screen_height - 50, 30, 30), "action": "plus", "image": asset_path + "zoom+.png"}
    ]

    # 加载和绘制按钮图标
    images = {}
    for button in buttons:
        if "image" in button:
            img = pygame.image.load(button["image"])
            images[button["action"]] = pygame.transform.scale(img, (button["rect"].width, button["rect"].height))

    for button in buttons:
        if "image" in button:
            surface.blit(images[button["action"]], button["rect"].topleft)

# 其他变量保持不变
current_color = (0, 0, 0)
current_thickness = 5
mode = "draw"
current_scale = 1.0
shadow_pos = (0, 0)
button_cooldown = 0.25
last_button_click_time = 0

def handle_button_click(pos, canvas, from_mouse=False):
    """处理按钮点击"""
    global current_color, current_thickness, mode, last_button_click_time, current_scale
    current_time = time.time()
    if current_time - last_button_click_time > button_cooldown:
        for button in buttons:
            if button["rect"].collidepoint(pos):
                action = button["action"]
                if action in ["file", "save", "clear_canvas"] and not from_mouse:
                    continue  # 这三个按钮只在鼠标点击时响应

                if action == "color":
                    current_color = button["value"]
                    mode = "draw"
                elif action == "increase_thickness":
                    current_thickness = min(current_thickness + 1, 20)
                elif action == "decrease_thickness":
                    current_thickness = max(current_thickness - 1, 1)
                elif action == "toggle_drag":
                    mode = "drag"
                elif action == "toggle_erase":
                    mode = "erase"
                elif action == "file":
                    new_file = file.load_file_with_dialog()
                    if new_file:
                        loaded_files.append({
                            "original_image": new_file["original_image"],
                            "image": new_file["image"],
                            "rect": new_file["rect"],
                            "scale": new_file["scale"]
                        })
                elif action == "clear_canvas":
                    canvas.fill((255, 255, 255))
                elif action == "minus":
                    current_scale = max(current_scale - 0.05, 0.5)
                elif action == "plus":
                    current_scale = min(current_scale + 0.05, 2.0)
                elif action == "save":
                    mode = "save"

                last_button_click_time = current_time
                break

loaded_files = []