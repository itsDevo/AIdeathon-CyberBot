import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, \
    QStackedWidget
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QTimer
from bot import Bot
import markdown2


class HomePage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        # Set up layout and appearance for the homepage
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Title label
        title_label = QLabel("Welcome to CyberBot")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #333333;")
        layout.addWidget(title_label)

        # Start button
        self.start_button = QPushButton("Start a New Chat")
        self.start_button.setFont(QFont("Arial", 14))
        self.start_button.setStyleSheet("""
                                        QPushButton {
                                            background-color: #5AA897; 
                                            color: white; 
                                            padding: 10px 20px; 
                                            border-radius: 8px;
                                        }
                                        QPushButton:hover {
                                            background-color: #4C8A75;
                                        }
                                         """)
        self.start_button.clicked.connect(self.go_to_chat)
        self.start_button.setDefault(True)  # Makes the button react to Enter
        layout.addWidget(self.start_button)

        self.setLayout(layout)

    def go_to_chat(self):
        self.stacked_widget.setCurrentIndex(1)  # Switch to the chat interface page


class chatInterFace(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        self.bot = Bot()
        # Set up the main layout
        layout = QVBoxLayout()

        self.timer = QTimer()  #Timer for text display

        # Chat display area
        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Arial", 12))
        self.chat_display.setStyleSheet("background-color: #F7F7F7; padding: 10px; border: 1px solid #DDDDDD;")
        layout.addWidget(self.chat_display)

        # User input area
        input_layout = QHBoxLayout()
        self.user_input = QLineEdit(self)
        self.user_input.setFont(QFont("Arial", 12))
        self.user_input.setPlaceholderText("Type your message here...")
        self.user_input.setStyleSheet("padding: 10px; border: 1px solid #DDDDDD; border-radius: 5px;")
        input_layout.addWidget(self.user_input)

        self.counter = 0
        self.user_text = ""

        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.setFont(QFont("Arial", 12))
        self.send_button.setStyleSheet("""
                                        QPushButton {
                                            background-color: #5AA897; 
                                            color: white; 
                                            padding: 10px 20px; 
                                            border-radius: 8px;
                                        }
                                        QPushButton:hover {
                                            background-color: #4C8A75;
                                        }
                                         """)

        self.user_input.returnPressed.connect(self.send_button.click)
        self.send_button.clicked.connect(self.handle_send_user_input)
        self.send_button.clicked.connect(self.on_click_disable)

        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)
        self.setLayout(layout)

    def display_conversation(self):
        # Get the welcome message from the bot and display it
        welcome_messages = self.bot.welcome_message()
        if self.counter == 0:
            if welcome_messages:
                for sender, message in welcome_messages:
                    self.chat_display.append(f"<b style='color: #5AA897;'>CyberBot:</b> {message}")
                    self.timer.singleShot(2000, self.handle_next_question)  #To show the first question

    def handle_next_question(self):
        self.counter += 1  # Increment counter here
        if self.counter <= 5:
            next_question = self.bot.next_question()
            sender, message = next_question[-1]
            self.chat_display.append(f"<b style='color: #5AA897;'>Question {self.counter}:</b> {message}")
        else:
            # Do nothing or display a message if necessary
            pass

    def handle_send_user_input(self):
        if self.counter <= 5:
            # Get user input and display it
            user_text = self.user_input.text()
            if user_text.strip() == "":
                return  # Avoid empty messages

            self.chat_display.append(f"<b style='color: #cf0202;'>You:</b> {user_text}")

    def handle_send_feedback(self):
        user_text = self.user_input.text()
        response = self.bot.generate_feedback(user_text)
        sender, message = response[-1]

        # Convert Markdown to HTML
        html_content = markdown2.markdown(message)
        self.chat_display.append(f"<b style='color: #5AA897;'>CyberBot:</b> {html_content}")
        self.user_input.clear()

        if self.counter < 5:
            self.timer.singleShot(1000, self.handle_next_question)
        else:
            # After the 5th feedback, show final messages and disable input
            self.chat_display.append(f"<b style='color: #5AA897;'>CyberBot:</b> Thank you for using CyberBot!")
            response = self.bot.get_final_grade()
            self.chat_display.append(f"<b style='color: #5AA897;'>CyberBot:</b> Your Quiz Result: {response}/5")
            self.chat_display.append(f"<b style='color: #5AA897;'>CyberBot:</b> Start a new chat!")
            self.user_input.setPlaceholderText("You have finished the test!")
            self.send_button.setDisabled(True)

    def on_click_disable(self):
        self.send_button.setText('Please Wait . . .')
        self.user_input.setPlaceholderText("Generating a new question . . .")
        self.send_button.setDisabled(True)
        self.timer.singleShot(1000, self.handle_send_feedback)
        self.timer.singleShot(4000, self.on_click_enable)
        # Removed the call to handle_next_question here

    def on_click_enable(self):  #Enables the send button again
        self.send_button.setEnabled(True)
        self.user_input.setPlaceholderText("Type your message here...")
        self.send_button.setText('Send')



class MainWindow(QWidget):
    def __init__(self, icon_path="icon.png"):
        super().__init__()

        # Set up the stacked widget
        self.stacked_widget = QStackedWidget()

        # Initialize pages
        self.home_page = HomePage(self.stacked_widget)
        self.chat_interface = chatInterFace(self.stacked_widget)

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.chat_interface)
        self.home_page.start_button.clicked.connect(self.chat_interface.display_conversation)

        # Set main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

        # Window settings
        self.setWindowTitle("CyberBot")
        self.setGeometry(250, 250, 800, 600)

        # Set the window icon
        self.setWindowIcon(QIcon(icon_path))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    icon_path = "__CyberBot.png"  # Update this path to the location of your icon file

    # Create the main window with the icon
    window = MainWindow(icon_path)
    window.show()
    sys.exit(app.exec_())
