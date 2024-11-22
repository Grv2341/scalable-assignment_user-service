import sqlite3
import os

# Path to the SQLite database file
DB_PATH = 'users.db'  # Replace with the actual path to your SQLite database

def get_all_users():
    """Fetch all users from the SQLite database."""
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Query to select all users
        cursor.execute("SELECT * FROM users")

        # Fetch all rows from the result of the query
        users = cursor.fetchall()

        # Close the connection to the database
        conn.close()

        return users
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"General error: {e}")
        return None

if __name__ == "__main__":
    users = get_all_users()
    if users:
        print("Fetched users:")
        for user in users:
            print(user)  # Print each user, you can modify this based on your user table structure
    else:
        print("No users found or failed to fetch users.")