import streamlit as st
from pdf_utils import extract_text_from_pdf

st.set_page_config(page_title="PDF Reader", layout="wide")
st.title("PDF text Extracter")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")


if uploaded_file is not None:
    with st.spinner("Extracting text ....."):
        extracted_text = extract_text_from_pdf(uploaded_file)
        st.success("✅ Extraction complete!")
        st.text_area("Extracted Text", extracted_text, height=400)
