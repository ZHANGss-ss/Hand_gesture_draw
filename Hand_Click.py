# Hand_Click.py
import pygame
import time
import file

asset_path = "assets/icons/"

# 按钮定义
def draw_buttons(surface, screen_width, screen_height):
    """绘制所有按钮"""
    global buttons, images
    buttons = [
        {"rect": pygame.Rect(20, 30, 40, 40), "color": (255, 0, 0), "action": "color", "value": (255, 0, 0)},  # 红色按钮
        {"rect": pygame.Rect(20, 90, 40, 40), "color": (0, 255, 0), "action": "color", "value": (0, 255, 0)},  # 绿色按钮
        {"rect": pygame.Rect(20, 150, 40, 40), "color": (0, 0, 255), "action": "color", "value": (0, 0, 255)},  # 蓝色按钮
        {"rect": pygame.Rect(20, 210, 40, 40), "color": (0, 0, 0), "action": "color", "value": (0, 0, 0)},  # 黑色按钮
        {"rect": pygame.Rect(10, 270, 40, 40), "color": (0, 0, 0), "action": "decrease_thickness", "image": asset_path + "minus.ico"},  # 减小线条宽度
        {"rect": pygame.Rect(10, 350, 40, 40), "color": (255, 255, 255), "action": "increase_thickness", "image": asset_path + "plus.ico"},  # 增大线条宽度
        {"rect": pygame.Rect(10, 410, 40, 40), "color": (255, 255, 255), "action": "toggle_drag", "image": asset_path + "drag.ico"},  # 拖拽按钮
        {"rect": pygame.Rect(10, 470, 40, 40), "color": (255, 255, 255), "action": "toggle_erase", "image": asset_path + "eraser.ico"},  # 擦除按钮
        {"rect": pygame.Rect(10, 530, 40, 40), "color": (255, 255, 255), "action": "toggle_draw", "image": asset_path + "pencil.ico"},  # 绘制按钮
        {"rect": pygame.Rect(600, 10, 40, 40), "color": (255, 255, 255), "action": "file", "image": asset_path + "file.ico"},  # 文件导入按钮
        {"rect": pygame.Rect(660, 10, 40, 40), "color": (255, 255, 255), "action": "save", "image": asset_path + "save.ico"},  # 文件保存按钮
        {"rect": pygame.Rect(screen_width - 80, screen_height - 50, 30, 50), "color": (255, 255, 255), "action": "clear_canvas", "image": asset_path + "trash.ico"},  # 清空画布按钮
        {"rect": pygame.Rect(screen_width - 200, screen_height - 50, 30, 30), "color": (255, 0, 0), "action": "minus", "image": asset_path + "zoom_minus.ico"},  # 全局缩小按钮
        {"rect": pygame.Rect(screen_width - 140, screen_height - 50, 30, 30), "color": (255, 0, 0), "action": "plus", "image": asset_path + "zoom_plus.ico"}  # 全局放大按钮
    ]

    images = {}
    for button in buttons:
        if "image" in button:
            img = pygame.image.load(button["image"])
            images[button["action"]] = pygame.transform.scale(img, (button["rect"].width, button["rect"].height))

    """绘制所有按钮"""
    for button in buttons:
        if "image" in button:
            surface.blit(images[button["action"]], button["rect"].topleft)
        else:
            pygame.draw.rect(surface, button["color"], button["rect"])

# 当前线条属性
current_color = (0, 0, 0)  # 默认黑色
current_thickness = 5  # 默认粗细为5
mode = "null"  # 默认模式为null

# 缩放
current_scale = 1.0

# 按钮点击处理
shadow_pos = (0, 0)
button_cooldown = 0.25  # 按钮冷却时间（秒）
last_button_click_time = 0  # 上次按钮点击时间

def handle_button_click(pos, canvas, layer):
    """处理按钮点击"""
    global current_color, current_thickness, mode, last_button_click_time, current_scale
    current_time = time.time()
    if current_time - last_button_click_time > button_cooldown:  # 按钮冷却时间
        for button in buttons:
            if button["rect"].collidepoint(pos):
                if button["action"] == "color":
                    current_color = button["value"]  # 更新颜色
                elif button["action"] == "increase_thickness":
                    current_thickness += 1  # 增大线条宽度
                    if current_thickness > 20:  # 设置最大宽度限制
                        current_thickness = 20
                elif button["action"] == "decrease_thickness":
                    current_thickness -= 1  # 减小线条宽度
                    if current_thickness < 1:  # 设置最小宽度限制
                        current_thickness = 1
                elif button["action"] == "toggle_drag":
                    mode = "drag"  # 切换到拖拽模式
                    print("切换到拖拽模式")
                elif button["action"] == "toggle_erase":
                    mode = "erase"  # 切换到擦除模式
                    print("切换到擦除模式")
                elif button["action"] == "toggle_draw":
                    mode = "draw"  # 切换到绘制模式
                    print("切换到绘制模式")
                elif button["action"] == "file":
                    new_file = file.load_file_with_dialog()
                    if new_file:
                        # 将新文件添加到全局变量中
                        loaded_files.append({
                            "original_image": new_file["original_image"],
                            "image": new_file["image"],
                            "rect": new_file["rect"],
                            "scale": new_file["scale"]
                        })
                    print("文件选择")
                elif button["action"] == "clear_canvas":
                    layer.fill((0, 0, 0, 0))  # 用白色填充画布
                    prev_x, prev_y = None, None  # 重置绘制时的起点坐标
                elif button["action"] == "minus":
                    current_scale = max(current_scale - 0.05, 0.5)
                    print("缩小画布")
                elif button["action"] == "plus":
                    current_scale = min(current_scale + 0.05, 2.0)
                    print("放大画布")
                elif button["action"] == "save":
                    mode = "save"
                last_button_click_time = current_time  # 更新按钮点击时间

# 导入的文件列表
loaded_files = []