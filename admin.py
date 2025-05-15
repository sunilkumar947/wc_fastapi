from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QComboBox, QPushButton, QTableWidget,
    QTableWidgetItem, QVBoxLayout,QInputDialog, QHBoxLayout, QWidget,QApplication, QMessageBox, QDateEdit, QFrame
)
from PyQt6.QtCore import Qt, QDate,QTimer
from PyQt6.QtGui import QPixmap
# from cht_openai import SQLChatbot
from cht_genai import SQLChatbot


class AdminPanel(QMainWindow):
    
    def __init__(self,api_base_url, db_handler):
        print('opening adminpanel')
        super().__init__()
        self.api_base_url = api_base_url
        self.db_handler = db_handler
        print('SQLchatbot')
        self.chatbot = SQLChatbot(db_handler)

        print(self.chatbot.get_response("total users"))
        
        self.setWindowTitle("Admin Panel")
        self.setGeometry(100, 100, 1000, 700)
        self.setFixedSize(1000, 700)

        
        # Central Widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Sidebar (User Selection)
        sidebar = QVBoxLayout()
        sidebar.setAlignment(Qt.AlignmentFlag.AlignTop)
        sidebar.setContentsMargins(10, 10, 10, 10)
        sidebar.setSpacing(15)

        self.sidebar_widget = QWidget()
        self.sidebar_widget.setFixedWidth(300)
        sidebar_layout = QVBoxLayout(self.sidebar_widget)

        
        self.user_label = QLabel("Select User:")
        self.user_dropdown = QComboBox()
        self.populate_user_dropdown()
        self.fetch_details_button = QPushButton("Fetch Details")
        self.fetch_details_button.clicked.connect(self.fetch_user_details)

        sidebar_layout.addWidget(self.user_label)
        sidebar_layout.addWidget(self.user_dropdown)
        sidebar_layout.addWidget(self.fetch_details_button)

        # User Info Display
        self.name_label = QLabel("User Name: ")
        self.email_label = QLabel("Email: ")
        self.user_id_label = QLabel("User ID: ")
        self.status_label = QLabel("Status:")
        
        for label in [self.name_label, self.email_label, self.user_id_label]:
            label.setWordWrap(True)
            label.setFixedWidth(280)
        
        sidebar_layout.addWidget(self.name_label)
        sidebar_layout.addWidget(self.email_label)
        sidebar_layout.addWidget(self.user_id_label)
        sidebar_layout.addWidget(self.status_label)
        
        # Date Filters
        self.start_date_label = QLabel("Start Date:")
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        
        self.end_date_label = QLabel("End Date:")
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        
        sidebar_layout.addWidget(self.start_date_label)
        sidebar_layout.addWidget(self.start_date_edit)
        sidebar_layout.addWidget(self.end_date_label)
        sidebar_layout.addWidget(self.end_date_edit)
        
        
        self.screenshot_details_button = QPushButton("Show Screenshots")
        self.screenshot_details_button.clicked.connect(self.show_screenshots)
        
        self.login_details_button = QPushButton("Login Details")
        self.login_details_button.clicked.connect(self.show_login_details)
        self.activity_details_button = QPushButton("Activity Details")
        self.activity_details_button.clicked.connect(self.show_activity_details)
        
        self.activate_button = QPushButton("Activate User")
        self.activate_button.setStyleSheet("background-color: #28B463; color: white; font-weight: bold;")
        self.activate_button.clicked.connect(self.activate_user)

        self.deactivate_button = QPushButton("Deactivate User")
        self.deactivate_button.setStyleSheet("background-color: #E74C3C; color: white; font-weight: bold;")
        self.deactivate_button.clicked.connect(self.deactivate_user)

        self.chatbot_button = QPushButton("Chat with AI")
        self.chatbot_button.setStyleSheet("background-color: #3498DB; color: white; font-weight: bold;")
        self.chatbot_button.clicked.connect(self.open_chatbot)

        sidebar_layout.addWidget(self.chatbot_button)


        # Exit Button
        self.exit_button = QPushButton("Exit Admin Panel")
        self.exit_button.setStyleSheet("background-color: #34495E; color: white; font-weight: bold;")
        self.exit_button.clicked.connect(self.confirm_exit)

        sidebar_layout.addWidget(self.activate_button)
        sidebar_layout.addWidget(self.deactivate_button)
        sidebar_layout.addWidget(self.login_details_button)
        sidebar_layout.addWidget(self.activity_details_button)
        sidebar_layout.addWidget(self.screenshot_details_button)
        
        sidebar.addWidget(self.sidebar_widget)
        sidebar_layout.addWidget(self.exit_button)
        
        # Main Content Area
        content_area = QVBoxLayout()
        content_area.setContentsMargins(0, 10, 10, 10)
        
        self.table = QTableWidget()
        self.table.setColumnCount(0)
        self.table.setRowCount(0)
        content_area.addWidget(self.table)
        
        main_layout.addLayout(sidebar, 3)
        main_layout.addLayout(content_area, 7)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.populate_user_dropdown)
        self.timer.start(10000)
    
    def open_chatbot(self):
        chatbot_dialog = ChatbotDialog(self.chatbot, self)
        chatbot_dialog.exec()
        
    def populate_user_dropdown(self):
        print('Refreshing user list...')
        
        # Save the currently selected user
        selected_user = self.user_dropdown.currentText()

        # Fetch latest users
        users = self.db_handler.fetch_all_users()
        self.user_dropdown.clear()
        
        # Rebuild the user mapping
        self.user_map = {user[0]: user[1] for user in users}
        self.user_dropdown.addItems(self.user_map.keys())

        # Restore the previous selection if it still exists
        if selected_user in self.user_map:
            self.user_dropdown.setCurrentText(selected_user)
 
    # def populate_user_dropdown(self):
    #     print('refreshed+++++++++++++++++++++++++++++++++++++')
    #     users = self.db_handler.fetch_all_users()
    #     self.user_dropdown.clear()
    #     self.user_map = {user[0]: user[1] for user in users}
    #     self.user_dropdown.addItems(self.user_map.keys())

    def fetch_user_details(self):
        selected_user = self.user_dropdown.currentText()
        if not selected_user:
            QMessageBox.warning(self, "Input Error", "Please select a user.")
            return
        
        user_id = self.user_map.get(selected_user)
        user_details = self.db_handler.fetch_user_details(user_id)
        if user_details:
            self.name_label.setText(f"User Name: {user_details['username']}")
            self.email_label.setText(f"Email: {user_details['email']}")
            self.user_id_label.setText(f"User ID: {user_details['user_id'][:10]}...")
            self.status_label.setText(f"Status:{user_details['status']}")
            
        else:
            QMessageBox.information(self, "Not Found", "No user found.")
            self.name_label.setText("User Name: ")
            self.email_label.setText("Email: ")
            self.user_id_label.setText("User ID: ")
            self.status_label.setText("Status:")

    def show_login_details(self):
        self.table.clear()
        selected_user = self.user_dropdown.currentText()
        user_id = self.user_map.get(selected_user)
        if not user_id:
            QMessageBox.warning(self, "Input Error", "Please select a user.")
            return
        
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        
        login_data = self.db_handler.fetch_login_details(user_id, start_date, end_date)
        if login_data:
            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels(["Date", "Login Time", "Break Time", "Screen Time", "Logout Time"])
            self.table.setRowCount(len(login_data))
            for row_idx, row_data in enumerate(login_data):
                for col_idx, col_data in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
        else:
            QMessageBox.information(self, "No Data", "No login details found.")
            self.table.setRowCount(0)

    def show_activity_details(self):
        self.table.clear() 
        selected_user = self.user_dropdown.currentText()
        user_id = self.user_map.get(selected_user)
        if not user_id:
            QMessageBox.warning(self, "Input Error", "Please select a user.")
            return
        
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        
        activity_data = self.db_handler.fetch_activity_details(user_id, start_date, end_date)
        if activity_data:
            self.table.setColumnCount(4)
            self.table.setHorizontalHeaderLabels(["Date", "App Name", "URL", "Duration"])
            self.table.setRowCount(len(activity_data))
            for row_idx, row_data in enumerate(activity_data):
                for col_idx, col_data in enumerate(row_data):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
        else:
            QMessageBox.information(self, "No Data", "No activity details found.")
            self.table.setRowCount(0)
       
            
    def show_screenshots(self):
        self.table.clear() 
        """Fetch and display screenshots for the selected user based on date filters."""
        selected_user = self.user_dropdown.currentText()
        user_id = self.user_map.get(selected_user)

        if not user_id:
            QMessageBox.warning(self, "Input Error", "Please select a user.")
            return

        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")

        screenshot_data = self.db_handler.fetch_screenshots(user_id, start_date, end_date)

        if not screenshot_data:
            QMessageBox.information(self, "No Screenshots", "No screenshots found for this user and date range.")
            return

        # Clear table and set it up for displaying images
        self.table.setRowCount(len(screenshot_data))
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Timestamp", "Screenshot"])

        self.screenshot_paths = []  # Store paths for larger view
        
        for row_idx, (timestamp, screenshot_path) in enumerate(screenshot_data):
            self.screenshot_paths.append(screenshot_path)

            # Timestamp column
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(timestamp)))

            # Load image and set as a thumbnail
            label = QLabel()
            pixmap = QPixmap(screenshot_path)
            if not pixmap.isNull():
                label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
                label.setCursor(Qt.CursorShape.PointingHandCursor)
                label.mousePressEvent = lambda event, path=screenshot_path: self.open_fullscreen_view(path)
                self.table.setCellWidget(row_idx, 1, label)
            else:
                self.table.setItem(row_idx, 1, QTableWidgetItem("Image not found"))

    def open_fullscreen_view(self, path):
        """Open selected image in fullscreen viewer."""
        if path in self.screenshot_paths:
            index = self.screenshot_paths.index(path)
            viewer = ScreenshotViewer(self.screenshot_paths, index, self)
            viewer.exec()


    def activate_user(self):
        """Set user as active."""
        selected_user = self.user_dropdown.currentText()
        if not selected_user:
            QMessageBox.warning(self, "Selection Error", "Please select a user.")
            return

        user_id = self.user_map.get(selected_user)
        if self.db_handler.update_user_status(user_id, "Active"):  
            QMessageBox.information(self, "Success", "User activated successfully!")
            self.fetch_user_details() 
        else:
            QMessageBox.warning(self, "Error", "Failed to activate user.")

    def deactivate_user(self):
        """Set user as inactive."""
        selected_user = self.user_dropdown.currentText()
        if not selected_user:
            QMessageBox.warning(self, "Selection Error", "Please select a user.")
            return

        user_id = self.user_map.get(selected_user)
        if self.db_handler.update_user_status(user_id, "Inactive"):  
            QMessageBox.information(self, "Success", "User deactivated successfully!")
            self.fetch_user_details()  
        else:
            QMessageBox.warning(self, "Error", "Failed to deactivate user.")


    def confirm_exit(self):
        """ Show confirmation dialog before exiting """
        reply = QMessageBox.question(
            self, "Exit Confirmation", "Are you sure you want to exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            QApplication.quit()
            

######################################################################## CHAT-BOT ###############################################

from PyQt6.QtWidgets import QDialog, QTextEdit, QVBoxLayout, QPushButton, QLineEdit
class ChatbotDialog(QDialog):
    def __init__(self, chatbot, parent=None):
        super().__init__(parent)
        self.chatbot = chatbot
        self.setWindowTitle("AI Chatbot")
        self.setGeometry(300, 200, 600, 400)
        
        layout = QVBoxLayout()

        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        # Input field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter your question...")
        layout.addWidget(self.input_field)

        # Send button
        self.send_button = QPushButton("Ask")
        self.send_button.clicked.connect(self.send_query)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def send_query(self):
        user_input = self.input_field.text().strip()
        if not user_input:
            return

        # Display user query
        self.chat_display.append(f"Admin: {user_input}")

        # Get chatbot response
        response = self.chatbot.get_response(user_input)
        print(response,'rrrrrrrrrrrrrrrrr')
        self.chat_display.append(f"AI: {response}")

        # Clear input field
        self.input_field.clear()


############################################################## SCREENSHOT VIEWER ######################################

from PyQt6.QtWidgets import QLabel, QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem
from PyQt6.QtGui import QPixmap, QWheelEvent, QMouseEvent
from PyQt6.QtCore import Qt, QPointF

class ScreenshotViewer(QDialog):
    """Dialog to view screenshots with zoom, pan, and navigation."""
    
    def __init__(self, image_paths, current_index, parent=None):
        super().__init__(parent)
        self.image_paths = image_paths
        self.current_index = current_index
        self.scale_factor = 1.0 
        
        self.setWindowTitle("Screenshot Viewer")
        self.setGeometry(200, 100, 900, 700)

        layout = QVBoxLayout()

        # Graphics View to display image
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(self.view.renderHints(), True)

        self.image_item = QGraphicsPixmapItem()
        self.scene.addItem(self.image_item)
        self.view.setScene(self.scene)
        layout.addWidget(self.view)

        # Navigation buttons
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")

        self.prev_button.clicked.connect(self.show_previous)
        self.next_button.clicked.connect(self.show_next)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Enable Mouse Tracking for smooth panning
        self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Load first image
        self.update_image()

    def update_image(self):
        """Load and display the image."""
        if 0 <= self.current_index < len(self.image_paths):
            pixmap = QPixmap(self.image_paths[self.current_index])
            if not pixmap.isNull():
                self.image_item.setPixmap(pixmap)
                self.image_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
                self.scene.setSceneRect(self.image_item.boundingRect())

                # Reset zoom & center image
                self.scale_factor = 1.0
                self.view.resetTransform()
                self.view.fitInView(self.image_item, Qt.AspectRatioMode.KeepAspectRatio)
            else:
                self.image_item.setPixmap(QPixmap())  # Clear image
                self.scene.setSceneRect(0, 0, 800, 600)  # Set default empty scene

    def show_previous(self):
        """Show the previous image."""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_image()

    def show_next(self):
        """Show the next image."""
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.update_image()

    def wheelEvent(self, event: QWheelEvent):
        """Zoom in/out with the mouse scroll wheel."""
        zoom_factor = 1.2 if event.angleDelta().y() > 0 else 0.8
        self.scale_factor *= zoom_factor
        self.view.scale(zoom_factor, zoom_factor)

    def mousePressEvent(self, event: QMouseEvent):
        """Enable dragging the image while zoomed."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Disable dragging after releasing mouse button."""
        self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
        super().mouseReleaseEvent(event)
