import os
import tempfile
import fitz  # pymupdf
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from pdf2image import convert_from_path
from supabase import create_client
from dotenv import load_dotenv
from app.utils.text_cleaner import clean_ocr_text

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\poppler\poppler-25.12.0\Library\bin"
TESS_CONFIG = r"--oem 1 --psm 6"


def download_pdf_from_supabase(bucket: str, file_path: str) -> str:
    response = supabase.storage.from_(bucket).download(file_path)
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_pdf.write(response)
    temp_pdf.close()
    return temp_pdf.name


def is_unicode_hindi(text: str) -> bool:
    """Check if extracted text contains proper Unicode Hindi characters."""
    hindi_chars = sum(1 for ch in text if '\u0900' <= ch <= '\u097F')
    total_chars = len(text.strip())
    if total_chars == 0:
        return False
    # If more than 5% of chars are proper Hindi Unicode, it's Unicode encoded
    return (hindi_chars / total_chars) > 0.05


def extract_with_pymupdf(pdf_path: str) -> str:
    """Extract text using PyMuPDF — works for Unicode fonts (class 6,7,8)."""
    full_text = ""
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        print(f"  Processing page {i + 1}/{len(doc)}...")
        text = page.get_text("text")
        if text:
            full_text += text + "\n"
    doc.close()
    return full_text


def preprocess_image(img: Image.Image) -> Image.Image:
    """Preprocess image for better OCR on Hindi text."""
    img = img.convert("L")
    img = ImageEnhance.Contrast(img).enhance(1.5)
    img = ImageEnhance.Brightness(img).enhance(1.2)
    img = img.filter(ImageFilter.SHARPEN)
    img = img.convert("RGB")
    return img


def extract_with_ocr(pdf_path: str) -> str:
    """Fallback OCR — used for legacy Kruti Dev encoded PDFs (class 9,10)."""
    print("  → Legacy font detected, switching to OCR...")
    images = convert_from_path(
        pdf_path,
        poppler_path=POPPLER_PATH,
        dpi=300,
        fmt="PNG",
    )
    full_text = ""
    for i, img in enumerate(images):
        print(f"  OCR page {i + 1}/{len(images)}...")
        processed = preprocess_image(img)
        text = pytesseract.image_to_string(
            processed,
            lang="hin+eng",
            config=TESS_CONFIG
        )
        full_text += text + "\n"
    return full_text


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Smart extraction:
    - First tries PyMuPDF (fast, perfect for Unicode fonts)
    - If Hindi not detected properly, falls back to OCR
    """
    # Try PyMuPDF first
    text = extract_with_pymupdf(pdf_path)


    if text.strip() and not is_unicode_hindi(text):
        # Check if it might be a Hindi file by looking at file path
        # (already handled in process_pdf_from_supabase)
        return text  # Return as-is for non-Hindi files (English, Math, Science)

    return text


def process_pdf_from_supabase(bucket: str, file_path: str) -> str:
    print(f"Downloading: {file_path}")
    local_pdf = download_pdf_from_supabase(bucket, file_path)

    print(f"Extracting text...")

    # Try PyMuPDF first
    text = extract_with_pymupdf(pdf_path=local_pdf)

    # For Hindi files — check if encoding is correct
    is_hindi_file = "/hindi/" in file_path.lower()

    if is_hindi_file and not is_unicode_hindi(text):
        # Legacy Kruti Dev font — fallback to OCR
        print(f"  → Garbled text detected for Hindi file, using OCR fallback...")
        text = extract_with_ocr(local_pdf)

    print(f"Cleaning text...")
    cleaned_text = clean_ocr_text(text)

    try:
        os.unlink(local_pdf)
    except Exception:
        pass

    return cleaned_text


def list_all_pdfs(bucket: str):
    all_files = []
    classes = supabase.storage.from_(bucket).list()

    for class_folder in classes:
        class_name = class_folder["name"]
        subjects = supabase.storage.from_(bucket).list(class_name)

        for subject_folder in subjects:
            subject_name = subject_folder["name"]
            chapters = supabase.storage.from_(bucket).list(
                f"{class_name}/{subject_name}"
            )

            for chapter in chapters:
                if chapter["name"].endswith(".pdf"):
                    full_path = f"{class_name}/{subject_name}/{chapter['name']}"
                    all_files.append(full_path)

    return all_files