from PyQt6.QtWidgets import QLabel, QHBoxLayout, QWidget, QGraphicsDropShadowEffect
from PyQt6.QtCore import QDateTime, Qt, QTimer, QTime
import os
from break_time import BreakWidget  
import ctypes
from PyQt6.QtGui import QColor

class ScreenTimeWidget(QWidget):
    def __init__(self, break_widget: BreakWidget):
        super().__init__()

        ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)
        
        self.break_widget = break_widget
        
        self.login_time = QDateTime.currentDateTime()
        self.screen_time = 0  # in seconds
        self.is_breaking = False
        
        self.screen_time_label = QLabel(f"Screen-Time: {self.format_time(self.screen_time)}", self)
        self.screen_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.screen_time_label.setStyleSheet("""
             QLabel{
                background-color: #2C3E50;
                color: white;
                font: bold 12px 'Arial';
                padding: 5px;
                border-radius: 6px;
                }                          
            """)
        
        shadow_effect = QGraphicsDropShadowEffect(self.screen_time_label)
        shadow_effect.setOffset(5, 5)  
        shadow_effect.setBlurRadius(10)  
        shadow_effect.setColor(QColor(0, 0, 0, 160)) 
        self.screen_time_label.setGraphicsEffect(shadow_effect)
        
        layout = QHBoxLayout(self)
        layout.addWidget(self.screen_time_label)
        layout.setContentsMargins(30, 30, 8, 30)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_screen_time)
        self.timer.start(1000)  
        
        # Connect signals from BreakWidget
        self.break_widget.break_started.connect(self.on_break_started)
        self.break_widget.break_ended.connect(self.on_break_ended)

    def get_screen_time(self):
        """Return the total screen time in seconds."""
        return self.format_time(self.screen_time)
    
    def update_screen_time(self):
        if not self.is_breaking:
            # Calculate elapsed time since login
            elapsed_time = self.login_time.secsTo(QDateTime.currentDateTime())
            self.screen_time = elapsed_time - self.break_widget.total_break_time
            self.screen_time_label.setText(f"Screen-Time: {self.format_time(self.screen_time)}")

    def on_break_started(self):
        self.is_breaking = True  

    def on_break_ended(self):
        self.is_breaking = False  

    def format_time(self, total_seconds):  
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"
