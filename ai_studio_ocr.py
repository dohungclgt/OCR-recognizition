# ai_studio_ocr.py
from typing import List, Optional
from io import BytesIO
from PIL import Image
import math

from google import genai
from google.genai import types

# Model mặc định: nhanh. Có thể đổi "gemini-2.5-pro" nếu cần độ chính xác cao hơn.
DEFAULT_VISION_MODEL = "gemini-2.5-flash"

_client = genai.Client()  # Tự lấy GEMINI_API_KEY từ env, theo docs.

def _ensure_rgb_jpeg(image_bytes: bytes, max_side: int = 1800, jpeg_quality: int = 85) -> bytes:
    """
    - Đọc ảnh bytes -> PIL -> ép về RGB + nén JPEG
    - Giới hạn cạnh dài để giữ request <~ vài MB (SDK khuyến nghị inline < 20MB)
    """
    im = Image.open(BytesIO(image_bytes))
    im = im.convert("RGB")
    w, h = im.size
    scale = min(1.0, max_side / max(w, h))
    if scale < 1.0:
        im = im.resize((math.floor(w * scale), math.floor(h * scale)), Image.LANCZOS)
    out = BytesIO()
    im.save(out, format="JPEG", quality=jpeg_quality, optimize=True)
    return out.getvalue()

def _image_bytes_to_part(image_bytes: bytes, mime: str = "image/jpeg") -> types.Part:
    return types.Part.from_bytes(data=image_bytes, mime_type=mime)

def gemini_ocr_image(image_bytes: bytes,
                     prompt: Optional[str] = None,
                     model: str = DEFAULT_VISION_MODEL) -> str:
    """
    OCR 1 ảnh bằng Gemini.
    prompt: nếu None sẽ dùng mặc định (trích xuất thuần văn bản, giữ dòng).
    """
    # Chuẩn hóa ảnh -> JPEG gọn nhẹ
    jpeg_bytes = _ensure_rgb_jpeg(image_bytes)

    user_prompt = prompt or (
        "Extract all readable text from this image in natural reading order. "
        "Keep line breaks. Vietnamese + English. Output plain text only."
    )

    contents = [
        _image_bytes_to_part(jpeg_bytes, "image/jpeg"),
        user_prompt
    ]

    resp = _client.models.generate_content(model=model, contents=contents)
    return (resp.text or "").strip()

def gemini_ocr_images(images: List[bytes],
                      per_page_prompt: Optional[str] = None,
                      joiner: str = "\n\n---\n\n",
                      model: str = DEFAULT_VISION_MODEL) -> str:
    """
    OCR nhiều ảnh (ví dụ các trang PDF đã render).
    Ghép kết quả lại, có vạch ngăn cách giữa các trang.
    """
    results = []
    for idx, img_bytes in enumerate(images, start=1):
        text = gemini_ocr_image(
            img_bytes,
            prompt=per_page_prompt or f"Page {idx}: extract text. Keep line breaks.",
            model=model
        )
        results.append(text)
    return joiner.join(results).strip()
