import tempfile
import speech_recognition as sr
from pydub import AudioSegment

def process_audio_file(file_path):
    """Nhận diện giọng nói từ file âm thanh (đường dẫn cụ thể)."""
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(file_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="vi-VN")
        return {"success": True, "text": text}
    except sr.UnknownValueError:
        return {"success": False, "message": "❌ Không thể nhận diện giọng nói trong file."}
    except Exception as e:
        return {"success": False, "message": f"Lỗi xử lý file âm thanh: {e}"}


def speech_to_text(audio_bytes=None, uploaded_file=None):
    """
    Nếu có audio_bytes → xử lý ghi âm từ mic.
    Nếu có uploaded_file → xử lý file tải lên.
    """
    try:
        if audio_bytes:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            return process_audio_file(tmp_path)

        elif uploaded_file:
            temp_audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
            # Dùng pydub để chuyển đổi sang wav
            audio = AudioSegment.from_file(uploaded_file)
            audio.export(temp_audio_path, format="wav")
            return process_audio_file(temp_audio_path)

        else:
            return {"success": False, "message": "❗ Không có dữ liệu âm thanh."}

    except Exception as e:
        return {"success": False, "message": f"Lỗi xử lý: {e}"}

