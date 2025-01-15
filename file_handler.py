import pygame
import os
from tkinter import filedialog
import tkinter as tk
import fitz  # PyMuPDF库用于处理PDF
from PIL import Image
import numpy as np

class ScaleButton:
    def __init__(self, pos, is_plus=True, size=(30, 30)):
        self.rect = pygame.Rect(pos, size)
        self.is_plus = is_plus
        self.color = (100, 100, 100)
        self.hover_color = (150, 150, 150)
        self.is_hover = False
        
    def draw(self, surface):
        """绘制缩放按钮"""
        color = self.hover_color if self.is_hover else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        
        # 绘制+或-符号
        text_color = (255, 255, 255)
        font = pygame.font.SysFont(None, 30)
        text = font.render('+' if self.is_plus else '-', True, text_color)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

class FileObject:
    def __init__(self, surface, pos=(0, 0), scale=1.0):
        self.surface = surface
        self.original_surface = surface.copy()
        self.draw_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)  # 新增绘画层
        self.rect = surface.get_rect()
        self.rect.topleft = pos
        self.scale = scale
        self.dragging = False
        self.drag_offset = (0, 0)
        self.selected = False
        
        # 缩放按钮
        self.scale_buttons = {
            'plus': ScaleButton((0, 0), True),
            'minus': ScaleButton((0, 0), False)
        }
        self.update_button_positions()
        self.scaling = None  # 记录当前是否在缩放('+' or '-' or None)

    def update_button_positions(self):
        """更新缩放按钮的位置"""
        self.scale_buttons['plus'].rect.topleft = (self.rect.right + 10, self.rect.top)
        self.scale_buttons['minus'].rect.topleft = (self.rect.right + 10, self.rect.top + 40)

    def draw_on_surface(self, pos, color, thickness):
        """在文件表面绘画"""
        # 转换全局坐标到文件局部坐标
        local_x = (pos[0] - self.rect.x) / self.scale
        local_y = (pos[1] - self.rect.y) / self.scale
        
        if 0 <= local_x <= self.draw_surface.get_width() and \
           0 <= local_y <= self.draw_surface.get_height():
            pygame.draw.circle(self.draw_surface, color, (int(local_x), int(local_y)), thickness)
            return True
        return False

    def update_scale(self, increase=True):
        """更新对象的缩放比例"""
        scale_factor = 1.1 if increase else 0.9
        self.scale *= scale_factor
        
        # 缩放原始表面和绘画层
        new_size = (int(self.original_surface.get_width() * self.scale),
                   int(self.original_surface.get_height() * self.scale))
        self.surface = pygame.transform.scale(self.original_surface, new_size)
        scaled_draw = pygame.transform.scale(self.draw_surface, new_size)
        
        old_center = self.rect.center
        self.rect = self.surface.get_rect()
        self.rect.center = old_center
        self.update_button_positions()

    def start_drag(self, pos):
        """开始拖拽"""
        if self.rect.collidepoint(pos):
            self.dragging = True
            self.selected = True
            self.drag_offset = (pos[0] - self.rect.x, pos[1] - self.rect.y)
            return True
        return False

    def update_position(self, pos):
        """更新位置"""
        if self.dragging:
            self.rect.x = pos[0] - self.drag_offset[0]
            self.rect.y = pos[1] - self.drag_offset[1]
            self.update_button_positions()

    def stop_drag(self):
        """停止拖拽"""
        self.dragging = False

    def check_scale_buttons(self, pos):
        """检查是否在缩放按钮上"""
        if not self.selected:
            return False
            
        for button_name, button in self.scale_buttons.items():
            button.is_hover = button.rect.collidepoint(pos)
            if button.is_hover:
                self.scaling = '+' if button_name == 'plus' else '-'
                return True
        self.scaling = None
        return False

    def apply_scaling(self):
        """应用缩放"""
        if self.scaling == '+':
            self.update_scale(True)
        elif self.scaling == '-':
            self.update_scale(False)

class FileHandler:
    def __init__(self):
        self.file_objects = []
        self.selected_object = None
        self.supported_formats = [
            ('All Files', '*.png;*.jpg;*.jpeg;*.pdf'),
            ('Images', '*.png;*.jpg;*.jpeg'),
            ('PDF', '*.pdf')
        ]

    def load_file(self):
        """打开文件选择对话框并加载文件"""
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        file_path = filedialog.askopenfilename(
            title='选择文件',
            filetypes=self.supported_formats
        )
        
        if file_path:
            if file_path.lower().endswith('.pdf'):
                return self._load_pdf(file_path)
            else:
                return self._load_image(file_path)
        return None

    def _load_image(self, file_path):
        """加载图片文件"""
        try:
            image = pygame.image.load(file_path)
            return FileObject(image)
        except Exception as e:
            print(f"Error loading image: {e}")
            return None

    def _load_pdf(self, file_path):
        """加载PDF文件的第一页"""
        try:
            doc = fitz.open(file_path)
            page = doc[0]
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            mode = img.mode
            size = img.size
            data = img.tobytes()
            py_surface = pygame.image.fromstring(data, size, mode)
            return FileObject(py_surface)
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return None

    def add_file_object(self, file_object, pos=(100, 100)):
        """添加新的文件对象到列表"""
        if file_object:
            file_object.rect.topleft = pos
            file_object.update_button_positions()
            self.file_objects.append(file_object)

    def handle_event(self, pos, is_dragging):
        """处理文件对象的事件"""
        if is_dragging:
            if not self.selected_object:
                # 取消之前选中的对象
                for obj in self.file_objects:
                    obj.selected = False
                
                # 检查是否选中新对象
                for obj in reversed(self.file_objects):
                    if obj.start_drag(pos):
                        self.selected_object = obj
                        break
            elif self.selected_object:
                # 检查是否在缩放按钮上
                if self.selected_object.check_scale_buttons(pos):
                    self.selected_object.apply_scaling()
                elif self.selected_object.dragging:
                    self.selected_object.update_position(pos)
        else:
            # 停止拖拽和缩放
            if self.selected_object:
                self.selected_object.stop_drag()
                self.selected_object.scaling = None
                self.selected_object = None

    def draw(self, surface):
        """绘制所有文件对象和控制按钮"""
        for obj in self.file_objects:
            # 绘制原始图像
            surface.blit(obj.surface, obj.rect)
            # 绘制绘画层
            scaled_draw = pygame.transform.scale(obj.draw_surface, obj.rect.size)
            surface.blit(scaled_draw, obj.rect)
            
            if obj.selected:
                # 绘制选中框
                pygame.draw.rect(surface, (0, 255, 0), obj.rect, 2)
                # 绘制缩放按钮
                for button in obj.scale_buttons.values():
                    button.draw(surface)

    def draw_on_selected(self, pos, color, thickness):
        """在选中的文件上绘画"""
        if self.selected_object:
            return self.selected_object.draw_on_surface(pos, color, thickness)
        return False
