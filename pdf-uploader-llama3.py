import streamlit as st
import fitz  # PyMuPDF
from langchain.prompts import ChatPromptTemplate
from langchain.llms import Ollama
from langchain.chains import LLMChain

# Initialize the Ollama LLM (adjust with the correct parameters if needed)
llm = Ollama(model="llama3")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Please respond to the questions"),
        ("user", "Question:{question}"),
    ]
)

chain = LLMChain(llm=llm, prompt=prompt)

st.title('Langchain Chatbot With LLAMA2 model')

st.header("Upload documents:")
uploaded_files = st.file_uploader("Upload your documents (PDFs only):", type=["pdf"], accept_multiple_files=True)

add_document_button = st.button("Add documents")

added_documents = []

st.header("Ask a question:")
question_text = st.text_input("Ask your question:")

def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

if add_document_button and uploaded_files:
    for uploaded_file in uploaded_files:
        text = extract_text_from_pdf(uploaded_file)
        added_documents.append(text)
    st.write("Documents added!")
    st.write("Current documents:", added_documents)

if question_text and added_documents:
    st.write("Received question:", question_text)
    context = "\n\n".join(added_documents)
    prompt_input = {"question": question_text, "context": context}

    st.write("Sending prompt to LLM with context:", prompt_input)
    answer = chain.run(prompt_input)
    st.write("Answer:", answer)
else:
    if not added_documents:
        st.write("No documents added yet.")
    if not question_text:
        st.write("No question asked yet.")
