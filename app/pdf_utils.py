from pypdf import PdfReader


def extract_text_from_pdf(file):
    pdf_file = PdfReader(file)
    text = ""
    for page in pdf_file.pages:
        text += page.extract_text() + "\n"

    return text
