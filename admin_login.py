from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtGui import QIcon
import requests
from main import resource_path


class AdminLoginWindow(QDialog):
    DEFAULT_ADMIN_CREDENTIALS = {
        "username": "admin",
        "password": "admin123"
    }

    def __init__(self,api_base_url):
        super().__init__()
        self.api_base_url = api_base_url
        self.setWindowTitle("Admin Login")
        self.setFixedSize(400, 200)

        icon_path = resource_path("assets/images/icon.ico")
        self.setWindowIcon(QIcon(icon_path))

        layout = QVBoxLayout()

        # Admin Username Input
        self.admin_username_input = QLineEdit()
        self.admin_username_input.setPlaceholderText("Admin Username")
        layout.addWidget(self.admin_username_input)

        # Admin Password Input
        self.admin_password_input = QLineEdit()
        self.admin_password_input.setPlaceholderText("Admin Password")
        self.admin_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.admin_password_input)

        # Login Button
        self.admin_login_button = QPushButton("Login")
        self.admin_login_button.clicked.connect(self.authenticate_admin)
        layout.addWidget(self.admin_login_button)

        self.setLayout(layout)

    def authenticate_admin(self):
        """Authenticate admin credentials via Flask API."""
        admin_username = self.admin_username_input.text()
        admin_password = self.admin_password_input.text()

        try:
            response = requests.post(
                "http://13.60.213.82:5000/api/admin-login",
                json={"username": admin_username, "password": admin_password}
            )
            if response.status_code == 200:
                QMessageBox.information(self, "Login Successful", "Welcome, Admin!")
                self.accept()
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid admin username or password.")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Connection Error", f"Could not connect to server:\n{e}")
