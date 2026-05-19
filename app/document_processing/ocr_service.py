from fastapi import UploadFile


async def extract_text_from_upload(file: UploadFile) -> str:
    """Simulated OCR layer.

    In production this boundary would call a managed OCR engine. For this
    project it deterministically decodes text files and falls back to filename
    hints for PDFs/images so downstream parsers can still be exercised.
    """

    content = await file.read()

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = ""

    if text.strip():
        return text

    return file.filename.replace("_", " ").replace("-", " ")
