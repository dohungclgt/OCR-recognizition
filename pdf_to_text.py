from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import os
from config import pytesseract

def pdf_to_text(pdf_path):
    """
    Chuyển đổi PDF sang text (dùng OCR cho cả file scan)
    """
    try:
        # Đường dẫn Poppler (bạn thay đúng đường dẫn bạn đã giải nén)
        poppler_path = r"C:\Program Files\poppler-25.07.0\Library\bin"

        temp_dir = "temp_pdf_images"
        os.makedirs(temp_dir, exist_ok=True)

        # ✅ Thêm poppler_path vào hàm convert_from_path
        pages = convert_from_path(pdf_path, dpi=300, fmt="png", output_folder=temp_dir, poppler_path=poppler_path)

        all_text = ""
        for i, page in enumerate(pages):
            image_path = os.path.join(temp_dir, f"page_{i+1}.png")
            page.save(image_path, "PNG")

            text = pytesseract.image_to_string(Image.open(image_path), lang="vie+eng")
            all_text += f"\n\n--- Trang {i+1} ---\n{text}"

        # Dọn dẹp file tạm
        for f in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, f))
        os.rmdir(temp_dir)

        if not all_text.strip():
            return {"success": False, "message": "Không phát hiện được chữ trong PDF."}
        return {"success": True, "text": all_text}

    except Exception as e:
        return {"success": False, "message": f"Lỗi xử lý PDF: {e}"}
