from PyQt6.QtCore import QTimer, QDateTime,Qt,QEvent,pyqtSignal
from PyQt6.QtWidgets import QLabel, QHBoxLayout, QWidget,QApplication,QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor
from pynput import mouse,keyboard 



class BreakWidget(QWidget):

    break_started = pyqtSignal()
    break_ended = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.break_label = QLabel("Break: 0 min", self)
        self.break_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.break_label.setStyleSheet("""
             QLabel{
                background-color: #2C3E50;
                color: white;
                font: bold 12px 'Arial';
                padding: 5px;
                border-radius: 6px;
                }                          
            """)
        shadow_effect = QGraphicsDropShadowEffect(self.break_label)
        shadow_effect.setOffset(5, 5)  
        shadow_effect.setBlurRadius(10)  
        shadow_effect.setColor(QColor(0, 0, 0, 160)) 
        self.break_label.setGraphicsEffect(shadow_effect)
        
        layout = QHBoxLayout(self)
        layout.addWidget(self.break_label)
        layout.setContentsMargins(30, 30, 10,30)

        self.total_break_time = 0  
        self.current_break_time = 0  
        self.last_activity_time = QDateTime.currentDateTime()
        self.break_timer = QTimer(self)
        self.break_timer.timeout.connect(self.update_break_time)   
        
        self.inactivity_timer = QTimer(self)
        self.inactivity_timer.timeout.connect(self.check_activity)
        self.inactivity_timer.start(1000)
        
        self.break_timer.start(1000)  
        self.mouse_listener = mouse.Listener(on_move=self.on_mouse_move, on_click=self.on_mouse_click)
        self.mouse_listener.start()
        
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

    def get_break_time(self):
        """Return the total break time formatted as HH:MM:SS."""
        hours = self.total_break_time // 3600
        minutes = (self.total_break_time % 3600) // 60
        seconds = self.total_break_time % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    
    def update_break_time(self):
        self.current_break_time += 1
        self.total_break_time += 1  
        hours = self.total_break_time // 3600  
        minutes = (self.total_break_time % 3600) // 60  
        seconds = self.total_break_time % 60  
    
        self.break_label.setText(f"Break: {hours:02}:{minutes:02}:{seconds:02}")
        
    def check_activity(self):
        if self.last_activity_time.secsTo(QDateTime.currentDateTime()) >= 60:
            self.break_timer.start()
            self.break_started.emit()
        else:
            self.break_timer.stop() 
            self.break_ended.emit() 


    def on_mouse_move(self, x, y):
        self.last_activity_time = QDateTime.currentDateTime()

    def on_mouse_click(self, x, y, button, pressed):
        if pressed:
            self.last_activity_time = QDateTime.currentDateTime()

    def on_key_press(self, key):
        self.last_activity_time = QDateTime.currentDateTime()

    def closeEvent(self, event):
        self.mouse_listener.stop()
        self.keyboard_listener.stop()
        event.accept()
         