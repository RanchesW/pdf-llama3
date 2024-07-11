import PyPDF2
from ollama import Ollama

def extract_text_from_pdf(pdf_path):
    """ Извлечь текст из PDF файла """
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfFileReader(file)
        text = ''
        for page_num in range(reader.numPages):
            page = reader.getPage(page_num)
            text += page.extractText()
    return text

def analyze_text_with_llama(text):
    """ Анализировать текст с помощью модели LLaMA """
    llm = Ollama(model="llama3")
    response = llm(text)
    return response

# Путь к PDF файлу
pdf_path = 'png2pdf.pdf'

# Извлечение текста из файла
pdf_text = extract_text_from_pdf(pdf_path)

# Анализ текста с помощью LLaMA
analysis_result = analyze_text_with_llama(pdf_text)
print("Результат анализа:", analysis_result)
