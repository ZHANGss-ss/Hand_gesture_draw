import pygame
import adjust_canvas_size

def draw_shadow(surface, color, x, y, size):
    """绘制实时阴影"""
    pygame.draw.circle(surface, color, (x, y), size)


def draw_brush(surface, x, y, thickness, color):
    """在指定位置绘制笔刷效果"""
    pygame.draw.circle(surface, color, (x, y), thickness // 2)  # 使用圆形来模拟画笔效果

