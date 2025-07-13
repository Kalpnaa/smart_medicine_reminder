# smart_medicine_reminder/app.py

import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import sys

# Add the project root to the sys.path to allow imports from subdirectories
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import functions from your existing modules
# We need preprocess_image_for_ocr, extract_text_from_processed_image,
# clean_extracted_text, extract_medicine_info from the ocr/nlp pipeline
# and create_table, add_medicine_record from db/database_manager.py
from ocr.image_processor import preprocess_image_for_ocr, extract_text_from_processed_image, clean_extracted_text
from nlp.medicine_extractor import extract_medicine_info # This is the specific NLP logic
from db.database_manager import create_table, add_medicine_record

app = Flask(__name__)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = os.path.join(current_dir, 'uploads') # Create an 'uploads' folder in the root
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Renders the main page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handles image upload and processes it."""
    if 'prescription_image' not in request.files:
        return render_template('index.html', error_message='No file part in the request.')
    
    file = request.files['prescription_image']
    
    if file.filename == '':
        return render_template('index.html', error_message='No selected file.')
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # --- Integrate your existing image processing and NLP pipeline ---
        create_table() # Ensure DB table exists

        processed_img_cv = preprocess_image_for_ocr(filepath)
        if processed_img_cv is None:
            return render_template('index.html', error_message='Image preprocessing failed.')
        
        raw_extracted_text = extract_text_from_processed_image(processed_img_cv)
        if raw_extracted_text is None or not raw_extracted_text.strip():
            return render_template('index.html', error_message='Text extraction (OCR) failed or returned empty text.')
        
        # Pass raw_extracted_text to the NLP extractor as discussed
        medicine_details = extract_medicine_info(raw_extracted_text)

        # Check if medicine_name was successfully extracted before saving
        if medicine_details.get('medicine_name') is None or not medicine_details.get('medicine_name').strip():
            return render_template('index.html', error_message='Could not extract medicine name from the image. Please try another image.')
        
        # Save to database
        success = add_medicine_record(medicine_details)

        # Clean up the uploaded image file after processing (optional but good practice)
        os.remove(filepath)

        if success:
            return render_template('index.html', 
                                   medicine_name=medicine_details.get('medicine_name'),
                                   dosage=medicine_details.get('dosage'),
                                   frequency=medicine_details.get('frequency'),
                                   duration=medicine_details.get('duration'))
        else:
            return render_template('index.html', error_message='Failed to save medicine details to database.')
    else:
        return render_template('index.html', error_message='File type not allowed. Please upload an image (png, jpg, jpeg, gif).')

if __name__ == '__main__':
    # For development: Run the Flask app
    # In a production environment, you would use a production-ready WSGI server like Gunicorn or uWSGI
    app.run(debug=True) # debug=True allows hot-reloading and better error messages