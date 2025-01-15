import pygame
import time

asset_path = "assets/icons/"
# 按钮定义
buttons = [
    {"rect": pygame.Rect(20, 10, 30, 30), "color": (255, 0, 0), "action": "color", "value": (255, 0, 0)},  # 红色按钮
    {"rect": pygame.Rect(20, 50, 30, 30), "color": (0, 255, 0), "action": "color", "value": (0, 255, 0)},  # 绿色按钮
    {"rect": pygame.Rect(20, 90, 30, 30), "color": (0, 0, 255), "action": "color", "value": (0, 0, 255)},  # 蓝色按钮
    {"rect": pygame.Rect(20, 130, 30, 30), "color": (0, 0, 0), "action": "color", "value": (0, 0, 0)},  # 黑色按钮
    {"rect": pygame.Rect(10, 170, 30, 30), "color": (0, 0, 0), "action": "decrease_thickness", "image": asset_path + "minus.png"},  # 减小线条宽度
    {"rect": pygame.Rect(10, 210, 30, 30), "color": (255, 255, 255), "action": "increase_thickness", "image": asset_path + "plus.png"},  # 增大线条宽度
    {"rect": pygame.Rect(10, 250, 30, 30), "color": (255, 255, 255), "action": "toggle_drag", "image": asset_path + "drag.png"},  # 拖拽按钮
    {"rect": pygame.Rect(10, 290, 30, 30), "color": (255, 255, 255), "action": "toggle_erase", "image": asset_path + "eraser.png"},  # 擦除按钮
    {"rect": pygame.Rect(10, 330, 30, 30), "color": (255, 255, 255), "action": "toggle_draw", "image": asset_path + "pencil.png"},  # 绘制按钮
    {"rect": pygame.Rect(150, 10, 30, 30), "color": (255, 255, 255), "action": "file", "image": asset_path + "file.png"},  # 文件按钮
    {"rect": pygame.Rect(20, 550, 30, 50), "color": (255, 255, 255), "action": "clear_canvas", "image": asset_path + "trash.png"}  # 清空画布按钮
]

images ={}
for button in buttons:
    if "image" in button:
        img = pygame.image.load(button["image"])
        images[button["action"]] = pygame.transform.scale(img, (button["rect"].width, button["rect"].height))

def draw_buttons(surface):
    """绘制所有按钮"""
    for button in buttons:
        if "image" in button:
            surface.blit(images[button["action"]], button["rect"].topleft)
        else:
            pygame.draw.rect(surface, button["color"], button["rect"])


# 当前线条属性
current_color = (0, 0, 0)  # 默认黑色
current_thickness = 5  # 默认粗细为5
mode = "null"    # 默认模式为null


shadow_pos = (0, 0)
button_cooldown = 0.25   # 按钮冷却时间（秒）
last_button_click_time = 0  # 上次按钮点击时间

def handle_button_click(pos, canvas):
    """处理按钮点击"""
    global current_color, current_thickness, mode,last_button_click_time
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
                        mode = "file" # 切换到文件模式
                        print("文件选择")
                elif button["action"] == "clear_canvas":
                        canvas.fill((255, 255, 255)) # 用白色填充画布
                        prev_x, prev_y = None, None # 重置绘制时的起点坐标
                last_button_click_time = current_time  # 更新按钮点击时间
                