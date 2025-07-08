import os, mammoth
from mutagen import File as MutagenFile
from moviepy import VideoFileClip

# from PyPDF2 import PdfReader
from docx import Document


def get_media_duration(file_path, media_type):
    try:
        if media_type == 'audio':
            audio = MutagenFile(file_path)
            if audio is not None and audio.info.length:
                return format_duration(audio.info.length)
        elif media_type == 'video':
            clip = VideoFileClip(file_path)
            duration = clip.duration
            clip.close()
            return format_duration(duration)
    except Exception as e:
        return "0:00"

def format_duration(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"





def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == '.docx':
            return extract_from_docx(file_path)

        elif ext == '.doc':
            return extract_from_doc(file_path)

        return f"Unsupported file type: {ext}"
    except Exception as e:
        print(f"[ERROR] extract_text_from_file: {e}")
        return "Unable to extract text."


def extract_from_docx(file_path):
    try:
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs).strip()
    except Exception as e:
        print(f"[ERROR] extract_from_docx: {e}")
        return ""


def extract_from_doc(file_path):
    try:
        with open(file_path, "rb") as doc_file:
            result = mammoth.extract_raw_text(doc_file)
            return result.value.strip()
    except Exception as e:
        print(f"[ERROR] extract_from_doc: {e}")
        return ""

