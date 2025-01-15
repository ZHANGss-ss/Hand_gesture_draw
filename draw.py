import pygame


def draw_shadow(surface, color, x, y, size):
    """绘制实时阴影"""
    pygame.draw.circle(surface, color, (x, y), size)


def draw_brush(surface, x, y, thickness, color):
    """在指定位置绘制笔刷效果"""
    pygame.draw.circle(surface, color, (x, y), thickness // 2)  # 使用圆形来模拟画笔效果


def draw_canvas_border(screen, canvas, canvas_offset_x, canvas_offset_y):
    """绘制画布边界"""
    canvas_width, canvas_height = canvas.get_size()
    
    # 计算画布边界的矩形位置
    border_rect = pygame.Rect(
        canvas_offset_x, 
        canvas_offset_y, 
        canvas_width, 
        canvas_height
    )
    
    # 绘制边界线（红色，宽度为 2 像素）
    pygame.draw.rect(screen, (255, 0, 0), border_rect, 2)


def ensure_canvas_size(canvas, x, y, padding=100):
    """
    确保画布大小足够容纳 (x, y) 坐标。
    如果坐标超出画布范围，则动态扩展画布。
    """
    canvas_width, canvas_height = canvas.get_size()

    # 计算需要的画布大小
    new_width = max(canvas_width, x + padding)
    new_height = max(canvas_height, y + padding)

    # 检查是否需要向左上扩展
    if x - padding < 0:
        x0 = abs(x - padding)
        if x0 > 2:
            x0 = 2
        new_width = new_width + x0
        offset_x = x0
    else:
        offset_x = 0 #非左

    if y - padding < 0:
        y0 = abs(y - padding)
        if y0 > 2:
            y0 = 2
        new_height = new_height + y0
        offset_y = y0
    else:
        offset_y = 0 #非上

    if new_width > canvas_width or new_height > canvas_height:
        # 创建新的画布并扩展
        new_canvas = pygame.Surface((new_width, new_height))
        new_canvas.fill((255, 255, 255))  # 填充白色背景
        new_canvas.blit(canvas, (offset_x, offset_y))  # 将旧画布内容复制到新画布
        #目前只能做到向右下实时扩展，左上的边界框在画布中不会动态扩展（而是采用画布内容偏移)
        print("画布大小扩展到", new_width, new_height)
        return new_canvas

    return canvas


