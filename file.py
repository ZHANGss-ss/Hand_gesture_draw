import os
import pygame

def get_files_in_directory(directory, extensions):
    """
    获取指定目录下指定扩展名的文件列表。
    """
    files = [f for f in os.listdir(directory) if f.lower().endswith(extensions)]
    print("文件列表：", files)  # 调试打印
    return files


def draw_file_list(screen, file_list, x, y, selected_index=-1):
    """
    绘制文件列表。
    """
    font = pygame.font.SysFont(None, 24)
    for i, file_name in enumerate(file_list):
        color = (200, 200, 200) if i == selected_index else (255, 255, 255)  # 高亮选中项
        text_surface = font.render(file_name, True, (0, 0, 0), color)
        text_rect = text_surface.get_rect(topleft=(x, y + i * 30))
        pygame.draw.rect(screen, color, text_rect)  # 背景色
        screen.blit(text_surface, text_rect)


def add_file_to_canvas(file_path, canvas, x, y):
    """
    将文件内容添加到画布中。
    - 对于图片文件(png, jpg, gif)，直接加载为图像。
    - 对于 PDF 等非图像文件，可以显示文件名或其他占位内容。
    """
    if file_path.lower().endswith((".png", ".jpg", ".gif")):
        try:
            img = pygame.image.load(file_path)
            canvas.blit(img, (x, y))
        except Exception as e:
            print(f"无法加载文件 {file_path}: {e}")
    else:
        print(f"文件 {file_path} 不支持直接加载到画布。")
