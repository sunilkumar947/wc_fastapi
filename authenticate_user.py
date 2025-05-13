import bcrypt
from flask import jsonify

class UserAuthentication:
    def __init__(self, db_handler): 
        self.connection = db_handler.connection  
        self.cursor = self.connection.cursor()

    def verify_password(self, entered_password, stored_password_hash):
        return bcrypt.checkpw(entered_password.encode(), stored_password_hash.encode())

    def authenticate_user(self, username, password):
        try:
            sql = "SELECT user_id, username, user_password, status FROM users WHERE username = %s"
            self.cursor.execute(sql, (username,))
            result = self.cursor.fetchone()
            
            if result and len(result) == 4:
                user_id, username, stored_password_hash, status = result
                if self.verify_password(password, stored_password_hash):
                    return jsonify({
                        "user_id": user_id,
                        "username": username,
                        "status": status,
                        "message": "Login successful"
                    }), 200
                else:
                    return jsonify({"error": "Invalid password"}), 401
            else:
                return jsonify({"error": "User not found"}), 404

        except Exception as e:
            return jsonify({"error": str(e)}), 500
