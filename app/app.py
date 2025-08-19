import os

import streamlit as st
from llm_utils import generate_llm_answer
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
            with st.spinner("Searching for relevant chunks..."):
                context_chunks = semantic_search(user_query, topk_results=3)

            if context_chunks:
                # Generate the answer using the LLM
                with st.spinner("Generating answer..."):
                    llm_answer = generate_llm_answer(user_query, context_chunks)

                # Display the final answer
                st.subheader("Answer:")
                st.success(llm_answer)

                # Use an expander to show the context chunks used for the answer
                with st.expander("View the context chunks used for this answer 📄"):
                    for chunk in context_chunks:
                        st.info(chunk)

            else:
                st.warning("No relevant chunks found for your query.")
