import os

from dotenv import load_dotenv
from groq import Groq
from langchain.prompts import PromptTemplate

load_dotenv()
key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=key)

tmpl = """
You are a helpful AI assistant. Answer the user's question based ONLY on the context provided below.
If the context does not contain the answer, state that the information is not available.

Context:
{context}

Question: {query}
"""

prompt_tmpl = PromptTemplate(input_variables=["context", "query"], template=tmpl)


def generate_llm_answer(query, chunks):
    if not key:
        return "Error: GROQ_API_KEY missing."

    ctx = "\n\n".join(chunks)
    fmt_msg = prompt_tmpl.format(context=ctx, query=query)

    try:
        resp = client.chat.completions.create(
            messages=[{"role": "user", "content": fmt_msg}],
            model="llama3-8b-8192-instant",
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"
