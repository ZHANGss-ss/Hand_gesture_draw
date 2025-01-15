import tkinter as tk
from tkinter import filedialog
import pygame

def export_canvas_with_dialog(canvas):
    """
    使用文件选择对话框导出画布。
    :param canvas: 当前画布 (pygame.Surface)
    """
    # 初始化 Tkinter 并隐藏主窗口
    root = tk.Tk()
    root.withdraw()

    # 打开保存文件对话框
    filetypes = [("PNG 文件", "*.png"), ("JPEG 文件", "*.jpg"), ("所有文件", "*.*")]
    filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=filetypes, title="保存画布为")
    
    if filename:  # 用户选择了文件名
        try:
            pygame.image.save(canvas, filename)
            print(f"画布已成功导出为文件：{filename}")
        except Exception as e:
            print(f"导出画布失败：{e}")
    else:
        print("取消保存操作")

def load_canvas_with_dialog(canvas):
    """
    使用文件选择对话框导入图像到画布，并根据需要扩展画布。
    :param canvas: 当前画布 (pygame.Surface)
    """
    # 初始化 Tkinter 并隐藏主窗口
    root = tk.Tk()
    root.withdraw()

    # 打开文件选择对话框
    filetypes = [("图像文件", "*.png *.jpg *.jpeg *.bmp *.gif"), ("所有文件", "*.*")]
    file_path = filedialog.askopenfilename(filetypes=filetypes, title="选择要导入的图像")
    
    if file_path:  # 用户选择了文件
        try:
            # 加载图像
            imported_image = pygame.image.load(file_path)
            image_width, image_height = imported_image.get_size()
            
            # 获取画布当前大小
            canvas_width, canvas_height = canvas.get_size()
            
            # 检查图像大小是否超过画布大小
            new_canvas_width = max(canvas_width, image_width)
            new_canvas_height = max(canvas_height, image_height)
            
            if new_canvas_width > canvas_width or new_canvas_height > canvas_height:
                # 创建新的画布并复制旧画布内容
                new_canvas = pygame.Surface((new_canvas_width, new_canvas_height))
                new_canvas.fill((255, 255, 255))  # 白色背景
                new_canvas.blit(canvas, (0, 0))  # 将旧画布内容复制到新画布
                canvas = new_canvas
            
            # 将图像绘制到画布，默认放置在 (50, 50)
            canvas.blit(imported_image, (50, 50))
            print(f"图像已成功导入到画布：{file_path}")
        except Exception as e:
            print(f"导入图像失败：{e}")
    else:
        print("未选择文件。")
    
    return canvas  # 返回可能被扩展的画布
