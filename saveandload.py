import tkinter as tk
from tkinter import filedialog
import pygame

def export_canvas_with_dialog(
    canvas,image_layer,
    loaded_files,
    canvas_offset_x,
    canvas_offset_y,
    current_scale
):
    """
    导出画布时动态合并所有图层和导入的图片。
    """

    # 初始化 Tkinter
    root = tk.Tk()
    root.withdraw()

    # 打开保存对话框
    filetypes = [("PNG 文件", "*.png"), ("JPEG 文件", "*.jpg"), ("所有文件", "*.*")]
    filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=filetypes, title="保存画布为")

    if not filename:
        print("取消保存操作")
        return

    try:
        # 创建临时合并层
        merged_surface = pygame.Surface(canvas.get_size(), pygame.SRCALPHA)
        merged_surface.fill((255, 255, 255))  # 白色背景

        # 合并画布
        merged_surface.blit(canvas, (0, 0))

        # 合并导入的图片
        for file in loaded_files:
            # 计算图片在画布上的实际位置（反向转换屏幕坐标）
            screen_x, screen_y = file["rect"].topleft
            canvas_x = (screen_x - canvas_offset_x) / current_scale
            canvas_y = (screen_y - canvas_offset_y) / current_scale

            # 缩放图片到原始尺寸（因为加载时可能已经缩放）
            original_width = file["original_image"].get_width()
            original_height = file["original_image"].get_height()
            scaled_image = pygame.transform.scale(
                file["original_image"],
                (int(original_width * file["scale"]), int(original_height * file["scale"]))
            )

            # 将图片绘制到合并层
            merged_surface.blit(scaled_image, (int(canvas_x), int(canvas_y)))

        # 最后合并绘制图层
        merged_surface.blit(image_layer, (0, 0))
        # 保存合并后的图像
        pygame.image.save(merged_surface, filename)
        print(f"画布已成功导出为文件：{filename}")

    except Exception as e:
        print(f"导出失败：{e}")

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
