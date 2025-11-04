from PIL import Image
import pytesseract
import cv2
import numpy as np
from config import pytesseract

def preprocess_image(image_path):
    """Tiền xử lý ảnh để tăng độ chính xác OCR"""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)        # chuyển sang grayscale
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]  # lọc nhiễu
    gray = cv2.medianBlur(gray, 3)
    processed_path = "temp_processed.png"
    cv2.imwrite(processed_path, gray)
    return processed_path

def image_to_text(image_path):
    """Chuyển ảnh sang văn bản"""
    try:
        processed = preprocess_image(image_path)
        text = pytesseract.image_to_string(Image.open(image_path), lang="vie+eng")
        if not text.strip():
            return {"success": False, "message": "Không phát hiện được chữ trong ảnh."}
        return {"success": True, "text": text}
    except Exception as e:
        return {"success": False, "message": f"Lỗi xử lý ảnh: {e}"}
