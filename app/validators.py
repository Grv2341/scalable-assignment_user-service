import re
from datetime import datetime

def validate_user_input(name, email, password, pan_card, dob):
    errors = []

    if not name or len(name) < 2:
        errors.append("Name must be at least 2 characters long.")

    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_regex, email):
        errors.append("Invalid email format.")

    password_regex = r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$'
    if not re.match(password_regex, password):
        errors.append("Password must be at least 8 characters long and contain both letters and numbers.")

    pan_regex = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
    if not re.match(pan_regex, pan_card):
        errors.append("PAN card must be 10 characters long, uppercase, and follow the format (e.g., ABCDE1234F).")

    try:
        dob_date = datetime.strptime(dob, '%Y-%m-%d')
        if dob_date >= datetime.now():
            errors.append("Date of birth must be a past date.")
    except ValueError:
        errors.append("Date of birth must be in the format YYYY-MM-DD.")

    return errors
