import pygame

def extend_canvas(x, y, EXTEND_MARGIN):
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
        new_background_layer.fill((255, 255, 255)) # 初始化为白色
        new_background_layer.blit(background_layer, (-new_canvas_offset_x + canvas_offset_x, -new_canvas_offset_y + canvas_offset_y))
        background_layer = new_background_layer

        new_drawing_layer = pygame.Surface((new_canvas_width, new_canvas_height), pygame.SRCALPHA)
        new_drawing_layer.blit(drawing_layer, (-new_canvas_offset_x + canvas_offset_x, -new_canvas_offset_y + canvas_offset_y))
        drawing_layer = new_drawing_layer

        canvas_width = new_canvas_width
        canvas_height = new_canvas_height
        canvas_offset_x = new_canvas_offset_x
        canvas_offset_y = new_canvas_offset_y