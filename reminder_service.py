import time
import datetime
from db.database_manager import get_medicines_due_soon, update_medicine_taken

def send_notification(medicine_name: str, dosage: str, frequency: str):
    """
    Placeholder function to simulate sending a notification.
    In a real application, this could be a pop-up, sound, email, etc.
    """
    print(f"\n--- REMINDER! ---")
    print(f"Time to take: {medicine_name}")
    print(f"Dosage: {dosage}")
    print(f"Frequency: {frequency}")
    print(f"Don't forget your medicine!")
    print(f"-----------------\n")

def reminder_loop():
    """
    Main loop that continuously checks for medicines due and triggers reminders.
    """
    print("Starting Reminder Service... (Press Ctrl+C to stop)")
    while True:
        try:
            # Get medicines that are due in the next 1 minute (adjust threshold as needed)
            # The 'get_medicines_due_soon' function retrieves items where next_due is <= now + threshold
            medicines_due = get_medicines_due_soon(minutes_threshold=1)

            if medicines_due:
                print(f"Checking for due medicines at {datetime.datetime.now().strftime('%H:%M:%S')}")
                for med in medicines_due:
                    med_id, name, dosage, frequency, next_due = med
                    print(f"ALERT! Medicine '{name}' ({dosage}) is due NOW!")
                    send_notification(name, dosage, frequency)

                    # --- IMPORTANT: Simulating taking medicine and updating ---
                    # In a real app, this would be triggered by user action (e.g., clicking 'taken' button)
                    # For now, we'll auto-update it to test the loop and rescheduling.
                    print(f"Simulating 'taking' {name}... Rescheduling next dose.")
                    update_medicine_taken(med_id, frequency) # Frequency is passed but not fully used yet
                    # ---------------------------------------------------------

            # Sleep for a short period before checking again (e.g., every 30 seconds)
            time.sleep(30)

        except KeyboardInterrupt:
            print("\nReminder Service stopped by user.")
            break
        except Exception as e:
            print(f"An error occurred in reminder loop: {e}")
            time.sleep(60) # Wait longer if an error occurs

if __name__ == "__main__":
    reminder_loop()