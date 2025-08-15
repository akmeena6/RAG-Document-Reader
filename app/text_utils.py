import re
import unicodedata

from langchain.text_splitter import RecursiveCharacterTextSplitter
from pypdf import PdfReader


def extract_text_from_pdf(file):
    pdf_file = PdfReader(file)
    text = ""
    for page in pdf_file.pages:
        text += page.extract_text() + "\n"

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
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " "],
    )
    return splitter.split_text(text)
