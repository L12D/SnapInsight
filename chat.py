import sys
import os
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap, QFont
import openai
import base64
import markdown
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLineEdit, QPushButton, 
                               QScrollArea, QLabel, QMessageBox, QFrame)
from PySide6.QtCore import Qt, QThread, Signal


class ChatMessage(QFrame):
    def __init__(self, message, is_user=True, image_path=None):
        super().__init__()
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {'#007ACC' if is_user else '#f0f0f0'};
                color: {'white' if is_user else 'black'};
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            }}
        """)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Add image if provided and exists
        if image_path and os.path.exists(image_path):
            image_label = QLabel()
            pixmap = QPixmap(image_path)
            # Scale image to fit nicely in chat
            scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(scaled_pixmap)
            layout.addWidget(image_label)
        
        # Add message text - use QTextBrowser for AI responses to support markdown
        if is_user:
            message_widget = QLabel(message)
            message_widget.setWordWrap(True)
            message_widget.setFont(QFont("Arial", 13))
            message_widget.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
            message_widget.setCursor(Qt.IBeamCursor)
        else:
            # Use QLabel with HTML converted from markdown for AI responses
            message_widget = QLabel()
            
            # Convert markdown to HTML
            html_message = markdown.markdown(message)
            
            message_widget.setText(html_message)
            message_widget.setWordWrap(True)
            message_widget.setFont(QFont("Arial", 13))
            message_widget.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
            message_widget.setCursor(Qt.IBeamCursor)
        
        layout.addWidget(message_widget)


class OpenAIWorker(QThread):
    response_received = Signal(str)
    error_occurred = Signal(str)
    
    def __init__(self, messages):
        super().__init__()
        self.messages = messages
        
    def run(self):
        try:
            # Initialize OpenAI client
            client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=self.messages,
                max_tokens=300
            )
            
            self.response_received.emit(response.choices[0].message.content)
        except Exception as e:
            self.error_occurred.emit(str(e))


class ChatWindow(QMainWindow):
    def __init__(self, screenshot_path=None):
        super().__init__()
        self.screenshot_path = screenshot_path
        self.messages = []
        self.screenshot_sent = False  # Track if screenshot has been sent
        self.preview_label = None  # Store reference to preview label
        self.resize(1000, 900)
        self.setup_ui()

        # Show welcome message or indicate screenshot is ready
        if screenshot_path and os.path.exists(screenshot_path):
            # Update placeholder text to guide user
            self.message_input.setPlaceholderText("Ask a question about this screenshot...")
        else:
            # Add welcome message if no screenshot
            self.add_chat_message("Welcome to SnapInsight! You can start chatting with the AI.", is_user=False)
    
    def setup_ui(self):
        self.setWindowTitle("SnapInsight - AI Chat")
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title
        title_label = QLabel("SnapInsight AI Chat")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # Chat area
        self.chat_scroll = QScrollArea()
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_widget.setLayout(self.chat_layout)
        self.chat_scroll.setWidget(self.chat_widget)
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        main_layout.addWidget(self.chat_scroll)
        
        # Input area with screenshot preview
        input_container = QHBoxLayout()
        
        # Screenshot preview (if exists)
        if self.screenshot_path and os.path.exists(self.screenshot_path):
            self.preview_label = QLabel()
            pixmap = QPixmap(self.screenshot_path)
            # Scale to a small preview size
            scaled_preview = pixmap.scaled(280, 280, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(scaled_preview)
            self.preview_label.setStyleSheet("border: 2px solid #ccc; border-radius: 5px; padding: 5px;")
            input_container.addWidget(self.preview_label)
        
        # Text input and send button
        input_layout = QVBoxLayout()
        
        text_input_layout = QHBoxLayout()
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.returnPressed.connect(self.send_message)
        text_input_layout.addWidget(self.message_input)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setStyleSheet("padding: 10px; font-size: 14px;")
        text_input_layout.addWidget(self.send_button)
        
        input_layout.addLayout(text_input_layout)
        input_container.addLayout(input_layout)
        
        main_layout.addLayout(input_container)
        
        # Set focus on the message input field
        self.message_input.setFocus()
    
    def add_chat_message(self, message, is_user=True, image_path=None):
        """Add a message to the chat display"""
        chat_message = ChatMessage(message, is_user, image_path)
        self.chat_layout.addWidget(chat_message)
        
        # Scroll to bottom
        self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        )
    
    def send_message(self):
        message_text = self.message_input.text().strip()
        if not message_text:
            return
        
        # Clear input
        self.message_input.clear()
        
        # If we have a screenshot and haven't sent it yet, include it with the first user message
        if self.screenshot_path and not self.screenshot_sent:
            self.send_screenshot_with_message(message_text)
        else:
            # Regular text message
            self.add_chat_message(message_text, is_user=True)
            
            # Add to messages for OpenAI
            self.messages.append({
                "role": "user",
                "content": message_text
            })
            
            # Send to OpenAI
            self.send_to_openai()
    
    def send_screenshot_with_message(self, user_message):
        """Send the screenshot along with the user's message"""
        try:
            # Add user message WITH screenshot to chat display
            self.add_chat_message(user_message, is_user=True, image_path=self.screenshot_path)
            
            # Prepare the message for OpenAI API with screenshot
            with open(self.screenshot_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            self.messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_message
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            })
            
            self.screenshot_sent = True
            
            # Hide the screenshot preview
            if self.preview_label:
                self.preview_label.hide()
            
            # Reset placeholder text
            self.message_input.setPlaceholderText("Type your message here...")
            
            # Send to OpenAI
            self.send_to_openai()
            
        except Exception as e:
            QMessageBox.warning(self, "Image Error", f"Failed to process screenshot: {str(e)}")
    
    def send_to_openai(self):
        """Send messages to OpenAI API"""
        # Check if API key is set
        if not os.getenv('OPENAI_API_KEY'):
            QMessageBox.warning(self, "API Key Missing", 
                              "Please set your OPENAI_API_KEY environment variable.")
            return
        
        # Disable send button
        self.send_button.setEnabled(False)
        self.send_button.setText("Sending...")
        
        # Create worker thread
        self.worker = OpenAIWorker(self.messages.copy())
        self.worker.response_received.connect(self.handle_response)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.start()
    
    def handle_response(self, response):
        """Handle OpenAI API response"""
        self.add_chat_message(response, is_user=False)
        
        # Add to messages
        self.messages.append({
            "role": "assistant",
            "content": response
        })
        
        # Re-enable send button
        self.send_button.setEnabled(True)
        self.send_button.setText("Send")
    
    def handle_error(self, error_message):
        """Handle OpenAI API errors"""
        QMessageBox.critical(self, "Error", f"Failed to get response: {error_message}")
        
        # Re-enable send button
        self.send_button.setEnabled(True)
        self.send_button.setText("Send")


def main():
    app = QApplication(sys.argv)
    
    window = ChatWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()