from tkinter import filedialog, messagebox
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import re
import tkinter as tk
import torch
from transformers import BertTokenizer, BertForQuestionAnswering



pytesseract.pytesseract.tesseract_cmd = r'C:\Users\BOSuser\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'


def extract_text_from_image(image_path):
    img = Image.open(image_path)
    custom_config = r'--oem 3 --psm 6 -l eng+rus+kaz'  
    text = pytesseract.image_to_string(img, config=custom_config)
    return text
import sqlite3
from hashlib import md5

def connect_db():
    conn = sqlite3.connect('ocr_results.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS documents (filename TEXT, hash TEXT, text TEXT)''')
    conn.commit()
    return conn

def get_text_from_db(conn, pdf_path):
    file_hash = md5(open(pdf_path, 'rb').read()).hexdigest()
    c = conn.cursor()
    c.execute("SELECT text FROM documents WHERE hash = ?", (file_hash,))
    result = c.fetchone()
    if result:
        return result[0]
    return None

def store_text_in_db(conn, pdf_path, text):
    file_hash = md5(open(pdf_path, 'rb').read()).hexdigest()
    c = conn.cursor()
    c.execute("INSERT INTO documents (filename, hash, text) VALUES (?, ?, ?)", (pdf_path, file_hash, text))
    conn.commit()

def extract_text_from_pdf_with_cache(pdf_path):
    conn = connect_db()
    text = get_text_from_db(conn, pdf_path)
    if text is not None:
        print("Using cached result")
        return text
    print("Performing OCR")
    text = extract_text_from_pdf(pdf_path)
    store_text_in_db(conn, pdf_path, text)
    return text


def extract_text_from_pdf(pdf_path):
    images = convert_from_path(pdf_path)
    text = ""
    for img in images:
        text += pytesseract.image_to_string(img, config=r'--oem 3 --psm 6 -l eng+rus+kaz')
    return text


def find_answer_in_text(text, question):
    key_phrase = question.replace('Каков', '').replace('?', '').strip().lower()
    
    synonyms = {
        'дата': ['дата', 'сроки', 'период', 'когда'],
        'место': ['место', 'локация', 'где', 'адрес'],
     
    }
    
    for key, values in synonyms.items():
        if any(word in key_phrase for word in values):
            pattern = '|'.join(values)
            break
    else:
        pattern = re.escape(key_phrase)  

    pattern = r'\b(' + pattern + r')\s*[:\-]?\s*([\w\s\-\/]+)'
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(2).strip()
    return "Ответ не найден."


def load_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("Image files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        extension = file_path.split('.')[-1].lower()
        if extension in ['jpg', 'jpeg', 'png']:
            text = extract_text_from_image(file_path)
        elif extension == 'pdf':
            text = extract_text_from_pdf(file_path)
        else:
            messagebox.showerror("Unsupported file", "This file type is not supported")
            return
        text_output.delete('1.0', tk.END)
        text_output.insert(tk.END, text)

def query():
    question = question_entry.get()
    text = text_output.get("1.0", tk.END)
    answer = find_answer_in_text(text, question)
    answer_output.delete('1.0', tk.END)
    answer_output.insert(tk.END, answer)


root = tk.Tk()
root.title("Document Query System")

load_button = tk.Button(root, text="Load Document", command=load_file)
load_button.pack(pady=20)

question_label = tk.Label(root, text="Enter your question:")
question_label.pack()

question_entry = tk.Entry(root, width=50)
question_entry.pack()

query_button = tk.Button(root, text="Submit Query", command=query)
query_button.pack(pady=10)

answer_label = tk.Label(root, text="Answer:")
answer_label.pack()

answer_output = tk.Text(root, height=1, width=50)
answer_output.pack(pady=20)

text_output = tk.Text(root, height=10, width=50)  
text_output.pack(pady=20)

root.mainloop()
