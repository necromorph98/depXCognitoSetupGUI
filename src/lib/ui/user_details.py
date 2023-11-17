import json
from PySide6 import QtCore
from PySide6.QtWidgets import QWidget, QVBoxLayout, QVBoxLayout, QWidget, QTextEdit, QApplication, QMessageBox, QLineEdit
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPalette, QColor, Qt

# from lib.vars.vars import USER_DATA_JSON_PATH
loader = QUiLoader()

class UserInfoUI(QWidget):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.parentWindow = parent
        self.data = data
        self.ui = loader.load("ui/user_details_window.ui")
        self.ui.setWindowTitle("User Details")
        self.ui.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        pallete = QPalette()
        self.ui.userStatusLine.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        
        if self.data["enabledUser"]:
            pallete.setColor(QPalette.Base, QColor(51, 209, 122))
            self.ui.userStatusLine.setPalette(pallete)
            self.ui.userStatusLine.setText("USER ENABLED")
        else:
            pallete.setColor(QPalette.Base, QColor(255, 0, 0))
            self.ui.userStatusLine.setPalette(pallete)
            self.ui.userStatusLine.setText("USER DELETED!")
        
        self.ui.cognitoUserIDLine.setText(self.data.get("CognitoUserID", None))
        self.ui.cognitoUserPoolClientIDLine.setText(self.data.get("CognitoUserPoolClientID", None))
        self.ui.identityPoolIDLine.setText(self.data.get("IdentityPoolID", None))
        
        self.ui.cognitoUsernameLine.setText(self.data.get("CognitoUsername", None))
        self.ui.cognitoPasswordLine.setText(self.data.get("CognitoPassword", None))
        self.ui.awsCredsPathLine.setText(self.data.get("AwsCredsPath", None))
        self.ui.cognitoUserPoolIDLine.setText(self.data.get("CognitoUserPoolID", None))
        self.ui.cognitoUserPoolDomainLine.setText(
            f"https://{self.data.get("CognitoUserPoolDomain", None)}.auth.ap-south-1.amazoncognito.com"
        )
        self.ui.roleArnLine.setText(self.data.get("RoleArn", None))
        self.ui.roleNameLine.setText(self.data.get("RoleName", None))
        self.ui.policyArnLine.setText(self.data.get("PolicyArn", None))
        self.ui.ec2KeyPairLocLine.setText(self.data.get("EC2KeyPairLoc", None))
        
        num_rows = self.ui.gridLayout_2.rowCount()  
        line_edits = [self.ui.gridLayout_2.itemAtPosition(row, 1).widget() for row in range(num_rows)] 
        copy_buttons = [self.ui.gridLayout_2.itemAtPosition(row, 2).widget() for row in range(num_rows)]
        
        # for line_edit, copy_button in zip(self.line_edits, self.copy_buttons):
        #     copy_button.clicked.connect(lambda: self.copy_text(line_edit))
        
        for row in range(num_rows):
            copy_buttons[row].clicked.connect((lambda i=line_edits[row].text(): lambda: self.copy_text(i))())
    
    def copy_text(self, line_edit):
        clipboard = QApplication.clipboard()
        clipboard.clear(mode=clipboard.Mode.Clipboard)
        clipboard.setText(line_edit, mode=clipboard.Mode.Clipboard)
    

    # def copy_line_edit_content(self, line_edit):
    #     copied_content = line_edit.text()
    #     print(f"Copied Content: {copied_content}")

    def load_json_data(self):  
        self.ui.show()
        


# if __name__ == "__main__":
#     app = QApplication([])
#     ui = UserInfoUI()
#     ui.load_json_data(json.dumps({"key": "value"}))
#     app.exec()