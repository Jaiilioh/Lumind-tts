from flask import Flask, request, render_template, send_file, redirect, url_for
import os
from werkzeug.utils import secure_filename
from gtts import gTTS
import PyPDF2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['AUDIO_FOLDER'] = os.path.join('static', 'audio')
ALLOWED_EXTENSIONS = {'txt', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Extract text based on file type
            if filename.lower().endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()

            # Convert text to speech using gTTS
            tts = gTTS(text=text, lang='en', slow=False)
            audio_filename = filename.rsplit('.', 1)[0] + '.mp3'
            audio_path = os.path.join(app.config['AUDIO_FOLDER'], audio_filename)
            tts.save(audio_path)

            return render_template('result.html', audio_file=audio_filename)

    return render_template('index.html')

@app.route('/audio/<filename>')
def audio(filename):
    return send_file(os.path.join(app.config['AUDIO_FOLDER'], filename), as_attachment=True)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['AUDIO_FOLDER'], exist_ok=True)
    app.run(debug=True)
