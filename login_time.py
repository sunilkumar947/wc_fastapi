from PyQt6.QtWidgets import QLabel, QHBoxLayout, QWidget,QGraphicsDropShadowEffect
from PyQt6.QtCore import QDateTime, Qt, QTimer ,QTime
import os
import xlsxwriter # type: ignore
import win32com.client as win32 # type: ignore
from break_time import BreakWidget  
from screen_time import ScreenTimeWidget
import ctypes
from PyQt6.QtCore import QStandardPaths
from PIL import ImageGrab  # type: ignore
from PyQt6.QtGui import QColor


def get_documents_path():
    
    documents_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
    return documents_path


class LoginTimeWidget(QWidget):
    def __init__(self , break_widget: BreakWidget,screen_widget: ScreenTimeWidget):
        super().__init__()

        ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)
        
        self.break_widget = break_widget
        self.screen_widget = screen_widget
        
        self.login_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.login_label = QLabel(f"Login: {self.login_time}", self)
        self.login_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.login_label.setStyleSheet("""
             QLabel{
                background-color: #2C3E50;
                color: white;
                font: bold 12px 'Arial';
                padding: 5px;
                border-radius: 6px;
                }                          
            """)
        
        shadow_effect = QGraphicsDropShadowEffect(self.login_label)
        shadow_effect.setOffset(5, 5)  
        shadow_effect.setBlurRadius(10)  
        shadow_effect.setColor(QColor(0, 0, 0, 160)) 
        self.login_label.setGraphicsEffect(shadow_effect)
                                       
        layout = QHBoxLayout(self)
        layout.addWidget(self.login_label)
        
        layout.setContentsMargins(0, 30, 50,30)
    
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.save_login_time)
        self.timer.start(60000)
    

        self.stop_timer = QTimer(self)
        self.stop_timer.timeout.connect(self.check_stop_time)
        self.stop_timer.start(60000)
        
        # self.screenshot_timer = QTimer(self)
        # self.screenshot_timer.timeout.connect(self.take_screenshot)
        # self.screenshot_timer.start(60000)    
    
        self.login_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.current_date = QDateTime.currentDateTime().toString("yyyy-MM-dd")  
        
    def format_time(self, total_seconds):
        hours = total_seconds // 3600  # 
        minutes = (total_seconds % 3600) // 60  
        seconds = total_seconds % 60  
        return f"{hours:02}:{minutes:02}:{seconds:02}" 
    
    def get_login_time(self):
        """Return the login time."""
        return self.login_time
      
    def save_login_time(self,logout_time=None):
        
        print("in save login time ")
        login_time = self.login_time
        break_time = self.break_widget.total_break_time  
        current_date = self.current_date
        screen_time = self.screen_widget.screen_time
        formatted_break_time = self.format_time(break_time)
        formatted_screen_time = self.format_time(screen_time)
        
        if logout_time is None:
            logout_time = ""
        try:
            documents_path = get_documents_path()
            folder_path = os.path.join(documents_path, 'WorkTracker', 'logs')
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            file_path = os.path.join(folder_path, f'user_log_{current_date}.xlsx')

            workbook = xlsxwriter.Workbook(file_path)
            worksheet = workbook.add_worksheet()

            worksheet.write('A1', 'Date')
            worksheet.write('B1', 'Login Time')
            worksheet.write('C1', 'Total Break Time (MM:SS)')
            worksheet.write('D1', 'Screen Time (MM:SS)')
            worksheet.write('E1',"Logout Time")
           
            worksheet.write('A2', current_date)  
            worksheet.write('B2', login_time)  
            worksheet.write('C2', formatted_break_time) 
            worksheet.write('D2',  formatted_screen_time) 
            worksheet.write('E2',logout_time)

            workbook.close()
            print(f"Created and saved login time, , break time, and screen time to {file_path}")
            excel = win32.Dispatch('Excel.Application')
            excel.Visible = False  
            excel.DisplayAlerts = False  

            workbook = excel.Workbooks.Open(file_path)
            workbook.Password = '123456'  
            workbook.Save()  
            workbook.Close()  
            excel.Quit() 
        except Exception as e:
            print(f"Error while saving data: {e}")
       
                
    def check_stop_time(self):
        """Check if the current time is 6:25 PM and stop the process."""
        current_time = QDateTime.currentDateTime()
        stop_time = QDateTime.currentDateTime()  
        stop_time.setTime(QTime(18, 25, 0))

        if current_time >= stop_time:
            print("Stopping process at 6:25 PM")
            self.timer.stop()  
            self.stop_timer.stop()
                        
    
        
           
            
    