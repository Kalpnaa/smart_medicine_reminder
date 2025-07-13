import sqlite3
import os
import datetime
import re

# Define the path to your database file
# It will be created in the 'smart_medicine_reminder' root directory
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'medicine_reminder.db')

def parse_frequency_to_timedelta(frequency_str: str) -> datetime.timedelta:
    """
    Parses a frequency string and returns a datetime.timedelta object.
    Handles common patterns like 'once daily', 'twice a day', 'every X hours/days'.
    Returns 24 hours (1 day) by default if pattern is not recognized.
    """
    freq = frequency_str.lower().strip()

    # 1. Prioritize specific 'daily' phrases before general 'daily'
    if 'twice daily' in freq:
        return datetime.timedelta(hours=12)
    if 'thrice daily' in freq:
        return datetime.timedelta(hours=8)
    if 'once daily' in freq: # Keep this specific 'once daily' check
        return datetime.timedelta(days=1)
    if 'four times a day' in freq: # Keep this specific one if it's common
        return datetime.timedelta(hours=6)

    # 2. Pattern for "every X hours" or "every X days"
    match_every_x = re.search(r'every\s*(\d+)\s*(hour|day)s?', freq)
    if match_every_x:
        value = int(match_every_x.group(1))
        unit = match_every_x.group(2)
        if unit == 'hour':
            return datetime.timedelta(hours=value)
        elif unit == 'day':
            return datetime.timedelta(days=value)

    # 3. Pattern for "X times a day" (e.g., "twice a day", "3 times a day")
    # This also catches "once a day", "twice a day", "thrice a day" which is fine here.
    match_times_a_day = re.search(r'(\d+|once|twice|thrice)\s*(?:time|times)?\s*a\s*day', freq)
    if match_times_a_day:
        count_str = match_times_a_day.group(1)
        if count_str == 'once': count = 1
        elif count_str == 'twice': count = 2
        elif count_str == 'thrice': count = 3
        else:
            try: count = int(count_str)
            except ValueError: count = 0

        if count > 0:
            return datetime.timedelta(hours=24 / count)
        else:
            return datetime.timedelta(days=1)

    # 4. General catch-all for 'daily' if not caught by more specific 'daily' phrases above
    if 'daily' in freq or 'every day' in freq:
        return datetime.timedelta(days=1)

    # Default if no specific pattern is found
    print(f"Warning: Could not parse frequency '{frequency_str}'. Defaulting to 24 hours interval.")
    return datetime.timedelta(days=1)


def connect_db():
    """Establishes a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def create_table():
    """Creates the 'medicines' table if it doesn't already exist."""
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS medicines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    medicine_name TEXT NOT NULL,
                    dosage TEXT,
                    frequency TEXT,
                    duration TEXT,
                    start_date TEXT, -- YYYY-MM-DD
                    last_taken TEXT,  -- YYYY-MM-DD HH:MM:SS
                    next_due TEXT    -- YYYY-MM-DD HH:MM:SS
                );
            ''')
            conn.commit()
            print("Table 'medicines' checked/created successfully.")
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")
        finally:
            conn.close()

def add_medicine_record(medicine_info: dict):
    """
    Adds a new medicine record to the database.
    Assumes medicine_info dict contains 'medicine_name', 'dosage', 'frequency', 'duration'.
    Sets start_date to now and calculates an initial next_due time based on frequency.
    """
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()

            current_time = datetime.datetime.now()
            
            # --- START OF CHANGE ---
            # Ensure frequency is always a string before parsing
            freq_str_from_info = medicine_info.get('frequency')
            if freq_str_from_info is None or not str(freq_str_from_info).strip():
                # Provide a sensible default if frequency is missing or empty
                actual_frequency_to_parse = 'once daily'
                print(f"Warning: Frequency not found or empty for '{medicine_info.get('medicine_name', 'Unknown medicine')}', defaulting to '{actual_frequency_to_parse}'.")
            else:
                actual_frequency_to_parse = freq_str_from_info
            # --- END OF CHANGE ---

            interval = parse_frequency_to_timedelta(actual_frequency_to_parse)
            initial_next_due = (current_time + interval).strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute('''
                INSERT INTO medicines (medicine_name, dosage, frequency, duration, start_date, next_due)
                VALUES (?, ?, ?, ?, DATE('now'), ?)
            ''', (
                medicine_info.get('medicine_name', 'Unknown'),
                medicine_info.get('dosage', 'Unknown'),
                medicine_info.get('frequency', 'Unknown'), # Store original frequency, even if None, or the defaulted one
                medicine_info.get('duration', 'Unknown'),
                initial_next_due
            ))
            conn.commit()
            print(f"Medicine '{medicine_info.get('medicine_name', 'Unknown')}' added to database with next due: {initial_next_due}.")
            return True
        except sqlite3.Error as e:
            print(f"Error adding medicine record: {e}")
            return False
        finally:
            conn.close()

def update_medicine_taken(medicine_id: int, frequency: str):
    """
    Updates the last_taken time and calculates the next_due time for a medicine
    based on its frequency.
    """
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            now = datetime.datetime.now()
            last_taken_time = now.strftime('%Y-%m-%d %H:%M:%S')

            # --- START OF CHANGE ---
            # Ensure frequency is always a string before parsing
            if frequency is None or not str(frequency).strip(): # Cast to str just in case
                 actual_frequency_to_parse = 'once daily'
                 print(f"Warning: Frequency input was empty or invalid for medicine ID {medicine_id}, defaulting to '{actual_frequency_to_parse}'.")
            else:
                 actual_frequency_to_parse = frequency
            # --- END OF CHANGE ---

            interval = parse_frequency_to_timedelta(actual_frequency_to_parse)
            next_due_time = (now + interval).strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute('''
                UPDATE medicines
                SET last_taken = ?,
                    next_due = ?
                WHERE id = ?;
            ''', (last_taken_time, next_due_time, medicine_id))
            conn.commit()
            print(f"Medicine ID {medicine_id} updated: Last taken {last_taken_time}, Next due {next_due_time}.")
            return True
        except sqlite3.Error as e:
            print(f"Error updating medicine record: {e}")
            return False
        finally:
            conn.close()

def get_all_medicines():
    """Retrieves all medicine records from the database."""
    conn = connect_db()
    medicines = []
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM medicines;')
            medicines = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving medicines: {e}")
        finally:
            conn.close()
    return medicines

def get_medicines_due_soon(minutes_threshold: int = 5):
    """
    Retrieves medicines that are due within the next 'minutes_threshold' minutes.
    """
    conn = connect_db()
    medicines_due = []
    if conn:
        try:
            cursor = conn.cursor()
            now = datetime.datetime.now()
            # Calculate the future time up to the threshold
            time_threshold = (now + datetime.timedelta(minutes=minutes_threshold)).strftime('%Y-%m-%d %H:%M:%S')
            current_time_str = now.strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute('''
                SELECT id, medicine_name, dosage, frequency, next_due
                FROM medicines
                WHERE next_due <= ? AND next_due >= ?;
            ''', (time_threshold, current_time_str)) # next_due is between now and threshold
            medicines_due = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving medicines due soon: {e}")
        finally:
            conn.close()
    return medicines_due


if __name__ == "__main__":
    print("Running database manager tests with new frequency parsing...")
    create_table()

    # Test cases for frequency parsing
    frequencies_to_test = [
        "once daily", "daily", "every day",
        "twice a day", "twice daily",
        "thrice a day", "thrice daily",
        "4 times a day",
        "every 8 hours", "every 2 days", "every 12 hours"
    ]
    print("\n--- Testing Frequency Parsing ---")
    for freq_str in frequencies_to_test:
        interval = parse_frequency_to_timedelta(freq_str)
        print(f"'{freq_str}' parses to: {interval}")


    # Example of adding a record (this will now set initial next_due based on frequency)
    print("\n--- Adding Test Records ---")
    test_medicine_info_a = {
        "medicine_name": "Paracetamol",
        "dosage": "500mg",
        "frequency": "twice a day", # Test this frequency
        "duration": "7 days"
    }
    add_medicine_record(test_medicine_info_a)

    test_medicine_info_b = {
        "medicine_name": "Amoxicillin",
        "dosage": "250mg",
        "frequency": "every 8 hours", # Test this frequency
        "duration": "10 days"
    }
    add_medicine_record(test_medicine_info_b)

    test_medicine_info_c = {
        "medicine_name": "Vitamin D",
        "dosage": "1 tablet",
        "frequency": "once daily", # Test this frequency
        "duration": "30 days"
    }
    add_medicine_record(test_medicine_info_c)


    print("\n--- All medicines in database after adding ---")
    all_meds = get_all_medicines()
    for med in all_meds:
        print(med)

    # Test retrieving medicines due soon (adjust minutes_threshold for testing)
    # Note: If you run this immediately, newly added medicines might not be "due soon"
    # based on their calculated next_due unless the interval is very short.
    print(f"\n--- Medicines due in next 5 minutes (as of {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")
    due_meds = get_medicines_due_soon(minutes_threshold=5)
    if due_meds:
        for med in due_meds:
            print(med)
    else:
        print("No medicines due soon (within 5 minutes).")

    # Example of updating a record (replace the ID with one from your database, e.g., the last one added)
    # After a few minutes, run this again and you should see the reminder trigger.
    # update_medicine_taken(1, "once daily")
    # print("\nAll medicines after update:")
    # all_meds_after_update = get_all_medicines()
    # for med in all_meds_after_update:
    #     print(med)