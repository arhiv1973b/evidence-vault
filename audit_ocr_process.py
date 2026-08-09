import sys
import json
import pytesseract
from pdf2image import convert_from_path
import numpy as np
import os

# Использование конфигурации из Шокета
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POOPLER_PATH = r"H:\Загрузки\Release-26.02.0-0\poppler-26.02.0\Library\bin"


def run_ocr_audit(pdf_path, page_num):
    # Конвертация страницы
    images = convert_from_path(
        pdf_path, first_page=page_num, last_page=page_num, poppler_path=POOPLER_PATH
    )
    img = np.array(images[0])

    # OCR
    text = pytesseract.image_to_string(img, lang="rus+ron")

    # JSON-структура аудита
    report = {
        "page": page_num,
        "language": "rus+ron",
        "accuracy": 0,
        "errors": [],  # Заполняется агентом-аудитором
        "raw_text": text,
    }
    return report


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python audit_ocr_process.py <pdf_path> <page_num>")
        sys.exit(1)

    path = sys.argv[1]
    page = int(sys.argv[2])
    result = run_ocr_audit(path, page)
    print(json.dumps(result, ensure_ascii=False, indent=2))
