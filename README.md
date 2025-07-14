# Smart Medicine Reminder System

## Project Overview

The Smart Medicine Reminder System is a Python-based application designed to help users manage their medication schedule. It utilizes:

- **Optical Character Recognition (OCR)** to extract medicine details from prescription images.
- **Natural Language Processing (NLP)** to parse extracted text.
- **Flask Web Interface** for easy interaction.
- **Background Service** that continuously monitors due medicines and triggers reminders.

---

## Features

- **Image-based Prescription Input:** Upload prescription images (PNG, JPG, JPEG, GIF).
- **OCR Text Extraction:** Extracts text from prescription images using Tesseract OCR.
- **NLP Information Extraction:** Parses medicine name, dosage, frequency, and duration.
- **Database Management:** Stores and manages medicine records in a local SQLite database.
- **Web-based GUI:** Built with Flask, HTML, and CSS.
- **Automated Reminders:** Background service provides alerts (currently console output).
- **Automatic Rescheduling:** Updates medicine’s next due time after a reminder.

---

## Technologies Used

- Python 3.x
- Flask
- OpenCV (cv2)
- Pytesseract
- Tesseract OCR
- SQLite3
- HTML, CSS

---

## Project Structure

```plaintext
smart_medicine_reminder/
├── app.py                    # Main Flask web application
├── reminder_service.py       # Background service for reminders
├── medicine_reminder.db      # SQLite database file
├── README.md                 # Project documentation

├── db/                       # Database management scripts
│   ├── database_manager.py
│   └── update_due_time.py    # Utility for testing due time updates

├── nlp/                      # NLP information extraction
│   └── medicine_extractor.py

├── ocr/                      # OCR image processing
│   └── image_processor.py

├── static/                   # Static files (CSS, JS, images)
│   └── style.css

├── templates/                # HTML templates for Flask
│   └── index.html

├── uploads/                  # Temporary folder for uploaded images
├── venv/                     # Python Virtual Environment (not version-controlled)
```
Setup and Installation
1. Install Git
Download from: https://git-scm.com

2. Clone the Repository
bash
Copy
Edit
git clone https://github.com/YOUR_GITHUB_USERNAME/smart_medicine_reminder.git
cd smart_medicine_reminder
3. Set Up a Python Virtual Environment
bash
Copy
Edit
python -m venv venv
Activate:

Windows (PowerShell):

bash
Copy
Edit
.\venv\Scripts\Activate.ps1
Windows (CMD):

bash
Copy
Edit
venv\Scripts\activate.bat
macOS/Linux:

bash
Copy
Edit
source venv/bin/activate
4. Install Python Dependencies
bash
Copy
Edit
pip install Flask opencv-python pytesseract numpy Werkzeug
5. Install Tesseract OCR Engine
Windows:
Download from: Tesseract Releases

During installation, check "Add to PATH".

If needed, set the Tesseract path in ocr/image_processor.py and app.py:

python
Copy
Edit
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
macOS (Homebrew):
bash
Copy
Edit
brew install tesseract
Linux (Debian/Ubuntu):
bash
Copy
Edit
sudo apt update
sudo apt install tesseract-ocr
Verify installation:

bash
Copy
Edit
tesseract --version
6. Create Necessary Folders
bash
Copy
Edit
mkdir uploads
(The static/ and templates/ folders should already exist.)

7. Database Initialization
The SQLite database (medicine_reminder.db) is created automatically when running app.py or image_processor.py for the first time.

Usage
1. Run the Flask Web Interface
In your project root:

bash
Copy
Edit
source venv/bin/activate  # Or equivalent for your OS
python app.py
Open your browser and go to:

http://127.0.0.1:5000

Use the form to upload a prescription image.

2. Run the Reminder Service
In a separate terminal:

bash
Copy
Edit
source venv/bin/activate
python reminder_service.py
When a medicine’s next due time arrives, reminders will print in this terminal.

To stop: Press Ctrl + C

Testing Reminders Immediately (For Development)
Stop reminder_service.py (if running).

Update the medicine due time:

bash
Copy
Edit
cd db
python update_due_time.py
cd ..
Restart the reminder service:

bash
Copy
Edit
python reminder_service.py
You should see a reminder within about a minute.

Future Enhancements (Ideas)
System Notifications using packages like plyer.

User Authentication.

Medicine Management GUI (edit/delete records via web).

Advanced Scheduling: e.g., "every 3 hours", "Mondays and Fridays".

Mobile App Integration.

Cloud Deployment (Heroku, AWS, Azure, etc.).

Logging System for debugging and monitoring.

Credits and Acknowledgements
This project was developed with assistance from AI language models and tools like Google Gemini for coding guidance, debugging, and problem-solving.