import sqlite3
import os
import uuid
from werkzeug.security import check_password_hash

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')

def init_db():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            pan_card TEXT UNIQUE NOT NULL,
            dob DATE NOT NULL,
            account_status TEXT DEFAULT 'ACTIVE' CHECK(account_status IN ('ACTIVE', 'DISABLED')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create wallets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wallets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wallet_id TEXT UNIQUE NOT NULL,
            user_id TEXT NOT NULL,
            balance REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')
    connection.commit()
    connection.close()

def add_user_db(name, email, hashed_password, pan_card, dob):
    user_id = str(uuid.uuid4())
    wallet_id = str(uuid.uuid4())
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        cursor.execute('''
            INSERT INTO users (user_id, name, email, password, pan_card, dob)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, name, email, hashed_password, pan_card, dob))

        cursor.execute('''
            INSERT INTO wallets (wallet_id, user_id, balance)
            VALUES (?, ?, ?)
        ''', (wallet_id, user_id, 0.0))

        connection.commit()
        connection.close()

        return {
            "status": "success",
            "message": "User and wallet successfully created.",
            "user_id": user_id,
            "wallet_id": wallet_id
        }

    except sqlite3.IntegrityError as e:
        return {"status": "error", "message": f"Database error: {str(e)}"}

def authenticate_user(email, password):

    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        # Fetch user details
        cursor.execute('SELECT user_id, password FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        connection.close()

        if user:
            user_id, hashed_password = user
            # Verify password
            if check_password_hash(hashed_password, password):
                return {"status": "success", "user_id": user_id}
            else:
                return {"status": "error", "message": "Invalid password"}
        else:
            return {"status": "error", "message": "User not found"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_wallet_balance(user_id):

    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        # Query the wallet balance
        cursor.execute('''
            SELECT balance FROM wallets WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        connection.close()

        if result:
            return {"status": "success", "balance": result[0]}
        else:
            return {"status": "error", "message": "Wallet not found for the provided user_id"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def handle_transaction(user_id, transaction_type, amount):

    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()

        # Validate user account status
        cursor.execute('''
            SELECT account_status FROM users WHERE user_id = ?
        ''', (user_id,))
        user = cursor.fetchone()
        if not user:
            return {"status": "error", "message": "User not found"}
        if user[0] == "DISABLED":
            return {"status": "error", "message": "Account is disabled"}

        # Get current wallet balance
        cursor.execute('''
            SELECT balance FROM wallets WHERE user_id = ?
        ''', (user_id,))
        wallet = cursor.fetchone()
        if not wallet:
            return {"status": "error", "message": "Wallet not found"}
        
        current_balance = wallet[0]

        # Validate transaction
        if transaction_type == "DEBIT" and current_balance < amount:
            return {"status": "error", "message": "Insufficient balance"}
        if transaction_type == "CREDIT":
            new_balance = current_balance + amount
        elif transaction_type == "DEBIT":
            new_balance = current_balance - amount
        else:
            return {"status": "error", "message": "Invalid transaction type"}

        # Update wallet balance
        cursor.execute('''
            UPDATE wallets SET balance = ? WHERE user_id = ?
        ''', (new_balance, user_id))
        connection.commit()
        connection.close()

        return {
            "status": "success",
            "message": f"{transaction_type} transaction of {amount} processed successfully",
            "new_balance": new_balance,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
