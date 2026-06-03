import io
from dataclasses import asdict
import pypdfium2
import pdfplumber
import pytesseract
from PIL import Image

from . import ExtractedPage

def extract_pdf(file_path: str) -> list[ExtractedPage]:
    pages: list[ExtractedPage] = []

    # Open PDF with pypdfium2
    pdf = pypdfium2.PdfDocument(file_path)
    for i, page in enumerate(pdf):
        text = page.get_textpage().get_text_range()
        metadata = {"page_number": i + 1}

        # If text is too short, assume scanned → OCR
        if len(text.strip()) < 50:
            bitmap = page.render(scale=2.0).to_pil()
            ocr_text = pytesseract.image_to_string(bitmap, config="--psm 6")
            pages.append(
                ExtractedPage(
                    page_number=i + 1,
                    content=ocr_text,
                    content_type="text",
                    metadata=metadata,
                )
            )
        else:
            pages.append(
                ExtractedPage(
                    page_number=i + 1,
                    content=text,
                    content_type="text",
                    metadata=metadata,
                )
            )

    # Extract tables separately with pdfplumber
    with pdfplumber.open(file_path) as pdfp:
        for i, page in enumerate(pdfp.pages):
            tables = page.extract_tables()
            for table in tables:
                md_table = "\n".join([" | ".join(row) for row in table])
                pages.append(
                    ExtractedPage(
                        page_number=i + 1,
                        content=md_table,
                        content_type="table",
                        metadata={"page_number": i + 1, "extracted_with": "pdfplumber"},
                    )
                )

    return pages
