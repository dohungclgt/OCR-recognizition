# app.py — Universal OCR App (Tesseract + Google AI Studio / Gemini)
from io import BytesIO
import os
import io
import tempfile
import pandas as pd
import streamlit as st
import audiorecorder
from PIL import Image
from docx import Document

# ====== MODULES ======
from image_to_text import image_to_text
from pdf_to_text import pdf_to_text
from scan_to_text import scan_to_text
from speech_to_text import speech_to_text
from smart_ai_extract import analyze_document_ai

# ====== GOOGLE GENAI SDK ======
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY", "your key here")

try:
    from google import genai
    from google.genai import types as gem_types
    _gemini_available = True
    _gem_client = genai.Client()
except Exception:
    _gemini_available = False
    _gem_client = None

# ====== GEMINI HELPER ======
def _ensure_rgb_jpeg_bytes(file_bytes: bytes, max_side: int = 2400, jpeg_quality: int = 90) -> bytes:
    img = Image.open(BytesIO(file_bytes)).convert("RGB")
    w, h = img.size
    scale = min(1.0, max_side / max(w, h))
    if scale < 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    out = BytesIO()
    img.save(out, format="JPEG", quality=jpeg_quality, optimize=True)
    return out.getvalue()

def _extract_text_from_resp(resp) -> str:
    """Trích text an toàn từ phản hồi Gemini"""
    try:
        if getattr(resp, "text", None):
            return resp.text.strip()
        if getattr(resp, "candidates", None):
            for c in resp.candidates:
                if getattr(c, "content", None) and getattr(c.content, "parts", None):
                    chunks = []
                    for p in c.content.parts:
                        if getattr(p, "text", None):
                            chunks.append(p.text)
                    if chunks:
                        return "\n".join(chunks).strip()
        return ""
    except Exception:
        return ""

# ====== PAGE CONFIG ======
st.set_page_config(page_title="Universal OCR App", page_icon="🧠", layout="wide")
st.title("🧠 Universal OCR App (Tesseract + Google Gemini AI)")

# ====== SIDEBAR ======
st.sidebar.header("⚙️ Settings")
lang = st.sidebar.radio("🌐 Language / Ngôn ngữ", ["English", "Tiếng Việt"], index=1)
engine = st.sidebar.radio("🧠 OCR Engine", ["Tesseract (Local)", "Google AI Studio (Gemini)"], index=1)
gem_model = st.sidebar.selectbox("🤖 Gemini Model", ["gemini-2.5-flash", "gemini-2.5-pro"], index=0)

if st.sidebar.button("🔍 Test Gemini API"):
    if not _gemini_available:
        st.sidebar.error("❌ Chưa cài Google GenAI SDK hoặc chưa có GEMINI_API_KEY.")
    else:
        try:
            ping = _gem_client.models.generate_content(model=gem_model, contents="Return READY")
            st.sidebar.success("✅ Gemini hoạt động: " + (_extract_text_from_resp(ping) or "OK"))
        except Exception as e:
            st.sidebar.error(f"Lỗi Gemini: {e}")

modes = ["📸 Image", "📄 PDF", "📷 Scan", "🎤 Speech"] if lang == "English" else ["📸 Ảnh", "📄 PDF", "📷 Scan", "🎤 Giọng nói"]
mode = st.sidebar.radio("🧩 " + ("Select Mode" if lang == "English" else "Chọn chế độ"), modes)

# ====== HIỂN THỊ KẾT QUẢ ======
def show_result_box(text: str, height: int = 350, filename: str = "ocr_result.txt"):
    st.success("✅ " + ("Result:" if lang == "English" else "Kết quả:"))
    st.text_area("Output", text, height=height)
    st.download_button("💾 " + ("Download text" if lang == "English" else "Tải kết quả"), text, file_name=filename)

# ============================================================
# 📸 IMAGE MODE
# ============================================================
if mode in ["📸 Image", "📸 Ảnh"]:
    uploaded_file = st.file_uploader("📤 " + ("Upload image" if lang == "English" else "Tải lên ảnh"),
                                     type=["png", "jpg", "jpeg"])
    if uploaded_file:
        img_bytes = uploaded_file.read()
        st.image(img_bytes, caption="🖼️ " + ("Uploaded Image" if lang == "English" else "Ảnh đã tải lên"),
                 use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            run_ocr = st.button("🧠 " + ("Tesseract OCR" if lang == "English" else "Nhận diện (Tesseract)"))
        with col2:
            run_ai = st.button("🤖 " + ("Gemini AI Analysis" if lang == "English" else "Phân tích thông minh (Gemini AI)"))

        # --- TESSERACT ---
        if run_ocr:
            with st.spinner("⏳ " + ("Reading text..." if lang == "English" else "Đang nhận diện...")):
                temp_path = "temp_image.png"
                with open(temp_path, "wb") as f:
                    f.write(img_bytes)
                result = image_to_text(temp_path)
                if result["success"]:
                    show_result_box(result["text"], filename="ocr_image.txt")
                else:
                    st.error(result["message"])

        # --- GEMINI AI ---
        if run_ai:
            st.session_state.ai_result_text = None
            language_input = "Vietnamese" if "Việt" in lang else "English"
            with st.spinner("🔮 " + ("Analyzing..." if lang == "English" else "Đang phân tích...")):
                ai_result = analyze_document_ai(img_bytes, file_type="image", language=language_input)
                if ai_result["success"]:
                    st.session_state.ai_result_text = ai_result["text"]
                else:
                    st.error(ai_result["message"])

    # --- HIỂN THỊ KẾT QUẢ GEMINI ---
    if "ai_result_text" in st.session_state and st.session_state.ai_result_text:
        st.success("✅ " + ("Analysis Complete!" if lang == "English" else "Phân tích thành công!"))

        # 🌟 Thêm tùy chọn trích xuất văn bản
        extract_mode = st.radio(
            "🧠 " + ("Select text extraction mode:" if lang == "English" else "Chọn mức độ trích xuất văn bản:"),
            ["📄 Full Text", "🏷️ Key Fields Only", "✅ Choose Manually"]
            if lang == "English"
            else ["📄 Lấy hết văn bản", "🏷️ Chỉ lấy trường đã phân loại", "✅ Chọn thủ công các trường"],
            index=0
        )

        lines = [line.strip() for line in st.session_state.ai_result_text.split("\n") if line.strip()]

        if extract_mode.startswith("📄") or extract_mode.startswith("Full"):
            filtered_text = "\n".join(lines)

        elif extract_mode.startswith("🏷️") or extract_mode.startswith("Key"):
            filtered_text = "\n".join(line for line in lines if ":" in line)

        else:  # ✅ chọn thủ công
            key_value_lines = [line for line in lines if ":" in line]
            selected_fields = []
            st.write("🔍 " + ("Select fields to include:" if lang == "English" else "Chọn các trường muốn lấy:"))
            for line in key_value_lines:
                k, v = line.split(":", 1)
                if st.checkbox(f"{k.strip()}: {v.strip()}", value=True):
                    selected_fields.append(f"{k.strip()}: {v.strip()}")
            filtered_text = "\n".join(selected_fields) if selected_fields else "(Không có trường nào được chọn)"

        # --- Hiển thị kết quả sau lọc ---
        st.text_area("📜 " + ("Filtered result:" if lang == "English" else "Kết quả sau lọc:"),
                     filtered_text, height=400)

        # --- Tải xuống ---
        format_choice = st.radio("📥 " + ("Download as:" if lang == "English" else "Tải xuống định dạng:"),
                                 ["TXT", "DOCX", "Excel"])

        if format_choice == "TXT":
            st.download_button("💾 TXT", filtered_text, file_name="ai_result_filtered.txt")

        elif format_choice == "DOCX":
            doc = Document()
            doc.add_paragraph(filtered_text)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_doc:
                doc.save(tmp_doc.name)
                tmp_doc.seek(0)
                st.download_button(
                    "💾 DOCX",
                    tmp_doc.read(),
                    file_name="ai_result_filtered.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

        elif format_choice == "Excel":
            rows = []
            for line in filtered_text.split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    rows.append({"Trường": k.strip(), "Giá trị": v.strip()})
            if rows:
                df = pd.DataFrame(rows)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_xlsx:
                    df.to_excel(tmp_xlsx.name, index=False)
                    tmp_xlsx.seek(0)
                    st.download_button(
                        "💾 Excel",
                        tmp_xlsx.read(),
                        file_name="ai_result_filtered.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

# ============================================================
# 📄 PDF MODE
# ============================================================
elif mode in ["📄 PDF"]:
    uploaded_pdf = st.file_uploader("📁 " + ("Upload PDF file" if lang == "English" else "Tải lên file PDF"),
                                    type=["pdf"])
    if uploaded_pdf:
        pdf_bytes = uploaded_pdf.read()
        with open("temp_pdf.pdf", "wb") as f:
            f.write(pdf_bytes)

        col1, col2 = st.columns(2)
        with col1:
            run_ocr = st.button("🧠 " + ("OCR PDF" if lang == "English" else "Nhận diện PDF"))
        with col2:
            run_ai = st.button("🤖 " + ("Gemini Analysis" if lang == "English" else "Phân tích Gemini"))

        if run_ocr:
            with st.spinner("📄 " + ("Processing PDF..." if lang == "English" else "Đang xử lý PDF...")):
                result = pdf_to_text("temp_pdf.pdf")
                if result["success"]:
                    show_result_box(result["text"], filename="pdf_result.txt")
                else:
                    st.error(result["message"])

        if run_ai:
            language_input = "Vietnamese" if "Việt" in lang else "English"
            with st.spinner("🔮 " + ("Analyzing PDF..." if lang == "English" else "Phân tích PDF...")):
                ai_result = analyze_document_ai(pdf_bytes, file_type="pdf", language=language_input)
                if ai_result["success"]:
                    show_result_box(ai_result["text"], filename="ai_pdf.txt")
                else:
                    st.error(ai_result["message"])

# ============================================================
# 📷 SCAN MODE
# ============================================================
elif mode in ["📷 Scan"]:
    st.caption("💡 " + ("Tip: Place paper flat, bright lighting." if lang == "English"
                         else "Mẹo: Đặt giấy phẳng, đủ sáng khi chụp."))
    cam = st.camera_input("📸 " + ("Take a picture" if lang == "English" else "Chụp ảnh"))
    if cam:
        img_bytes = cam.getvalue()
        with st.spinner("🔍 " + ("Scanning..." if lang == "English" else "Đang quét...")):
            result = scan_to_text(img_bytes, lang=lang)
            if result["success"]:
                show_result_box(result["text"], filename="scan_result.txt")
            else:
                st.error(result["message"])

# ============================================================
# 🎤 SPEECH MODE
# ============================================================
elif mode in ["🎤 Speech", "🎤 Giọng nói"]:
    choice = st.radio("🎧 " + ("Select method:" if lang == "English" else "Chọn phương thức:"),
                      ["🎙️ " + ("Record directly" if lang == "English" else "Ghi âm trực tiếp"),
                       "📁 " + ("Upload file" if lang == "English" else "Tải file âm thanh")])

    if "Record" in choice or "Ghi" in choice:
        audio = audiorecorder.audiorecorder(
            "🎙️ " + ("Start Recording" if lang == "English" else "Bắt đầu ghi âm"),
            "🛑 " + ("Stop" if lang == "English" else "Dừng")
        )
        if len(audio) > 0:
            buf = BytesIO()
            audio.export(buf, format="wav")
            wav_bytes = buf.getvalue()
            st.audio(wav_bytes, format="audio/wav")

            if st.button("🧠 " + ("Transcribe Speech" if lang == "English" else "Nhận diện giọng nói")):
                result = speech_to_text(audio_bytes=wav_bytes, lang=lang)
                if result["success"]:
                    show_result_box(result["text"], filename="speech_result.txt")
                else:
                    st.error(result["message"])

    else:
        up = st.file_uploader("📁 " + ("Upload audio" if lang == "English" else "Chọn file âm thanh"),
                              type=["wav", "mp3", "m4a", "aac", "ogg", "flac"])
        if up:
            st.audio(up)
            if st.button("🧠 " + ("Recognize Audio" if lang == "English" else "Nhận diện âm thanh")):
                result = speech_to_text(uploaded_file=up, lang=lang)
                if result["success"]:
                    show_result_box(result["text"], filename="uploaded_audio_result.txt")
                else:
                    st.error(result["message"])
