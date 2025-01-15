import pygame
import time
import os

# 定义颜色
COLORS = [
    (255, 0, 0),    # 红色
    (0, 0, 0),      # 黑色
    (0, 0, 255),    # 蓝色
    (255, 255, 0),  # 黄色
]

# 定义画笔粗细
BRUSH_SIZES = [2, 4, 6, 8, 10]

# 图标大小
ICON_SIZE = (40, 40)

def load_icon(icon_path):
    """加载图标文件并调整大小"""
    try:
        icon = pygame.image.load(icon_path)
        return pygame.transform.scale(icon, ICON_SIZE)
    except Exception as e:
        print(f"Error loading icon {icon_path}: {e}")
        # 创建默认图标作为备用
        default_icon = pygame.Surface(ICON_SIZE, pygame.SRCALPHA)
        pygame.draw.rect(default_icon, (100, 100, 100), default_icon.get_rect(), 2)
        return default_icon

# 加载图标
mouse_icon = load_icon("./ico/mouse.ico")
eraser_icon = load_icon("./ico/eraser.ico")

# 工具按钮
TOOL_BUTTONS = {
    "mouse": {
        "rect": pygame.Rect(280, 10, 40, 40),
        "icon": mouse_icon,
        "action": "mouse"
    },
    "eraser": {
        "rect": pygame.Rect(330, 10, 40, 40),
        "icon": eraser_icon,
        "action": "eraser"
    }
}

# 创建颜色选择按钮
def create_color_buttons():
    buttons = []
    x = 10
    for color in COLORS:
        buttons.append({
            "rect": pygame.Rect(x, 10, 40, 40),
            "color": color,
            "action": "color",
            "value": color
        })
        x += 50
    return buttons

# 创建画笔粗细选择按钮
def create_size_buttons():
    buttons = []
    x = 10
    y = 60
    for size in BRUSH_SIZES:
        buttons.append({
            "rect": pygame.Rect(x, y, 40, 40),
            "size": size,
            "action": "size",
            "value": size
        })
        x += 50
    return buttons

# 合并所有按钮
buttons = create_color_buttons() + create_size_buttons()

def draw_buttons(surface):
    """绘制所有按钮"""
    # 绘制颜色按钮
    for button in buttons:
        if button["action"] == "color":
            pygame.draw.rect(surface, button["color"], button["rect"])
        elif button["action"] == "size":
            center = button["rect"].center
            pygame.draw.circle(surface, (0, 0, 0), center, button["size"])

    # 绘制工具图标
    for tool in TOOL_BUTTONS.values():
        surface.blit(tool["icon"], tool["rect"])

# 当前属性
current_color = (0, 0, 0)  # 默认黑色
current_thickness = 5  # 默认粗细
current_tool = None  # 当前选中的工具
shadow_pos = (0, 0)

def check_button_hover(pos):
    """检查手指是否悬停在按钮上"""
    global current_color, current_thickness, current_tool
    
    # 检查工具按钮
    for tool_name, tool in TOOL_BUTTONS.items():
        if tool["rect"].collidepoint(pos):
            current_tool = tool_name
            return True

    # 检查其他按钮
    for button in buttons:
        if button["rect"].collidepoint(pos):
            current_tool = None
            if button["action"] == "color":
                current_color = button["value"]
            elif button["action"] == "size":
                current_thickness = button["value"]
            return True
            
    return False

def draw_shadow(surface, pos):
    """绘制手指追踪点"""
    x, y = pos
    if current_tool == "mouse":
        # 绘制鼠标图标
        surface.blit(mouse_icon, (x - ICON_SIZE[0]//2, y - ICON_SIZE[1]//2))
    elif current_tool == "eraser":
        # 绘制橡皮擦图标
        surface.blit(eraser_icon, (x - ICON_SIZE[0]//2, y - ICON_SIZE[1]//2))
    else:
        # 绘制当前颜色和大小的圆圈
        pygame.draw.circle(surface, current_color, (x, y), current_thickness)

def is_dragging():
    """检查是否处于拖拽模式"""
    return current_tool == "mouse"

def is_erasing():
    """检查是否处于擦除模式"""
    return current_tool == "eraser"
