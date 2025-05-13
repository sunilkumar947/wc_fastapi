from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtGui import QIcon
# from database import DatabaseHandler
from main_window import MainWindow
from tray_handler import TrayHandler
import sys
import os
import threading
import logging

from admin import AdminPanel




def resource_path(relative_path):
    """Get the resource path for application assets."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    from login import LoginWindow
    try:
        print("in")
        app = QApplication(sys.argv)
        API_BASE_URL = "http://13.61.186.99:5000"

        # Resource paths (icon)
        icon_path = resource_path("assets/images/icon.ico")

        # Database handler
        # db_handler = DatabaseHandler(
        #     host="localhost",
        #     user="root",
        #     password="root",
        #     database="tracker_db"
        # )
        # db_handler = DatabaseHandler(
        #     host="sql12.freesqldatabase.com",
        #     user="sql12775997",
        #     password="KADxumQrpE",
        #     database="sql12775997"
        # )
        # if not db_handler.connection:
        #     # logging.error("Database connection failed. Exiting.", exc_info=True)
        #     sys.exit(1)

        # Login window
        login_window = LoginWindow(API_BASE_URL)
        login_window.setWindowIcon(QIcon(icon_path))
        # tray_handler = TrayHandler(icon_path)
        # tray_handler.show_signal.connect(login_window.show)
        # tray_handler.hide_signal.connect(login_window.hide)
        # tray_handler.exit_signal.connect(app.quit)
        # tray_thread = threading.Thread(target=tray_handler.setup_tray, daemon=True)
        # tray_thread.start()
        
        
        if login_window.exec():  # If login is successful
            login_window.close() 
            if login_window.user_id is None:  # Admin Login
                admin_panel = AdminPanel(API_BASE_URL)
                admin_panel.setWindowIcon(QIcon(icon_path))  # Set icon for admin panel

                tray_handler = TrayHandler(icon_path)
                tray_handler.show_signal.connect(admin_panel.show)
                tray_handler.hide_signal.connect(admin_panel.hide)
                tray_handler.exit_signal.connect(app.quit)

                # Start tray thread safely
                tray_thread = threading.Thread(target=tray_handler.setup_tray, daemon=True)
                tray_thread.start()
                admin_panel.show()
                admin_panel.closeEvent = lambda event: (
                    tray_handler.on_exit(), sys.exit(0)
                ) 
                
            else:  # Regular User Login
                print(f"Logged in as user: {login_window.user_id}")
                user_id = login_window.user_id
                username = login_window.username
                main_window = MainWindow(icon_path, API_BASE_URL, user_id,username)

                tray_handler = TrayHandler(icon_path)
                tray_handler.show_signal.connect(main_window.show)
                tray_handler.hide_signal.connect(main_window.hide)
                tray_handler.exit_signal.connect(app.quit)

                # Start tray thread safely
                tray_thread = threading.Thread(target=tray_handler.setup_tray, daemon=True)
                tray_thread.start()

                main_window.show()
                main_window.closeEvent = lambda event: sys.exit(0)
        sys.exit(app.exec())

    except Exception as e:
        # logging.error(f"Application failed to start: {e}", exc_info=True)
        sys.exit(1)














