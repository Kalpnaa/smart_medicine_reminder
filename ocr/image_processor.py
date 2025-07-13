import sys
import os

# --- IMPORTANT: START OF WORKAROUND FOR IMPORT ERROR ---
# Get the directory of the current script (image_processor.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Go up one level from 'ocr' to reach the project root ('smart_medicine_reminder')
project_root = os.path.join(current_dir, '..')

# Add the project root to Python's search path for modules
sys.path.append(project_root)
# --- IMPORTANT: END OF WORKAROUND FOR IMPORT ERROR ---


from PIL import Image
import pytesseract
import cv2
import numpy as np
import re

# Import our new medicine extraction function
from nlp.medicine_extractor import extract_medicine_info

# Import our database functions
from db.database_manager import create_table, add_medicine_record


# --- IMPORTANT CONFIGURATION ---
# On Windows, you might need to specify the path to the Tesseract executable.
# Find your tesseract.exe path (e.g., C:\Program Files\Tesseract-OCR\tesseract.exe)
# Uncomment the line below and replace with your actual path:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# -------------------------------


def preprocess_image_for_ocr(image_path: str) -> np.ndarray | None:
    """
    Loads an image, converts it to grayscale, and then applies adaptive thresholding
    to enhance text for OCR.
    """
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at '{image_path}'")
        return None

    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Could not load image from '{image_path}'. Check path and image integrity.")
            return None
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        processed_img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                              cv2.THRESH_BINARY, 11, 2)
        return processed_img
    except Exception as e:
        print(f"An error occurred during image preprocessing: {e}")
        return None

def extract_text_from_processed_image(processed_img: np.ndarray) -> str | None:
    """
    Extracts text from a preprocessed (OpenCV) image using Tesseract OCR.
    """
    try:
        pil_img = Image.fromarray(processed_img)
        text = pytesseract.image_to_string(pil_img)
        return text.strip()
    except pytesseract.TesseractNotFoundError:
        print("Error: Tesseract OCR engine is not found.")
        print("Please ensure Tesseract is installed and its executable is in your system PATH,")
        print("or set 'pytesseract.pytesseract.tesseract_cmd' to its full path.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during OCR: {e}")
        return None

def clean_extracted_text(text: str) -> str:
    """
    Performs basic cleaning on the extracted text.
    - Converts to lowercase.
    - Removes non-alphanumeric characters (except whitespace).
    - Replaces multiple spaces with a single space.
    - Strips leading/trailing whitespace.
    """
    text = text.lower()
    # Remove all characters that are not letters, numbers, or whitespace
    text = re.sub(r'[^a-z0-9\s]', '', text)
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


if __name__ == "__main__":
    # Define the path to the sample image.
    # '..' goes up one directory from 'ocr' to 'smart_medicine_reminder',
    # then into 'data_samples'
    sample_image_path = os.path.join("..", "data_samples", "sample_prescription_text.png")

    print(f"Attempting to preprocess, extract, and clean text from: {sample_image_path}")

    # First, ensure the database table is created/checked when the script runs
    create_table()

    # Step 1: Preprocess the image for better OCR results
    preprocessed_img_cv = preprocess_image_for_ocr(sample_image_path)

    if preprocessed_img_cv is not None:
        # Optional: Save the preprocessed image to see its effect (for debugging/visualization)
        output_path = os.path.join("..", "data_samples", "processed_sample_image.png")
        cv2.imwrite(output_path, preprocessed_img_cv)
        print(f"Preprocessed image saved to: {output_path}")

        # Step 2: Extract raw text from the preprocessed image using Tesseract OCR
        raw_extracted_text = extract_text_from_processed_image(preprocessed_img_cv)

        if raw_extracted_text:
            print("\n--- Raw Extracted Text ---")
            print(raw_extracted_text)
            print("--------------------------")

            # Step 3: Clean the extracted text
            cleaned_text = clean_extracted_text(raw_extracted_text)

            print("\n--- Cleaned Text ---")
            print(cleaned_text)
            print("--------------------")
            
            # Step 4: Extract structured medicine information using our NLP module
            # THIS IS THE FIX: Pass raw_extracted_text to the extractor
            print("\n--- Extracted Medicine Info (NLP) ---")
            medicine_details = extract_medicine_info(raw_extracted_text) # <--- CRUCIAL CHANGE HERE
            for key, value in medicine_details.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
            print("-----------------------------------")

            # Step 5: Add the extracted medicine details to the database!
            print("\n--- Saving to Database ---")
            # Only attempt to add record if medicine_name was successfully extracted (not None)
            if medicine_details.get('medicine_name') is not None:
                add_medicine_record(medicine_details)
            else:
                print("Skipping database entry: Medicine Name could not be extracted (it was 'None').")


        else:
            print("\nFailed to extract text after preprocessing.")
    else:
        print("Image preprocessing failed. Cannot proceed with text extraction.")