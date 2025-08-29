import os

import jwt
import streamlit as st
from llm_utils import generate_llm_answer
from text_utils import convert_text_to_chunks, extract_text_from_pdf, text_cleaning
from user_db_utils import create_jwt_token, create_user, verify_jwt_token, verify_user
from vectordb_utils import add_chunks_to_collection, semantic_search

st.set_page_config(page_title="PDF Reader", layout="wide")
st.title("PDF Chatbot")

# --- Token Validation at the Top ---
# This is the key part that ensures a check on every rerun
if "token" in st.session_state and st.session_state.token:
    payload = verify_jwt_token(st.session_state.token)
    if isinstance(payload, str):  # Token is invalid or expired
        st.error(payload)
        st.session_state.token = None  # Clear the invalid token
        st.session_state.username = None
        st.info("Please log in again.")
    else:
        st.session_state.username = payload["username"]
else:
    st.session_state.token = None
    st.session_state.username = None


# --- User Interface Logic ---
def login_form():
    # Renders the login form and handles JWT token creation.
    with st.form("login_form"):
        st.subheader("Login to your account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if verify_user(username, password):
                token = create_jwt_token(username)
                st.session_state.token = token
                st.session_state.username = username
                st.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.error("Invalid username or password.")


def signup_form():
    # Renders the signup form.
    with st.form("signup_form"):
        st.subheader("Create a new account")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.form_submit_button("Sign Up"):
            success, message = create_user(new_username, new_password)
            if success:
                st.success(message + " You can now log in.")
            else:
                st.error(message)


def main_app_content():
    # The main content of the application after a successful login.
    st.write(f"Welcome, {st.session_state.username}!")
    st.sidebar.button("Logout", on_click=logout)

    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    if uploaded_file is not None:
        with st.spinner("Extracting text..."):
            extracted_text = extract_text_from_pdf(uploaded_file)
            normalized_text = text_cleaning(extracted_text)
            chunks = convert_text_to_chunks(normalized_text)
            st.success("✅ Extraction complete!")
            st.text_area("Extracted Text", extracted_text, height=400)
            st.text_area("Normalized Text", normalized_text, height=400)

        if st.button("Embed the Chunks and add to ChromaDB"):
            with st.spinner("Embedding and Adding chunks to ChromaDB..."):
                add_chunks_to_collection(chunks)
                st.success("✅ Chunks added to ChromaDB successfully!")

        user_query = st.text_input(
            "Your question:",
            placeholder="What is the main topic of the document?",
            key="search_input",
        )

        if user_query:
            with st.spinner("Searching for relevant chunks..."):
                context_chunks = semantic_search(user_query, topk_results=3)

            if context_chunks:
                with st.spinner("Generating answer..."):
                    llm_answer = generate_llm_answer(user_query, context_chunks)

                st.subheader("Answer:")
                st.success(llm_answer)

                with st.expander("View the context chunks used for this answer 📄"):
                    for chunk in context_chunks:
                        st.info(chunk)
            else:
                st.warning("No relevant chunks found for your query.")


def logout():
    # Handles user logout by clearing the JWT token.
    st.session_state.token = None
    st.session_state.username = None
    st.info("You have been logged out.")
    st.rerun()


# --- Conditional Rendering ---
if st.session_state.token:
    # If a valid token exists, show the main app content
    main_app_content()
else:
    # Otherwise, show the login/signup forms
    st.title("Welcome to the PDF RAG System")
    st.info("Please log in or sign up to continue.")
    choice = st.radio("Select an option:", ["Login", "Sign Up"])
    if choice == "Login":
        login_form()
    else:
        signup_form()
