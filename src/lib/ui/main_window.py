
from PySide6 import QtCore
from PySide6.QtUiTools import QUiLoader


loader = QUiLoader()

class MainWindowUI(QtCore.QObject):
    def __init__(self):
        super().__init__()
        self.ui = loader.load("ui/main_window.ui", None)
        self.ui.setWindowTitle("Cognito Setup for DepX")

    def show(self):
        self.ui.show()