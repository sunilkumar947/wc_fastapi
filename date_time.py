from PyQt6.QtCore import QTimer, QDateTime
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget,QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor
class DateTimeWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.date_label = QLabel(self)
        self.time_label = QLabel(self)
        self.date_label.setStyleSheet("""
            QLabel {
                background-color: #2C3E50;
                color: white;
                font: bold 12px 'Arial';
                padding: 5px;  
                border-radius: 6px; 
            }
        """)
        self.time_label.setStyleSheet("""
            QLabel {
                background-color: #2C3E50;
                color: white;
                font: bold 12px 'Arial';
                padding: 5px;
                border-radius: 6px; 
            }
        """)
        
        shadow_effect = QGraphicsDropShadowEffect(self.date_label)
        shadow_effect.setOffset(5, 5)  
        shadow_effect.setBlurRadius(10)  
        shadow_effect.setColor(QColor(0, 0, 0, 160)) 
        self.date_label.setGraphicsEffect(shadow_effect)
        shadow_effect = QGraphicsDropShadowEffect(self.time_label)
        shadow_effect.setOffset(5, 5)  
        shadow_effect.setBlurRadius(10)  
        shadow_effect.setColor(QColor(0, 0, 0, 160)) 
        self.time_label.setGraphicsEffect(shadow_effect)
        
        self.update_date_time()
        
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.date_label)
        layout.addWidget(self.time_label)
        layout.setContentsMargins(0, 0, 665, 10)

      

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_date_time)
        self.timer.start(1000) 
         
    def get_date_time(self):
        """Return the total screen time in seconds."""
        current_date_time = QDateTime.currentDateTime()
        current_date = current_date_time.toString("yyyy-MM-dd")
        current_time = current_date_time.toString("hh:mm:ss")
        return current_date, current_time

    
    def update_date_time(self):
        current_date_time = QDateTime.currentDateTime()
        current_date = current_date_time.toString("yyyy-MM-dd")
        current_time = current_date_time.toString("hh:mm:ss")

        self.date_label.setText(f"Date: {current_date}")
        self.time_label.setText(f"Time: {current_time}")
    