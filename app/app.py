import os

import streamlit as st
from text_utils import convert_text_to_chunks, extract_text_from_pdf, text_cleaning
from vectordb_utils import add_chunks_to_collection, semantic_search

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

        if st.button("Embed the Chunks and add to ChromaDB"):
            with st.spinner("Embedding and Adding chunks to ChromaDB..."):
                add_chunks_to_collection(chunks)
                st.success("✅ Chunks added to ChromaDB successfully!")

        # taking user questions about the document that he uploaded
        user_query = st.text_input(
            "Your question:",
            placeholder="What is the main topic of the document?",
            key="search_input",
        )

        if user_query:
            # Show a spinner while the search is in progress
            with st.spinner("Searching for relevant chunks..."):
                # Perform the semantic search
                results = semantic_search(user_query, topk_results=3)

            st.subheader("Search Results")

            if results:
                # Use an expander to neatly display the retrieved chunks
                with st.expander("View the top 3 most relevant chunks 📄"):
                    for chunk in results:
                        # Using st.info provides a nicely formatted box for each chunk
                        st.info(chunk)
            else:
                st.warning("No relevant chunks found for your query.")
