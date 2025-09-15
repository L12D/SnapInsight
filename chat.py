import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SnapInsight")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Add widgets
        title_label = QLabel("Welcome to SnapInsight")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        
        info_label = QLabel("This is your basic PySide6 application")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 14px; margin: 10px;")
        
        button = QPushButton("Click Me!")
        button.clicked.connect(self.on_button_click)
        button.setStyleSheet("padding: 10px; font-size: 16px;")
        
        # Add widgets to layout
        layout.addWidget(title_label)
        layout.addWidget(info_label)
        layout.addWidget(button)
        
    def on_button_click(self):
        QMessageBox.information(self, "Hello", "Button clicked!")

def main():
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()