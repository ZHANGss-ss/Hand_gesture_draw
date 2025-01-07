import pygame
import time

# 按钮定义
buttons = [
    {"rect": pygame.Rect(10, 10, 50, 30), "color": (255, 0, 0), "action": "color", "value": (255, 0, 0)},  # 红色按钮
    {"rect": pygame.Rect(70, 10, 50, 30), "color": (0, 255, 0), "action": "color", "value": (0, 255, 0)},  # 绿色按钮
    {"rect": pygame.Rect(130, 10, 50, 30), "color": (0, 0, 255), "action": "color", "value": (0, 0, 255)},  # 蓝色按钮
    {"rect": pygame.Rect(190, 10, 50, 30), "color": (0, 0, 0), "action": "decrease_thickness"},  # 减小线条宽度
    {"rect": pygame.Rect(250, 10, 50, 30), "color": (128, 128, 128), "action": "increase_thickness"},  # 增大线条宽度
    {"rect": pygame.Rect(310, 10, 70, 30), "color": (200, 200, 200), "action": "toggle_drag"},  # 拖拽按钮
    {"rect": pygame.Rect(390, 10, 70, 30), "color": (100, 100, 100), "action": "toggle_erase"},  # 擦除按钮
    {"rect": pygame.Rect(410, 10, 70, 30), "color": (0, 150, 100), "action": "toggle_draw"},  # 擦除按钮
]

def draw_buttons(surface):
    """绘制所有按钮"""
    for button in buttons:
        pygame.draw.rect(surface, button["color"], button["rect"])

# 当前线条属性
current_color = (0, 0, 255)  # 默认蓝色
current_thickness = 5  # 默认粗细为5
mode = "null"    # 默认模式为null


shadow_pos = (0, 0)
button_cooldown = 0.5   # 按钮冷却时间（秒）
last_button_click_time = 0  # 上次按钮点击时间

def handle_button_click(pos):
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
                elif button["action"] == "toggle_draw":
                        mode = "draw"  # 切换到绘制模式
                last_button_click_time = current_time  # 更新按钮点击时间
                