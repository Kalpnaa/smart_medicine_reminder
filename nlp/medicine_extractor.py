import re

def get_first_match(text, pattern):
    """
    Finds the first match for a regex pattern in text.
    Prioritizes the first capturing group if it exists, otherwise returns the full match.
    Uses re.IGNORECASE for case-insensitive matching.
    """
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        # If there's a capturing group, return its content (e.g., for "Dose: (546 mg)")
        # Otherwise, return the entire matched string.
        return match.group(1) if len(match.groups()) > 0 else match.group(0)
    return "Unknown"

def extract_medicine_info(text: str) -> dict:
    """
    Extracts medicine information (name, dosage, frequency, duration) from cleaned text.
    """
    # Regex patterns (adjusted for robustness, assuming cleaned text structure)
    # The patterns are designed to capture the content *after* the label.
    medicine_name_pattern = r"Medicine:\s*(.+)"
    dosage_pattern = r"Dose:\s*(\d+\s*mg)" # Specific for numbers + 'mg'
    frequency_pattern = r"Frequency:\s*(.+)"
    
    # Duration pattern: captures the number and unit (e.g., "7 days")
    # The (?:...) is a non-capturing group for 'for' or 'duration' keywords
    duration_pattern = r"Duration:\s*(?:for|duration)?\s*(\d+\s*(?:day|week|month|year)s?)"


    medicine_info = {
        "medicine_name": get_first_match(text, medicine_name_pattern),
        "dosage": get_first_match(text, dosage_pattern),
        "frequency": get_first_match(text, frequency_pattern),
        "duration": get_first_match(text, duration_pattern)
    }

    # Post-process duration to remove "duration" or "for" prefix if it slipped through
    # This handles cases where OCR might combine the keyword with the value.
    if medicine_info["duration"].lower().startswith("duration "):
        medicine_info["duration"] = medicine_info["duration"][len("duration "):].strip()
    elif medicine_info["duration"].lower().startswith("for "):
        medicine_info["duration"] = medicine_info["duration"][len("for "):].strip()
    
    # For very generic "Unknown" or empty results, sometimes setting to None is better for DB
    for key, value in medicine_info.items():
        if value == "Unknown" or not value.strip():
            medicine_info[key] = None

    return medicine_info

if __name__ == "__main__":
    # Test cases for extract_medicine_info
    print("Running medicine_extractor tests...")

    sample_cleaned_text_1 = "Medicine: Paracetamol Dose: 500 mg Frequency: Twice a day Duration: 7 days"
    info1 = extract_medicine_info(sample_cleaned_text_1)
    print(f"\nExtracted Info 1: {info1}")
    # Expected: {'medicine_name': 'Paracetamol', 'dosage': '500 mg', 'frequency': 'Twice a day', 'duration': '7 days'}

    sample_cleaned_text_2 = "Medicine: Amoxicillin Dose: 250mg Frequency: every 8 hours Duration: for 10 days"
    info2 = extract_medicine_info(sample_cleaned_text_2)
    print(f"\nExtracted Info 2: {info2}")
    # Expected: {'medicine_name': 'Amoxicillin', 'dosage': '250mg', 'frequency': 'every 8 hours', 'duration': '10 days'}

    sample_cleaned_text_3 = "Medicine: Vitamin C Dose: 1 tablet Frequency: once daily Duration: duration 3 weeks"
    info3 = extract_medicine_info(sample_cleaned_text_3)
    print(f"\nExtracted Info 3: {info3}")
    # Expected: {'medicine_name': 'Vitamin C', 'dosage': '1 tablet', 'frequency': 'once daily', 'duration': '3 weeks'}

    sample_cleaned_text_4 = "Medicine: Ibuprofen Dose: 400 mg Frequency: As needed"
    info4 = extract_medicine_info(sample_cleaned_text_4)
    print(f"\nExtracted Info 4: {info4}")
    # Expected: {'medicine_name': 'Ibuprofen', 'dosage': '400 mg', 'frequency': 'As needed', 'duration': 'Unknown'} # or None