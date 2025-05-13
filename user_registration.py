# user_registration.py (for Flask server side)
import bcrypt
import mysql.connector
import uuid

def register_user_to_db(username, email, phone_no, password, db):
    user_id = str(uuid.uuid4())
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    cursor = db.cursor()
    cursor.execute("INSERT INTO users (user_id, username, email, phone_no, user_password) VALUES (%s, %s, %s, %s, %s)",
                   (user_id, username, email, phone_no, hashed_password))
    db.commit()
    cursor.close()
