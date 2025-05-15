from datetime import datetime
import time
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QFrame, QPushButton, QMessageBox
from PyQt6.QtCore import QDateTime, QTimer, Qt
from PyQt6.QtGui import QIcon, QFont
from date_time import DateTimeWidget
from login_time import LoginTimeWidget
from break_time import BreakWidget
from table import TableWidget
from screen_time import ScreenTimeWidget
from PyQt6.QtCore import QStandardPaths
from PIL import ImageGrab
import os
import winreg
import requests

def get_documents_path():
    return QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)

class MainWindow(QMainWindow):
    def __init__(self, icon_path, api_base_url, user_id, username):
        super().__init__()
        print("MainWindow initialized.")

        self.user_id = user_id
        self.username = username
        self.api_base_url = api_base_url

        self.setWindowTitle("Work Tracker")
        self.setWindowIcon(QIcon(icon_path))
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)

        # self.screenshot_timer = QTimer(self)
        # self.screenshot_timer.timeout.connect(self.take_screenshot)
        # self.screenshot_timer.start(60000)  # every 60 sec

        central_widget = QWidget(self)
        central_widget.setStyleSheet("background-color: #2b2f38;")
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        username_layout = QVBoxLayout()
        header_layout = QHBoxLayout()
        login_break_layout = QHBoxLayout()

        # Title
        title_label = QLabel("Work Tracker Dashboard", self)
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; padding: 10px;")

        # User Info
        self.user_info_label = QLabel(f"User: {self.username} | ID: {self.user_id}", self)
        self.user_info_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.user_info_label.setStyleSheet("color: white; padding: 10px;")

        # Logout Button
        self.logout_button = QPushButton("Logout", self)
        self.logout_button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.logout_button.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border-radius: 5px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        self.logout_button.clicked.connect(self.confirm_logout)

        # Layouts
        username_layout.addWidget(self.user_info_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.logout_button)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #555; height: 2px;")

        # Widgets
        self.date_time_widget = DateTimeWidget()
        self.break_widget = BreakWidget()
        self.screen_time_widget = ScreenTimeWidget(self.break_widget)
        self.login_time_widget = LoginTimeWidget(self.break_widget, self.screen_time_widget)
        self.table_widget = TableWidget(self.user_id)

        widget_style = """
            QWidget {
                border-radius: 10px;
                border: 1px solid #555;
                background-color: #3d424b;
                color: white;
                padding: 5px;
            }
        """
        self.login_time_widget.setStyleSheet(widget_style)
        self.break_widget.setStyleSheet(widget_style)
        self.screen_time_widget.setStyleSheet(widget_style)
        self.table_widget.setStyleSheet("border-radius: 10px; background-color: #2f333b; color: white;")

        self.login_time_widget.setMinimumSize(200, 100)
        self.break_widget.setMinimumSize(200, 100)
        self.screen_time_widget.setMinimumSize(200, 100)

        login_break_layout.addWidget(self.login_time_widget)
        login_break_layout.addWidget(self.break_widget)
        login_break_layout.addWidget(self.screen_time_widget)

        main_layout.addLayout(username_layout)
        main_layout.addLayout(header_layout)
        main_layout.addWidget(divider)
        main_layout.addWidget(self.date_time_widget)
        main_layout.addLayout(login_break_layout)
        main_layout.addWidget(self.table_widget)

        main_layout.setContentsMargins(10, 10, 10, 10)
        login_break_layout.setContentsMargins(50, 0, 280, 0)
        login_break_layout.setSpacing(250)
        main_layout.setSpacing(10)

        # Data update every 60 sec
        # self.update_timer = QTimer(self)
        # self.update_timer.timeout.connect(self.update_data)
        # self.update_timer.timeout.connect(self.take_screenshot)
        # self.update_timer.start(60000)
        # self.update_data()
        # self.take_screenshot()
          
    
    def update_data(self):
        date, current_time = self.date_time_widget.get_date_time()
        login_time = self.login_time_widget.get_login_time()
        break_time = self.break_widget.get_break_time()
        screen_time = self.screen_time_widget.get_screen_time()

        # Send work_time to Flask
        payload = {
            "user_id": self.user_id,
            "date": date,
            "login_time": login_time,
            "break_time": break_time,
            "screen_time": screen_time,
            "logout_time": current_time
        }
        print("payload",payload)
        
        try:
            requests.post(f"{self.api_base_url}/api/work_time", json=payload)
            print("Work time data sent to server.")
            
        except Exception as e:
            print(f"Error sending work time: {e}")

        # Send app_usage to Flask
        app_usage_data = self.table_widget.get_table_data()
        for app_name, url, duration in app_usage_data:
            usage_payload = {
                "user_id": self.user_id,
                "app_name": app_name,
                "url": url,
                "duration": duration,
                "date": date
            }
            try:
                requests.post(f"{self.api_base_url}/api/app_usage", json=usage_payload)
            except Exception as e:
                print(f"Error sending app usage: {e}")

    def confirm_logout(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Logout")
        msg_box.setText("Are you sure you want to logout?")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #3a434d;
                color: white;
                border-radius: 10px;
                font-size: 12px;
            }
            QPushButton {
                border-radius: 5px;
                padding: 5px 15px;
                font-weight: bold;
            }
        """)
        yes_button = msg_box.addButton("Logout", QMessageBox.ButtonRole.AcceptRole)
        yes_button.setStyleSheet("background-color: #d9534f; color: white;")
        no_button = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        no_button.setStyleSheet("background-color: #555; color: white;")

        msg_box.exec()
        if msg_box.clickedButton() == yes_button:
            self.logout()

    def logout(self):
        logout_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.login_time_widget.save_login_time(logout_time=logout_time)
        print(f"User logged out at {logout_time}. Closing app...")
        self.close()

    def closeEvent(self, event):
        logout_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.login_time_widget.save_login_time(logout_time=logout_time)
        print(f"Logout time saved: {logout_time}")
        event.accept()

    def get_onedrive_documents_path(self):
        try:
            key = winreg.HKEY_CURRENT_USER
            sub_key = r"Software\Microsoft\OneDrive"
            with winreg.OpenKey(key, sub_key) as reg_key:
                onedrive_path, _ = winreg.QueryValueEx(reg_key, "UserFolder")
            return os.path.join(onedrive_path, "Documents")
        except Exception as e:
            print(f"Error getting OneDrive path: {e}")
            return None

    def take_screenshot(self):
        try:
            folder_path = self.get_onedrive_documents_path() or get_documents_path()
            screenshot_folder = os.path.join(folder_path, "WorkTracker", "screenshots", self.user_id)
            os.makedirs(screenshot_folder, exist_ok=True)

            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            screenshot_path = os.path.join(screenshot_folder, f"screenshot_{timestamp}.png")

            screenshot = ImageGrab.grab()
            screenshot.save(screenshot_path)

            # Send screenshot path + time to Flask
            data = {
                "user_id": self.user_id,
                "screenshot_path": screenshot_path,
                "timestamp": timestamp
            }
            requests.post(f"{self.api_base_url}/api/screenshots", json=data)
            print(f"Screenshot saved and sent: {screenshot_path}")
        except Exception as e:
            print(f"Screenshot error: {e}")
