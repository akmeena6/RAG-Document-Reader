import streamlit as st
from text_utils import convert_text_to_chunks, extract_text_from_pdf, text_cleaning

st.set_page_config(page_title="PDF Reader", layout="wide")
st.title("PDF text Extracter")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")


if uploaded_file is not None:
    with st.spinner("Extracting text ....."):
        extracted_text = extract_text_from_pdf(uploaded_file)
        normalized_text = text_cleaning(extracted_text)
        chunks = convert_text_to_chunks(normalized_text)
        st.success("✅ Extraction complete!")
        st.text_area("Extracted Text", extracted_text, height=400)
        st.text_area("Normalized Text", normalized_text, height=400)

        st.subheader("Generated Chunks")
        for i, chunk in enumerate(chunks, start=1):
            st.markdown(f"**Chunk {i}**")
            st.write(chunk)
