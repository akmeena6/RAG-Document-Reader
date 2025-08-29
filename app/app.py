import os

import jwt
import streamlit as st
from llm_utils import generate_llm_answer
from text_utils import convert_text_to_chunks, extract_text_from_pdf, text_cleaning
from user_db_utils import create_user, verify_user
from vectordb_utils import add_chunks_to_collection, semantic_search

st.set_page_config(page_title="PDF Reader", layout="wide")
st.title("PDF text Extracter")

# Global JWT Secret
JWT_SECRET = ""

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""


def login_form():
    """Renders the login form."""
    with st.form("login_form"):
        st.subheader("Login to your account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if verify_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.error("Invalid username or password.")


def signup_form():
    """Renders the signup form."""
    with st.form("signup_form"):
        st.subheader("Create a new account")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.form_submit_button("Sign Up"):
            if new_password != confirm_password:
                st.error("Passwords do not match!")
            else:
                success, message = create_user(new_username, new_password)
                if success:
                    st.success(message + " You can login now.")
                else:
                    st.error(message)


def main_app():
    """Main application logic after login."""

    st.write(f"Hello, {st.session_state.username}! You have successfully logged in.")
    st.sidebar.button("Logout", on_click=logout)

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


def logout():
    """Logs out the user."""
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.success("You have been logged out.")
    st.experimental_rerun()


# Conditional rendering based on authentication state
if st.session_state.logged_in:
    main_app()
else:
    st.title("Welcome to Meri Duniya")
    st.info("Please log in or sign up to continue.")

    choice = st.radio("Select an option:", ["Login", "Sign Up"])
    if choice == "Login":
        login_form()
    else:
        signup_form()
