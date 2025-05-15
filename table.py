import sys
import time
import json
import psutil
import requests
import win32gui
import win32process
from PyQt6.QtCore import Qt, QThread, pyqtSignal 
from PyQt6.QtWidgets import (QTableWidgetItem,QVBoxLayout, QWidget,QTableWidget)
from PyQt6.QtWidgets import QHeaderView, QSizePolicy, QAbstractScrollArea


def get_active_window_process_name():
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['pid'] == pid:
                return proc.info['name']
    except Exception as e:
        print(f"Error getting active window process name: {e}")
    return None

class AppTrackerThread(QThread):
    update_signal = pyqtSignal(str, int)  # app_name, duration_seconds

    def __init__(self,user_id,main_window=None):
        super().__init__()
        self.running = True
        self.app_durations = {}  # {app_name: seconds}
        self.last_app = None
        self.last_time = time.time()
        self.user_id =  user_id  # Replace with dynamic user ID if needed
        self.api_url = "http://16.170.141.240:5000/api/app_usage"  # Replace with your Flask API URL
        self.main_window = main_window

    def run(self):
        while self.running:
            app_name = get_active_window_process_name()
            current_time = time.time()
            elapsed = current_time - self.last_time

            if app_name:
                if app_name not in self.app_durations:
                    self.app_durations[app_name] = 0
                self.app_durations[app_name] += elapsed
                self.update_signal.emit(app_name, int(self.app_durations[app_name]))

                # Send data to Flask API
                payload = {
                    "user_id": self.user_id,
                    "app_name": app_name,
                    "duration": int(self.app_durations[app_name])
                }
                try:
                    response = requests.post(self.api_url, json=payload)
                    if response.status_code != 200:
                        print(f"Failed to send data: {response.text}")
                except Exception as e:
                    print(f"Error sending data to API: {e}")

            self.last_app = app_name
            self.last_time = current_time
            time.sleep(1)

    def stop(self):
        self.running = False
        self.wait()

    def convert_duration_to_time_format(self, duration):
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        seconds = duration % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"

class TableWidget(QWidget):

    def __init__(self,user_id):
        super().__init__()
        self.user_id = user_id

        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["S.No", "Apps", "Url", "Duration"])
        self.update_table_rows()
        self.table.setStyleSheet("background-color: #717d8a;")
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                color: white;
                background-color: #2C3E50;  
                font-weight: bold;  
                font-size: 14px;  
                padding: 5px;  
            }
        """)
        self.table.setColumnWidth(0, 32)
        self.table.setColumnWidth(1, 240)
        self.table.setColumnWidth(2, 404)
        self.table.setColumnWidth(3, 77)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)  

        self.table.setMinimumHeight(100)
        self.table.setMinimumWidth(600)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.table.verticalScrollBar().setStyleSheet("""
                QScrollBar:vertical {
                    background: #2C3E50;
                    width: 10px;
                    margin: 0px 0px 0px 0px;
                    border: none;
                }
                QScrollBar::handle:vertical {
                    background: #95A5A6;
                    min-height: 20px;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #BDC3C7;
                }
                QScrollBar::add-line:vertical,
                QScrollBar::sub-line:vertical {
                    height: 0;
                    background: none;
                }
                QScrollBar::add-page:vertical,
                QScrollBar::sub-page:vertical {
                    background: none;
                }
            """)

        self.table.horizontalScrollBar().setStyleSheet("""
                    QScrollBar:horizontal {
                        background: #2C3E50;
                        height: 10px;
                        margin: 0px 0px 0px 0px;
                        border: none;
                    }
                    QScrollBar::handle:horizontal {
                        background: #95A5A6;
                        min-width: 20px;
                        border-radius: 4px;
                    }
                    QScrollBar::handle:horizontal:hover {
                        background: #BDC3C7;
                    }
                    QScrollBar::add-line:horizontal,
                    QScrollBar::sub-line:horizontal {
                        width: 0;
                        background: none;
                    }
                    QScrollBar::add-page:horizontal,
                    QScrollBar::sub-page:horizontal {
                        background: none;
                    }
                """)

        
        layout = QVBoxLayout(self)
        layout.addWidget(self.table)

        self.tracker_thread = AppTrackerThread(self.user_id)
        self.tracker_thread.update_signal.connect(self.update_table)
        self.tracker_thread.start()
        
        
    def update_table_rows(self):
        self.table.setRowCount(0)
        
    def update_table(self, app_name, duration):
        formatted_duration = self.tracker_thread.convert_duration_to_time_format(duration)
        for row in range(self.table.rowCount()):
            if self.table.item(row, 1) and self.table.item(row, 1).text() == app_name:
                self.table.setItem(row, 3, QTableWidgetItem(formatted_duration))
                return
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        self.table.setItem(row, 1, QTableWidgetItem(app_name))
        self.table.setItem(row, 2, QTableWidgetItem("N/A"))  
        self.table.setItem(row, 3, QTableWidgetItem(formatted_duration))
        
    def get_table_data(self):
        table_data = []
        for row in range(self.table.rowCount()):
            app_name = self.table.item(row, 1).text()
            duration = self.table.item(row, 3).text()
            table_data.append((app_name, "N/A", duration))  
        return table_data
            
        
    def setRowBackgroundColor(self, row, color):
        for column in range(self.table.columnCount()):
            item = self.table.item(row, column)
            if item is not None:
                item.setBackground(color)

    def closeEvent(self, event):
        self.tracker_thread.stop()
        super().closeEvent(event)
