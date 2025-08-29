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
                st.experimental_rerun()
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

    # ... All your PDF processing and RAG logic here ...
    # This section remains unchanged from your original app.py
    # ...


def logout():
    # Handles user logout by clearing the JWT token.
    st.session_state.token = None
    st.session_state.username = None
    st.info("You have been logged out.")
    st.experimental_rerun()


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
