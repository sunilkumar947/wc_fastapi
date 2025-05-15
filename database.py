import requests
import bcrypt

class APIHandler:
    api_base_url = "http://16.170.141.240:5000"
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url.rstrip("/")
        print("APIHandler initialized with URL:", self.api_base_url)

    def insert_data(self, endpoint, data):
        try:
            url = f"{self.api_base_url}/{endpoint}"
            response = requests.post(url, json=data)
            return response.ok
        except Exception as e:
            print("Error inserting data:", e)
            return False

    def fetch_all_users(self):
        try:
            response = requests.get(f"{self.api_base_url}/users")
            return response.json() if response.ok else []
        except Exception as e:
            print("Error fetching users:", e)
            return []

    def fetch_user_details(self, user_id):
        try:
            response = requests.get(f"{self.api_base_url}/users/{user_id}")
            return response.json() if response.ok else None
        except Exception as e:
            print("Error fetching user details:", e)
            return None

    def fetch_login_details(self, user_id, start_date=None, end_date=None):
        try:
            params = {"start_date": start_date, "end_date": end_date} if start_date and end_date else {}
            response = requests.get(f"{self.api_base_url}/work_time/{user_id}", params=params)
            return response.json() if response.ok else None
        except Exception as e:
            print("Error fetching login details:", e)
            return None

    def fetch_activity_details(self, user_id, start_date=None, end_date=None):
        try:
            params = {"start_date": start_date, "end_date": end_date} if start_date and end_date else {}
            response = requests.get(f"{self.api_base_url}/app_usage/{user_id}", params=params)
            return response.json() if response.ok else None
        except Exception as e:
            print("Error fetching activity details:", e)
            return None

    def fetch_screenshots(self, user_id, start_date, end_date):
        try:
            params = {"start_date": start_date, "end_date": end_date}
            response = requests.get(f"{self.api_base_url}/screenshots/{user_id}", params=params)
            return response.json() if response.ok else []
        except Exception as e:
            print("Error fetching screenshots:", e)
            return []

    def update_user_status(self, user_id, status):
        try:
            response = requests.put(f"{self.api_base_url}/users/{user_id}/status", json={"status": status})
            return response.ok
        except Exception as e:
            print("Error updating user status:", e)
            return False

    def get_user_by_email(self, email):
        try:
            response = requests.get(f"{self.api_base_url}/users/email", params={"email": email})
            return response.json() if response.ok else None
        except Exception as e:
            print("Error fetching user by email:", e)
            return None

    def get_username_by_email(self, email):
        try:
            response = requests.get(f"{self.api_base_url}/users/username", params={"email": email})
            return response.json().get("username") if response.ok else None
        except Exception as e:
            print("Error getting username by email:", e)
            return None

    def update_password(self, email, new_password):
        try:
            hashed_password = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
            response = requests.put(f"{self.api_base_url}/users/password", json={"email": email, "new_password": hashed_password})
            return response.ok
        except Exception as e:
            print("Error updating password:", e)
            return False
