import sqlite3
import datetime
import os

# Define the path to your database file
# This path now correctly points to the 'medicine_reminder.db' in the project root
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'medicine_reminder.db')

def connect_db():
    """Establishes a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def update_next_due_for_latest_medicine(minutes_from_now: int = 1):
    """
    Updates the 'next_due' time for the most recently added medicine record
    to 'minutes_from_now' minutes in the future.
    """
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()

            # Find the ID of the last inserted medicine
            # We order by ID in descending order and take the first one
            cursor.execute("SELECT id, medicine_name, next_due FROM medicines ORDER BY id DESC LIMIT 1;")
            result = cursor.fetchone()

            if not result:
                print("No medicine records found in the database. Please add one first using image_processor.py.")
                return False

            medicine_id, medicine_name, old_next_due = result

            # Calculate the new next_due time: now + specified minutes
            new_due_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes_from_now)
            new_due_time_str = new_due_time.strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute('''
                UPDATE medicines
                SET next_due = ?
                WHERE id = ?;
            ''', (new_due_time_str, medicine_id))
            conn.commit()
            print(f"Successfully updated 'next_due' for medicine '{medicine_name}' (ID: {medicine_id})")
            print(f"Old next_due: {old_next_due}")
            print(f"New next_due: {new_due_time_str}")
            return True
        except sqlite3.Error as e:
            print(f"Error updating next_due time: {e}")
            return False
        finally:
            conn.close()

if __name__ == "__main__":
    print("Attempting to update the next due time for the latest medicine record...")
    # Set the next due time to 1 minute from now for immediate testing
    update_next_due_for_latest_medicine(minutes_from_now=1)
    print("\nAfter update, please restart reminder_service.py to check for immediate reminders.")