
from PySide6 import QtCore
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QWidget, 
    QLineEdit,
    QMessageBox
)

from lib.credentials.validate import validate_email, validate_password

loader = QUiLoader()


class RegisterDialog(QWidget):
    register_successful = QtCore.Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = loader.load("ui/set_username_password.ui")
        self.ui.setWindowTitle("Cognito Username and Password")
        
        self.ui.showPasswordCheck.stateChanged.connect(self.toggle_password_visibility)
        self.ui.createAccountButton.clicked.connect(self.validate_credentials)
        self.ui.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        
        self.ui.usernameEdit.setText("test@gmail.com")
        self.ui.passwordEdit.setText("Test@password123")
        self.ui.confirmPasswordEdit.setText("Test@password123")

    def toggle_password_visibility(self, state):
        password_visibility = QLineEdit.Normal if state == 2 else QLineEdit.Password
        self.ui.passwordEdit.setEchoMode(password_visibility)
        self.ui.confirmPasswordEdit.setEchoMode(password_visibility)

    def validate_credentials(self):
        username = self.ui.usernameEdit.text()
        password = self.ui.passwordEdit.text()
        confirm_password = self.ui.confirmPasswordEdit.text()

        if not username:
            self.show_error_message('Username cannot be empty')
            return
        
        if not validate_email(username):
            self.show_error_message('Username should be a valid email address')
            return

        if not validate_password(password):
            self.show_error_message('Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character')
            return

        if not password or not confirm_password:
            self.show_error_message('Password and Confirm Password cannot be empty')
            return

        if password != confirm_password:
            self.show_error_message('Password and Confirm Password do not match')
            return

        # If all validations pass, store the credentials in environment variables
        # os.environ['COGNITO_USERNAME'] = username
        # os.environ['COGNITO_PASSWORD'] = password
        
        self.register_successful.emit({
            'username': username,
            'password': password
        })
        
        # self.register_successful.accept()
            
    def show_error_message(self, message):
        error_message_box = QMessageBox(self)
        error_message_box.setIcon(QMessageBox.Critical)
        error_message_box.setWindowTitle('Error')
        error_message_box.setText(message)
        error_message_box.exec()

    def open_register_window(self):
        self.ui.show()