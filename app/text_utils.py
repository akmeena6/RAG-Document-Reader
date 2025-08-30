import io
import re
import unicodedata

import fitz  # PyMuPDF
import pytesseract
import streamlit as st
from langchain.text_splitter import RecursiveCharacterTextSplitter
from PIL import Image
from pypdf import PdfReader


def extract_text_from_pdf(file):
    # pdf_file = PdfReader(file)
    text = ""
    # for page in pdf_file.pages:
    #     text += page.extract_text() + "\n"
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)

            # Standard text extraction first
            page_text = page.get_text()
            st.write(f"Extracted {len(page_text)} characters from page {page_num}")
            if not page_text.strip():
                try:
                    st.write("Performing OCR on page")
                    # If no text found, use OCR(Optical Character Recognition)
                    image_list = page.get_images(full=True)
                    print(f"Found {len(image_list)} images on page {page_num}")
                    if image_list:
                        for img in image_list:
                            xref = img[0]
                            base_image = doc.extract_image(xref)
                            image_bytes = base_image["image"]

                            # Convert the image bytes to a PIL Image object
                            pil_image = Image.open(io.BytesIO(image_bytes))

                            # Use pytesseract to perform OCR on the image
                            ocr_text = pytesseract.image_to_string(pil_image)
                            page_text += ocr_text + "\n"
                    else:
                        # Blank documents
                        page_text = "[No text or image content found on this page.]"

                except Exception as e:
                    print(f"OCR failed for page {page_num}: {e}")
                    page_text = "[OCR failed for this page.]"
            text += page_text + "\n"

    except Exception as e:
        print(f"Failed to open PDF file: {e}")
        return ""

    return text


def text_cleaning(text):
    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)

    # Remove non-printable characters
    text = "".join(ch for ch in text if ch.isprintable() or ch.isspace())

    # Remove multiple spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Collapse multiple newlines
    text = re.sub(r"\n{2,}", "\n\n", text)

    # Strip leading/trailing spaces
    text = text.strip()

    return text


def convert_text_to_chunks(text, chunk_size=1000, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len
    )
    return splitter.split_text(text)
