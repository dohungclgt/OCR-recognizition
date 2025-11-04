import audiorecorder
import streamlit as st
from image_to_text import image_to_text
from pdf_to_text import pdf_to_text
from scan_to_text import scan_to_text
from speech_to_text import speech_to_text

st.set_page_config(page_title="Universal OCR App", page_icon="🧠")
st.title("🧠 Universal OCR - Nhận diện chữ từ Ảnh, PDF, Scan, và Giọng nói")

# === Sidebar: Language + Mode + Description ===
st.sidebar.header("⚙️ Settings")

lang = st.sidebar.radio("🌐 Language / Ngôn ngữ", ["English", "Tiếng Việt"])

if lang == "English":
    sidebar_info = {
        "📸 Image": "Upload an image (PNG, JPG, JPEG) to extract text using OCR.",
        "📄 PDF": "Upload a PDF file to extract text from scanned pages.",
        "📷 Scan": "Turn on the webcam and take a picture to scan text.",
        "🎤 Speech": "Record or upload a voice file to convert speech to text."
    }
else:
    sidebar_info = {
        "📸 Ảnh": "Tải lên ảnh (PNG, JPG, JPEG) để nhận diện chữ.",
        "📄 PDF": "Tải lên file PDF để trích xuất chữ từ trang quét.",
        "📷 Scan": "Bật webcam để chụp ảnh và quét chữ.",
        "🎤 Giọng nói": "Ghi âm hoặc tải file giọng nói để chuyển thành văn bản."
    }

mode = st.sidebar.radio(
    "🧩 " + ("Select Mode" if lang == "English" else "Chọn chế độ"),
    list(sidebar_info.keys())
)

st.sidebar.markdown("---")
st.sidebar.subheader("ℹ️ " + ("Description" if lang == "English" else "Mô tả"))
st.sidebar.info(sidebar_info[mode])

# === IMAGE MODE ===
if mode in ["📸 Ảnh", "📸 Image"]:
    st.subheader("🖼️ " + ("Image to Text" if lang == "English" else "Chuyển Ảnh thành Văn bản"))
    col1, col2, col3 = st.columns([1, 1, 1.2])

    with col1:
        uploaded_file = st.file_uploader(
            "📤 " + ("Upload Image" if lang == "English" else "Tải lên ảnh"),
            type=["png", "jpg", "jpeg"]
        )
        if uploaded_file:
            temp_path = "uploaded_image.png"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())

            if st.button("🧠 " + ("Recognize Text" if lang == "English" else "Nhận diện chữ"), use_container_width=True):
                result = image_to_text(temp_path)
                if result["success"]:
                    st.session_state["img_result"] = result["text"]
                else:
                    st.error(result["message"])

    with col2:
        if uploaded_file:
            st.image(temp_path, caption="Preview", use_column_width=True)

    with col3:
        if "img_result" in st.session_state:
            st.text_area("📝 " + ("Result" if lang == "English" else "Kết quả"),
                         st.session_state["img_result"], height=300)
            st.download_button(
                "💾 " + ("Download text" if lang == "English" else "Tải kết quả"),
                st.session_state["img_result"],
                file_name="image_result.txt"
            )

# === PDF MODE ===
elif mode in ["📄 PDF", "📄 Pdf"]:
    uploaded_pdf = st.file_uploader(
        "📁 " + ("Upload PDF file" if lang == "English" else "Tải lên file PDF"),
        type=["pdf"]
    )
    if uploaded_pdf:
        temp_path = "uploaded_file.pdf"
        with open(temp_path, "wb") as f:
            f.write(uploaded_pdf.read())
        if st.button("🧠 " + ("Extract Text" if lang == "English" else "Nhận diện chữ từ PDF")):
            result = pdf_to_text(temp_path)
            if result["success"]:
                st.text_area("📝 Result:", result["text"], height=300)
                st.download_button(
                    "💾 Download text" if lang == "English" else "💾 Tải kết quả",
                    result["text"],
                    file_name="pdf_result.txt"
                )
            else:
                st.error(result["message"])

# === SCAN MODE ===
elif mode in ["📷 Scan", "📷 Scan"]:
    st.info("📸 " + ("Use camera to take photo and scan text." if lang == "English" else "Bật webcam và chụp ảnh để nhận diện chữ."))
    enable_cam = st.toggle("📷 " + ("Enable Camera" if lang == "English" else "Bật/Tắt Camera"))

    if enable_cam:
        camera_image = st.camera_input("📸 " + ("Take a picture" if lang == "English" else "Chụp ảnh bằng webcam"))
        if camera_image is not None:
            if st.button("🧠 " + ("Scan Text" if lang == "English" else "Nhận diện chữ từ ảnh đã chụp")):
                result = scan_to_text(camera_image.getvalue())
                if result["success"]:
                    st.text_area("📝 Result:", result["text"], height=250)
                    st.download_button(
                        "💾 Download text" if lang == "English" else "💾 Tải kết quả",
                        result["text"],
                        file_name="scan_result.txt"
                    )
                else:
                    st.error(result["message"])

# === SPEECH MODE ===
elif mode in ["🎤 Giọng nói", "🎤 Speech"]:
    st.info("🎤 " + (
        "Choose how to input your audio:" if lang == "English"
        else "Chọn cách nhập âm thanh để nhận diện:"
    ))

    choice = st.radio(
        "🎧 " + ("Select method:" if lang == "English" else "Lựa chọn:"),
        ["🎙️ " + ("Record directly" if lang == "English" else "Ghi âm trực tiếp"),
         "📁 " + ("Upload audio file" if lang == "English" else "Tải lên file giọng nói")]
    )

    if "Record" in choice or "Ghi âm" in choice:
        audio = audiorecorder.audiorecorder(
            "🎙️ " + ("Start recording" if lang == "English" else "Bắt đầu ghi âm"),
            "🛑 " + ("Stop recording" if lang == "English" else "Dừng ghi âm")
        )

        if len(audio) > 0:
            st.audio(audio.export().read(), format="audio/wav")
            if st.button("🧠 " + ("Recognize Speech" if lang == "English" else "Nhận diện giọng nói")):
                result = speech_to_text(audio_bytes=audio.export().read(), lang=lang)
                if result["success"]:
                    st.success("✅ " + ("Recognition complete!" if lang == "English" else "Đã nhận diện xong!"))
                    st.text_area("📝 Result:", result["text"], height=250)
                    st.download_button(
                        "💾 " + ("Download text" if lang == "English" else "Tải kết quả"),
                        result["text"],
                        file_name="speech_result.txt"
                    )
                else:
                    st.error(result["message"])

    elif "Upload" in choice or "Tải lên" in choice:
        uploaded_audio = st.file_uploader(
            "📁 " + ("Upload audio file" if lang == "English" else "Chọn file âm thanh"),
            type=["wav", "mp3", "m4a"]
        )
        if uploaded_audio:
            st.audio(uploaded_audio, format="audio/wav")
            if st.button("🧠 " + ("Recognize Speech" if lang == "English" else "Nhận diện file giọng nói")):
                result = speech_to_text(uploaded_file=uploaded_audio, lang=lang)
                if result["success"]:
                    st.success("✅ " + ("Recognition complete!" if lang == "English" else "Đã nhận diện xong!"))
                    st.text_area("📝 Result:", result["text"], height=250)
                    st.download_button(
                        "💾 " + ("Download text" if lang == "English" else "Tải kết quả"),
                        result["text"],
                        file_name="uploaded_audio_result.txt"
                    )
                else:
                    st.error(result["message"])
