import io
from PIL import Image
import pytesseract

from . import ExtractedPage
from backend.providers.client import NeuroFlowClient
from backend.providers.router import RoutingCriteria
from backend.providers.base import ChatMessage

def extract_image(file_path: str, client: NeuroFlowClient) -> list[ExtractedPage]:
    pages: list[ExtractedPage] = []

    # Load and resize image
    img = Image.open(file_path)
    img.thumbnail((1024, 1024))  # longest side max 1024px

    # OCR text
    ocr_text = pytesseract.image_to_string(img, config="--psm 6")

    # Vision LLM description
    criteria = RoutingCriteria(task_type="rag_generation", require_vision=True)
    messages = [ChatMessage(role="user", content="Describe this image in detail.")]
    # Convert PIL image to bytes for LLM if supported
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    # Some vision models accept multi-modal input: [text, image]
    messages[0].content = [
        {"type": "text", "text": "Describe this image in detail."},
        {"type": "image", "image_data": img_bytes.getvalue()},
    ]

    result = client.chat(messages, criteria)

    description = result.content + "\n\nText found in image: " + ocr_text

    pages.append(
        ExtractedPage(
            page_number=1,
            content=description,
            content_type="image_description",
            metadata={"file_path": file_path, "ocr_text_length": len(ocr_text)},
        )
    )

    return pages
