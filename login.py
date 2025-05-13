from PyQt6.QtWidgets import QDialog, QVBoxLayout, QApplication, QLineEdit, QPushButton, QMessageBox
from registration import RegistrationWindow
from admin_login import AdminLoginWindow
from forget_credentials import ForgotCredentialsWindow
import sys
import requests


class LoginWindow(QDialog):
    api_base_url = "http://13.61.186.99:5000"
    def __init__(self, api_base_url):
        super().__init__()
        self.setWindowTitle("Login")
        self.setFixedSize(400, 200)

        self.api_base_url = api_base_url
        self.user_id = None
        self.username = None

        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.authenticate_user)
        layout.addWidget(self.login_button)

        self.admin_login_button = QPushButton("Login as Admin")
        self.admin_login_button.clicked.connect(self.open_admin_login)
        layout.addWidget(self.admin_login_button)

        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.open_registration)
        layout.addWidget(self.register_button)

        self.forgot_button = QPushButton("Forgot Username/Password?")
        self.forgot_button.clicked.connect(self.forgot_credentials)
        layout.addWidget(self.forgot_button)

        self.setLayout(layout)

    def authenticate_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Username and password cannot be empty.")
            return

        try:
            response = requests.post(f"{self.api_base_url}/users", json={
                "username": username,
                "password": password
            })

            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "Inactive":
                    QMessageBox.warning(self, "Access Denied", "Your account is inactive. Contact admin.")
                    return

                self.user_id = data.get("user_id")
                self.username = data.get("username")

                QMessageBox.information(self, "Login Successful", f"Welcome, {self.username}!")
                self.accept()

            else:
                QMessageBox.warning(self, "Login Failed", response.json().get("message", "Login failed."))

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Network Error", f"Could not connect to the server.\n\nError: {e}")

    def open_admin_login(self):
        admin_login = AdminLoginWindow(self.api_base_url)
        if admin_login.exec():
            QMessageBox.information(self, "Admin Login", "Welcome, Admin!")
            self.accept()

    def open_registration(self):
        self.registration_window = RegistrationWindow(self.api_base_url)
        self.registration_window.exec()

    def forgot_credentials(self):
        self.forgot_password_window = ForgotCredentialsWindow(self.api_base_url)
        self.forgot_password_window.exec()

    def closeEvent(self, event):
        event.accept()
        self.exit_application()

    def exit_application(self):
        QApplication.quit()
        sys.exit(0)
