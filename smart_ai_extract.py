"""
smart_ai_extract.py — Gemini AI bilingual (Vietnamese / English)
----------------------------------------------------------
Phân tích tài liệu (ảnh hoặc PDF) và trả kết quả dễ đọc
bằng ngôn ngữ mà người dùng chọn.
"""

import tempfile
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
import os

# ⚙️ Load API key từ .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "your key here"))


def analyze_document_ai(file_data: bytes, file_type: str = "image", language: str = "Vietnamese"):
    """
    Phân tích tài liệu bằng Google Gemini AI.
    language: 'Vietnamese' hoặc 'English'
    """
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")

        # Chọn prompt theo ngôn ngữ
        if language.lower().startswith("vi"):
            prompt = """
            Bạn là trợ lý chuyên đọc hiểu tài liệu hành chính Việt Nam.
            Hãy đọc ảnh hoặc PDF này (bằng tốt nghiệp, chứng chỉ, hóa đơn, CMND...).
            Trích xuất thông tin chính và trình bày bằng tiếng Việt, định dạng rõ ràng như sau:

            =====================================
            🧾 Thông tin tài liệu:
            • Loại tài liệu: ...
            • Họ và tên: ...
            • Ngày sinh: ...
            • Nơi sinh: ...
            • Giới tính: ...
            • Cấp bởi: ...
            • Ngày cấp: ...
            • Số hiệu / Mã chứng nhận: ...

            📄 Tóm tắt nội dung:
            [viết đoạn ngắn tiếng Việt mô tả tài liệu]

            Không trả về JSON, không giải thích thêm.
            """

        else:  # English mode
            prompt = """
            You are a professional document understanding assistant.
            Read this image or PDF (such as a certificate, ID, invoice, or diploma).
            Extract the key information and present it in English, clearly formatted as follows:

            =====================================
            🧾 Document Information:
            • Document Type: ...
            • Full Name: ...
            • Date of Birth: ...
            • Place of Birth: ...
            • Gender: ...
            • Issued by: ...
            • Issue Date: ...
            • Certificate / Reference No.: ...

            📄 Summary:
            [Write a short English paragraph summarizing the document content.]

            Do not return JSON or explanations, only formatted text.
            """

        # 📸 Nếu là ảnh
        if file_type == "image":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(file_data)
                tmp_path = tmp.name
            img = Image.open(tmp_path)
            response = model.generate_content([prompt, img])

        # 📄 Nếu là PDF
        elif file_type == "pdf":
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(file_data)
                tmp_path = tmp.name
            response = model.generate_content([
                prompt,
                {"mime_type": "application/pdf", "data": open(tmp_path, "rb").read()}
            ])
        else:
            return {"success": False, "message": f"Không hỗ trợ loại file: {file_type}"}

        result_text = response.text.strip()

        if not result_text:
            return {"success": False, "message": "Không nhận được phản hồi từ Gemini AI."}

        return {"success": True, "text": result_text}

    except Exception as e:
        return {"success": False, "message": f"Lỗi khi xử lý AI: {e}"}


# Test thủ công
if __name__ == "__main__":
    print("🧠 Test smart_ai_extract.py (bilingual)")
    with open("test_image.png", "rb") as f:
        res = analyze_document_ai(f.read(), file_type="image", language="Vietnamese")
        print(res["text"])
