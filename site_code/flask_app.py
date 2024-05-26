from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
import fitz
from functions import load_pdfs_for_user, update_pdf_database, split_text, change_index, convert_pdf_to_images, extract_text_from_pdf, extract_text_from_pdf_by_ocr
from pdf_manager import init_db

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Initialize the database
init_db()

# Ensure the necessary directories are created
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def home():
    if 'name' in session:
        return redirect(url_for('user_dashboard'))
    else:
        return redirect(url_for("signup"))

@app.route('/signup')
def signup():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    session['name'] = request.form['name']
    if 'pdfs' not in session:
        session['pdfs'] = []
    return redirect(url_for('user_dashboard'))

@app.route('/dashboard')
def user_dashboard():
    if 'name' in session:
        name = session['name']
        load_pdfs_for_user(session)
        return render_template('dashboard.html', name=name, pdfs=session['pdfs'])
    return redirect(url_for('home'))

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' in request.files:
        file = request.files['file']
        if file.filename:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            update_pdf_database(session['name'], filename, '0', file.mode)
            flash('File uploaded successfully.')
            return redirect(url_for('user_dashboard'))
    return redirect(url_for("home"))

@app.route('/pdf_reader/<pdf_name>/<oindex>/<mode>')
def play_pdf(pdf_name, oindex, mode):
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_name)
    text = extract_text_from_pdf(pdf_path)
    result_array = split_text(text)

    return render_template('pdf_reader.html', pdf_name=pdf_name, content=result_array, oindex=oindex, b=0)

@app.route('/play/<pdf_name>/<index>/<mode>')
def play2_pdf(pdf_name, index, mode):
    try:
        index_int = int(index.split('-')[1])
    except (IndexError, ValueError):
        flash("Invalid index format.")
        return redirect(url_for('user_dashboard'))

    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_name)
    text = extract_text_from_pdf(pdf_path)
    result_array = split_text(text)

    #new version
    doc = fitz.open(pdf_path)
    images = convert_pdf_to_images(doc)

    return render_template('play.html', pdf_name=pdf_name, content=result_array, index_far=index_int, images=images)

@app.route('/update_index', methods=['POST'])
def update_index():
    try:
        data = request.json
        pdf_name = data.get('pdfName')
        new_index = data.get('index')

        if pdf_name is None or new_index is None:
            return jsonify({"error": "Invalid input data"}), 400
        change_index(pdf_name, new_index)
        return jsonify({"message": "Index updated"}), 200
    except Exception as e:
        print(f"Error updating index: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run()
