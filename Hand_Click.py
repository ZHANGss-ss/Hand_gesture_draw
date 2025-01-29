import pygame
import time
import file

asset_path = "assets/icons/"

# 按钮定义
def draw_buttons(surface, screen_width, screen_height):
    """绘制所有按钮"""
    global buttons, images
    buttons = [
        {"rect": pygame.Rect(20, 30, 40, 40), "color": (255, 0, 0), "action": "color", "value": (255, 0, 0)},
        {"rect": pygame.Rect(20, 90, 40, 40), "color": (0, 255, 0), "action": "color", "value": (0, 255, 0)},
        {"rect": pygame.Rect(20, 150, 40, 40), "color": (0, 0, 255), "action": "color", "value": (0, 0, 255)},
        {"rect": pygame.Rect(20, 210, 40, 40), "color": (0, 0, 0), "action": "color", "value": (0, 0, 0)},
        {"rect": pygame.Rect(10, 270, 40, 40), "color": (0, 0, 0), "action": "decrease_thickness", "image": asset_path + "minus.ico"},
        {"rect": pygame.Rect(10, 350, 40, 40), "color": (255, 255, 255), "action": "increase_thickness", "image": asset_path + "plus.ico"},
        {"rect": pygame.Rect(10, 410, 40, 40), "color": (255, 255, 255), "action": "toggle_drag", "image": asset_path + "drag.ico"},
        {"rect": pygame.Rect(10, 470, 40, 40), "color": (255, 255, 255), "action": "toggle_erase", "image": asset_path + "eraser.ico"},
        {"rect": pygame.Rect(10, 530, 40, 40), "color": (255, 255, 255), "action": "toggle_draw", "image": asset_path + "pencil.ico"},
        {"rect": pygame.Rect(600, 10, 40, 40), "color": (255, 255, 255), "action": "file", "image": asset_path + "file.ico"},
        {"rect": pygame.Rect(660, 10, 40, 40), "color": (255, 255, 255), "action": "save", "image": asset_path + "save.ico"},
        {"rect": pygame.Rect(screen_width - 80, screen_height - 50, 30, 50), "color": (255, 255, 255), "action": "clear_canvas", "image": asset_path + "trash.ico"},
        {"rect": pygame.Rect(screen_width - 200, screen_height - 50, 30, 30), "color": (255, 0, 0), "action": "minus", "image": asset_path + "zoom_minus.ico"},
        {"rect": pygame.Rect(screen_width - 140, screen_height - 50, 30, 30), "color": (255, 0, 0), "action": "plus", "image": asset_path + "zoom_plus.ico"}
    ]

    images = {}
    for button in buttons:
        if "image" in button:
            img = pygame.image.load(button["image"])
            images[button["action"]] = pygame.transform.scale(img, (button["rect"].width, button["rect"].height))

    for button in buttons:
        if "image" in button:
            surface.blit(images[button["action"]], button["rect"].topleft)
        else:
            pygame.draw.rect(surface, button["color"], button["rect"])

current_color = (0, 0, 0)
current_thickness = 5
mode = "drag"
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
                elif action == "increase_thickness":
                    current_thickness = min(current_thickness + 1, 20)
                elif action == "decrease_thickness":
                    current_thickness = max(current_thickness - 1, 1)
                elif action == "toggle_drag":
                    mode = "drag"
                elif action == "toggle_erase":
                    mode = "erase"
                elif action == "toggle_draw":
                    mode = "draw"
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