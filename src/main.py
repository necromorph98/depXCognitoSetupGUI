import sys

from PySide6.QtWidgets import QApplication
from lib.ui.setup_cognito_window import CreateWindowUI

if __name__ == "__main__":
    app = QApplication(sys.argv) 
    main_window = CreateWindowUI()
    app.setApplicationName("Cognito Setup for DepX")
    app.exec() 