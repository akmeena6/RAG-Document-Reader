import os

import google.generativeai as genai
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configure the Google AI client
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    print("Error: Google API key not found.")

# Define a new, simpler prompt template for Gemini
template = """
You are a helpful AI assistant. Answer the user's question based ONLY on the context provided below.
If the context does not contain the answer, state that the information is not available in the document.
Do not add any information that is not in the context. Be concise.

Context:
{context}

Question: {query}
"""

# Create a PromptTemplate instance
prompt_template = PromptTemplate(
    input_variables=["context", "query"], template=template
)


def generate_llm_answer(query: str, context_chunks: list[str]) -> str:
    """
    Generates an answer using the Gemini model.
    """
    if not GOOGLE_API_KEY:
        return "Error: Google API key not configured. Please set GOOGLE_API_KEY in your .env file."

    # Initialize the Gemini model
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Combine the context chunks into a single string
    context = "\n\n".join(context_chunks)

    # Format the prompt using the template
    formatted_prompt = prompt_template.format(context=context, query=query)

    # Send the prompt to the LLM
    try:
        response = model.generate_content(formatted_prompt)
        return response.text
    except Exception as e:
        return f"Error calling Google Gemini API: {e}"
