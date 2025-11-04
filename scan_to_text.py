import pytesseract
from PIL import Image, ImageOps
import io
import cv2
import numpy as np

def scan_to_text(image_bytes):
    try:
        # Đọc ảnh từ bytes
        image = Image.open(io.BytesIO(image_bytes))

        # Lật ảnh ngang (mirror)
        image = ImageOps.mirror(image)

        # Chuyển sang OpenCV để xử lý
        img_cv = np.array(image)
        img_gray = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)

        # Làm rõ chữ: threshold + blur nhẹ
        img_gray = cv2.GaussianBlur(img_gray, (3, 3), 0)
        _, img_thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # OCR
        text = pytesseract.image_to_string(img_thresh, lang='vie+eng')

        if text.strip() == "":
            return {"success": False, "message": "Không phát hiện được chữ. Hãy thử chụp gần hơn hoặc tăng sáng."}

        return {"success": True, "text": text}

    except Exception as e:
        return {"success": False, "message": f"Lỗi xử lý ảnh: {str(e)}"}
