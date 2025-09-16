import sys
from PySide6.QtWidgets import QApplication
from chat import ChatWindow
import screenshot

def main():
    # First, take screenshot using tkinter
    screenshot_path = screenshot.take_screenshot()
    
    # If screenshot was taken successfully, launch Qt chat app
    if screenshot_path:
        app = QApplication(sys.argv)
        
        # Launch chat window with screenshot
        chat_window = ChatWindow(screenshot_path)
        chat_window.show()
        
        sys.exit(app.exec())
    else:
        print("Screenshot was cancelled or failed.")

if __name__ == "__main__":
    main()