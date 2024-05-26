import re
import fitz  # PyMuPDF
import openai
from PIL import Image
import base64
import io
import pytesseract
import sqlite3

# OpenAI API 키 설정
openai.api_key = ''


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def load_pdfs_for_user(session):
    conn = get_db_connection()
    user_pdfs = conn.execute('SELECT pdf_name, progress, mode FROM pdfs WHERE user_name = ?', (session['name'],)).fetchall()
    conn.close()
    session['pdfs'] = [{'name': row['pdf_name'], 'progress': row['progress'], 'mode': row['mode']} for row in user_pdfs]
    session.modified = True

def update_pdf_database(name, pdf_name, progress, mode):
    conn = get_db_connection()
    conn.execute('INSERT INTO pdfs (user_name, pdf_name, progress, mode) VALUES (?, ?, ?, ?)', (name, pdf_name, progress, mode))
    conn.commit()
    conn.close()

def split_text(text):
    parts = re.split(r'[\s“”‘’]+|(\([^)]*\))', text)
    parts = [part for part in parts if part]
    return parts

def change_index(p_name, new_index):
    conn = get_db_connection()
    conn.execute('UPDATE pdfs SET progress = ? WHERE pdf_name = ?', (new_index, p_name))
    conn.commit()
    conn.close()

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ''
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def process_text_with_gpt(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "사용자에게 내용을 받으면 띄어쓰기를 고치고 문장단위로 줄바꿈을 해서 다시 줘\n 그리고 이게 논문 의 글자를 다 따온건데 출처 팩스 번호 출처등 내용과 관련없는 내용은 지우고 문맥에 맞는 내용만 남겨줘"},
            {"role": "user", "content": text}
        ]
    )
    return response['choices'][0]['message']['content']

def save_text_to_file(text, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)

def processing_gpt(pdf_path, output_file_path):
    text = extract_text_from_pdf(pdf_path)
    processed_text = ''

    # 1500자씩 끊어서 처리
    chunk_size = 1500
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        processed_chunk = process_text_with_gpt(chunk)
        processed_text += processed_chunk + '\n'

    save_text_to_file(processed_text, output_file_path)
    print(f"Processed text saved to {output_file_path}")

# 예시 사용법
pdf_path = 'path/to/your/pdf/file.pdf'  # PDF 파일 경로를 여기에 입력
output_file_path = 'output.txt'  # 출력 텍스트 파일 경로를 여기에 입력
processing_gpt(pdf_path, output_file_path)





































def convert_pdf_to_images(pdf_document):
    images = []
    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        pix = page.get_pixmap()
        img = io.BytesIO(pix.tobytes("png"))
        img.seek(0)
        images.append(base64.b64encode(img.getvalue()).decode('utf-8'))
    return images
def extract_text_from_pdf_by_ocr(pdf_path):
    zoom_x = 3.0
    zoom_y = 3.0
    mat = fitz.Matrix(zoom_x, zoom_y)
    doc = fitz.open(pdf_path)
    text = ''
    page = doc[0]
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    text += pytesseract.image_to_string(img, lang='kor+eng')
    doc.close()
    return text
