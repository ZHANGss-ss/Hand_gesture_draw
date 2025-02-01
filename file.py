# file.py
import os
import pygame
from PyPDF2 import PdfReader
from PIL import Image
import fitz  # PyMuPDF

def load_image(file_path):
    """加载图片文件"""
    return pygame.image.load(file_path)

def convert_pdf_to_image(pdf_path):
    """将PDF文件转换为图片"""
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)  # 读取第一页
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img.save("temp.png")
    return pygame.image.load("temp.png")

def load_file_with_dialog():
    """打开文件对话框选择文件并加载"""
    from tkinter import Tk, filedialog
    Tk().withdraw()  # 隐藏主窗口
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg"), ("PDF files", "*.pdf"),("所有文件", "*.*")])
    if file_path:
        if file_path.lower().endswith('.pdf'):
            original_image = convert_pdf_to_image(file_path)
        else:
            original_image = load_image(file_path)
        scaled_image = pygame.transform.scale(original_image, (100, 100))  # 初始缩放
        return {
            "original_image": original_image,
            "image": scaled_image,
            "rect": scaled_image.get_rect(topleft=(100, 100)),  # 初始位置
            "scale": 1.0
        }
    return None