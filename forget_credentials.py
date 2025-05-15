import requests
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtGui import QIcon
from main import resource_path

class ForgotCredentialsWindow(QDialog):
    def __init__(self,api_base_url):
        super().__init__()
        
        self.api_base_url = api_base_url
        
        self.setWindowTitle("Reset Password")
        self.setFixedSize(400, 200)

        icon_path = resource_path("assets/images/icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        
        layout = QVBoxLayout()
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        layout.addWidget(self.email_input)

        self.get_username_button = QPushButton("Retrieve Username")
        self.get_username_button.clicked.connect(self.retrieve_username)
        layout.addWidget(self.get_username_button)
        
        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("Enter new password")
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.new_password_input)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm new password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.confirm_password_input)

        self.reset_button = QPushButton("Reset Password")
        self.reset_button.clicked.connect(self.reset_password)
        layout.addWidget(self.reset_button)

        self.setLayout(layout)

    def retrieve_username(self):
        email = self.email_input.text().strip()
        if not email:
            QMessageBox.warning(self, "Input Error", "Please enter your email.")
            return

        try:
            f"{self.api_base_url}/users/login"
            response = requests.post(f"{self.api_base_url}/api/retrieve-username", json={"email": email})
            if response.status_code == 200:
                username = response.json().get("username")
                QMessageBox.information(self, "Username Retrieved", f"Your username is: {username}")
            else:
                QMessageBox.warning(self, "Error", response.json().get("message", "Failed to retrieve username."))
        except Exception as e:
            QMessageBox.critical(self, "Network Error", f"Could not contact server:\n{str(e)}")

    def reset_password(self):
        email = self.email_input.text().strip()
        new_password = self.new_password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()

        if not email or not new_password or not confirm_password:
            QMessageBox.warning(self, "Error", "All fields are required.")
            return
        if new_password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return

        try:
            response = requests.post(f"{self.api_base_url}/api/reset-password", json={
                "email": email,
                "new_password": new_password
            })

            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Your password has been reset successfully.")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", response.json().get("message", "Password reset failed."))
        except Exception as e:
            QMessageBox.critical(self, "Network Error", f"Could not contact server:\n{str(e)}")
