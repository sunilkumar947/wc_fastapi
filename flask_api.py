from authenticate_user import UserAuthentication
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash
import mysql.connector
from datetime import datetime
from werkzeug.security import check_password_hash
import requests
app = Flask(__name__)
CORS(app)

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='your_user',
        password='your_password',
        database='your_database'
    )

conn = get_db_connection()
cursor = conn.cursor(dictionary=True)

@app.route('/')
def home():
    return "Flask API is running."

@app.route('/api/retrieve-username', methods=['POST'])
def retrieve_username():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE email = %s", (email,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify({'username': result[0]})
    else:
        return jsonify({'error': 'No user found with this email'}), 404

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    email = data.get('email')
    new_password = data.get('new_password')

    if not email or not new_password:
        return jsonify({'error': 'Email and new password are required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify({'error': 'No user found with this email'}), 404

    hashed_password = generate_password_hash(new_password)
    cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Password reset successful'})

@app.route('/users', methods=['GET'])
def get_all_users():
    cursor.execute("SELECT username, user_id FROM users")
    return jsonify(cursor.fetchall())

@app.route('/users/<user_id>', methods=['GET'])
def get_user_details(user_id):
    cursor.execute("SELECT username, email, user_id, status FROM users WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    return jsonify(result) if result else ('', 404)

@app.route('/users/email', methods=['GET'])
def get_user_by_email():
    email = request.args.get('email')
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    result = cursor.fetchone()
    return jsonify(result) if result else ('', 404)

@app.route('/users/username', methods=['GET'])
def get_username_by_email():
    email = request.args.get('email')
    cursor.execute("SELECT username FROM users WHERE email = %s", (email,))
    result = cursor.fetchone()
    return jsonify({'username': result['username']}) if result else ('', 404)

@app.route('/users/<int:user_id>/status', methods=['PUT'])
def update_user_status(user_id):
    status = request.json.get('status')
    cursor.execute("UPDATE users SET status = %s WHERE user_id = %s", (status, user_id))
    conn.commit()
    return jsonify({'status': 'updated'})

@app.route('/users/password', methods=['PUT'])
def update_password():
    email = request.json.get('email')
    new_password = request.json.get('new_password')
    hashed = generate_password_hash(new_password)
    cursor.execute("UPDATE users SET user_password = %s WHERE email = %s", (hashed, email))
    conn.commit()
    return jsonify({'status': 'password updated'})

@app.route('/work_time/<user_id>', methods=['GET'])
def get_work_time(user_id):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date and end_date:
        cursor.execute("""
            SELECT date, login_time, break_time, screen_time, logout_time
            FROM work_time
            WHERE user_id = %s AND date BETWEEN %s AND %s
        """, (user_id, start_date, end_date))
    else:
        cursor.execute("""
            SELECT date, login_time, break_time, screen_time, logout_time
            FROM work_time WHERE user_id = %s
        """, (user_id,))
    
    rows = cursor.fetchall()
    
    # Convert timedelta to string
    for row in rows:
        for key in ['break_time', 'screen_time']:
            if row[key] is not None:
                row[key] = str(row[key])
    
    return jsonify(rows)

@app.route('/app_usage/<user_id>', methods=['GET'])
def get_app_usage(user_id):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if start_date and end_date:
        cursor.execute("""
            SELECT date, app_name, url, duration FROM app_usage
            WHERE user_id = %s AND date BETWEEN %s AND %s
        """, (user_id, start_date, end_date))
    else:
        cursor.execute("SELECT date, app_name, url, duration FROM app_usage WHERE user_id = %s", (user_id,))
    return jsonify(cursor.fetchall())

@app.route('/screenshots/<int:user_id>', methods=['GET'])
def get_screenshots(user_id):
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    cursor.execute("""
        SELECT timestamp, screenshot_path FROM screenshots
        WHERE user_id = %s AND DATE(timestamp) BETWEEN %s AND %s
        ORDER BY timestamp ASC
    """, (user_id, start_date, end_date))
    return jsonify(cursor.fetchall())

@app.route('/<table>', methods=['POST'])
def insert_data(table):
    data = request.json
    placeholders = ', '.join(['%s'] * len(data))
    columns = ', '.join(data.keys())
    sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    cursor.execute(sql, tuple(data.values()))
    conn.commit()
    return jsonify({'status': 'inserted'})


@app.route('/api/admin-login', methods=['POST'])
def admin_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username == "admin" and password == "admin123":
        return jsonify({"message": "Admin login successful", "status": "admin"}), 200
    else:
        return jsonify({"error": "Invalid admin credentials"}), 401


@app.route('/users/register', methods=['POST'])
def register_user():
    data = request.json
    user_id = data.get('user_id')
    username = data.get('username')
    email = data.get('email')
    phone_no = data.get('phone_no')
    password = data.get('password')  

    if not all([user_id, username, email, phone_no, password]):
        return jsonify({'error': 'All fields are required.'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Email already registered.'}), 409
        hashed_password = generate_password_hash(password)
        # Insert new user
        cursor.execute("""
            INSERT INTO users (user_id, username, email, phone_no, user_password, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, username, email, phone_no, hashed_password, 'active'))
        conn.commit()
        conn.close()

        return jsonify({'message': 'User registered successfully.'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/users/login', methods=['POST'])
def user_login():
    data = request.json
    print("login data:", data)
    if data is None:
        return jsonify({"message": "No JSON received", "raw_data": request.data.decode(), "headers": dict(request.headers)}), 400

    username = data.get('username')
    password = data.get('password')
    print("USERNAME:",username)
    print("PASSWORD:",password)
    

    if not username or not password:
        return jsonify({"message": "Username and password are required."}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch user just by username
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({"message": "User not found."}), 404

        stored_hash = user.get('password')

        if not check_password_hash(stored_hash, password):
            return jsonify({"message": "Incorrect password."}), 401

        return jsonify({
            "message": "Login successful",
            "user_id": user['user_id'],
            "username": user['username'],
            "status": user['status']
        }), 200

    except Exception as e:
        return jsonify({"message": f"Login failed. Error: {str(e)}"}), 500


@app.route('/api/work_time', methods=['POST'])
def save_work_time():
    data = request.get_json()

    user_id = data.get('user_id')
    date = data.get('date')
    login_time = data.get('login_time')
    break_time = data.get('break_time')
    screen_time = data.get('screen_time')
    logout_time = data.get('logout_time')

    if not all([user_id, date , login_time,break_time,screen_time,logout_time]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO work_time (user_id, date, login_time, break_time, screen_time, current_time)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (user_id, date, login_time, break_time, screen_time, logout_time))
    conn.commit()
    conn.close()
    return jsonify({"message": "Work time saved successfully"}), 200



@app.route('/api/app_usage', methods=['POST'])
def save_app_usage():
    data = request.get_json()
    user_id = data.get('user_id')
    app_name = data.get('app_name')
    url = data.get('url')
    duration = data.get('duration')
    date = data.get('date')

    if not all([user_id, app_name,url, duration, date]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO app_usage (user_id, app_name, url, duration, date)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (user_id, app_name, url, duration, date))
    conn.commit()
    conn.close()
    return jsonify({"message": "App usage saved successfully"}), 200


@app.route('/api/screenshots', methods=['POST'])
def save_screenshot():
    data = request.get_json()
    user_id = data.get('user_id')
    screenshot_path = data.get('screenshot_path')
    timestamp = data.get('timestamp')

    if not all([user_id, screenshot_path, timestamp]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO screenshots (user_id, screenshot_path, timestamp)
        VALUES (%s, %s, %s)
    """
    cursor.execute(query, (user_id, screenshot_path, timestamp))
    conn.commit()
    conn.close()
    return jsonify({"message": "Screenshot saved successfully"}), 200



if __name__ == '__main__':
    app.run(debug=True, port=5000)
