import json
import os
import random
import string

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QCheckBox, 
    QFileDialog, 
    QMainWindow
)

from lib.cleanup.cleanup import cleanup
from lib.cognito_identity.cognito_identity import (
    attach_role_to_identity_pool, 
    create_iam_role, 
    create_identity_pool
)
from lib.cognito_idp.cognito_idp import (
    create_user_pool,
    create_user_pool_client,
    create_user_pool_domain,
    create_user_pool_user,
    set_user_pool_user_password
)
from lib.credentials.credentials import (
    check_credentials_validity,
    check_csv_validity_in_file,
    get_aws_creds_path_from_user_data,
    store_credentials_to_env
)
from lib.ec2.ec2 import create_key_pair_ec2
from lib.helpers.helpers import create_clients
from lib.iam.iam import attach_policy_to_role, create_policy
from lib.vars.vars import (
    COGNITO_CALLBACK, 
    USER_DATA_DIR,
    USER_DATA_JSON_PATH, 
    USER_EC2_DIR
)

from lib.ui.register_window import RegisterDialog
from lib.ui.user_details import UserInfoUI

loader = QUiLoader()

class CreateWindowUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = loader.load("ui/setup_cognito.ui")
        self.checkbox_group = self.ui.awsGroupBox.findChildren(QCheckBox)
        self.ui.setWindowTitle("Cognito Setup for DepX")

        # Initialize Register Window
        self.register_window = RegisterDialog(self)

        # Load user data
        os.makedirs(USER_DATA_DIR, exist_ok=True)
        if not os.path.exists(USER_DATA_JSON_PATH):
            with open(USER_DATA_JSON_PATH, 'w') as f:
                f.write(json.dumps({
                    "description": "This file is used by depX Cognito Setup utitlity. Donot modify this file or risk breaking the app"
                }))
                f.close()
        
        file = open(USER_DATA_JSON_PATH, 'r')
        self.user_data = json.load(file)
        file.close()

        # Set button actions
        self.ui.uploadButton.clicked.connect(self.upload_file)
        self.ui.confirmButton.clicked.connect(self.confirm_selection)
        self.ui.clearLogsButton.clicked.connect(self.clear_logs)
        self.ui.setupButton.clicked.connect(self.create_user)
        self.ui.revertButton.clicked.connect(self.revert)
        self.ui.showStoredUserButton.clicked.connect(self.show_stored_user_data)

        # Track checkbox state changes
        for checkbox in self.checkbox_group:
            checkbox.stateChanged.connect(self.checkbox_state_changed)
        
        # Set default value of AWS Creds Path if present in user data
        aws_file_path = get_aws_creds_path_from_user_data()  
        if aws_file_path:
            self.ui.filePathTextBox.setText(aws_file_path)
            self.ui.awsGroupBox.setEnabled(True)
            self.ui.confirmButton.setEnabled(True)
            self.ui.logsList.addItem(f'Filepath Set: {aws_file_path}')
            
            response = check_csv_validity_in_file(aws_file_path)
            if response is None:
                self.ui.logsList.addItem("Error: Invalid CSV supplied. Please check your credentials file and try again.")
                return
            
            # Check validity of AWS Creds
            access_key, secret_key = response
            store_credentials_to_env(access_key, secret_key)
            
        self.ui.show()
        
    def clear_logs(self):
        self.ui.logsList.clear()
        
    def append_logs(self, text):
        current_text = self.ui.logsList.toPlainText()
        self.ui.logsList.setText(current_text + text)

    def upload_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName()

        if file_path:
            # Check if CSV format of credentials file is valid
            response = check_csv_validity_in_file(file_path)
            if response is None:
                self.ui.logsList.addItem("Error: Invalid CSV supplied. Please check your credentials file and try again.")
                return
            
            # Check validity of AWS Creds
            access_key, secret_key = response
            response = check_credentials_validity(access_key, secret_key)
            if response is None:
                self.ui.logsList.addItem("Error: Invalid AWS Credentials. Please check your credentials file and try again.")
                return
            
            self.ui.logsList.addItem(f"Account ID: {response['Account']}")
            self.ui.logsList.addItem(f"User Arn: {response['Arn']}")
            
            
            # Store AWS Creds
            store_credentials_to_env(access_key, secret_key) 
            
            self.ui.logsList.addItem(f'Filepath Set: {file_path}')
            self.ui.filePathTextBox.setText(file_path)
            self.ui.awsGroupBox.setEnabled(True)
            self.ui.confirmButton.setEnabled(True)
            

    def checkbox_state_changed(self, state):
        self.ui.setupButton.setEnabled(False)

    def confirm_selection(self):
        data = []
        for checkbox in self.checkbox_group:
            if checkbox.isChecked():
                data.append(checkbox.objectName())

        if not data:
            self.ui.logsList.addItem("Please select atleast one resource!")
        else:     
            """ file = open(USER_DATA_JSON_PATH, 'r')
            user_data = json.load(file)
            user_data["enabledResources"] = data
            file.close()
            
            with open(USER_DATA_JSON_PATH, 'w') as file:
                json.dump(user_data, file) """
            
            self.user_data["enabledResources"] = data
            self.ui.setupButton.setEnabled(True)
            self.ui.revertButton.setEnabled(True)
        
    def show_stored_user_data(self):
        # file = open(USER_DATA_JSON_PATH, 'r')
        # user_data = json.load(file)
        # file.close()
        
        # self.uinfo.load_json_data(json.dumps({"key": "value"}))        
        self.uinfo = UserInfoUI(self, self.user_data)
        self.uinfo.load_json_data()
        
    def open_register_window(self):
        self.register_window.register_successful.connect(self.handle_register_successful)
        self.register_window.open_register_window()
            
    def create_user(self): 
        self.ui.setupButton.setEnabled(False)
        self.ui.revertButton.setEnabled(False)       
        self.user_data["AwsCredsPath"] = self.ui.filePathTextBox.toPlainText()
        self.open_register_window()    
        
    def handle_register_successful(self, cognito_credentials):
        try:
            self.register_window.ui.close()
            self.user_data["CognitoUsername"] = cognito_credentials["username"]
            self.user_data["CognitoPassword"] = cognito_credentials["password"]
            
            clients = create_clients()
            if clients is None:
                self.ui.logsList.addItem("Error: AWS Credentials not found in environment variables")
                return 
            
            cognito_idp_client, cognito_identity_pool_client, iam_client, ec2_client = clients 
            user_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=14)) 
            self.user_data["CognitoUserID"] = user_id
            
            self.ui.logsList.addItem("Creating User Pool...")
            self.user_data["CognitoUserPoolID"] = create_user_pool(cognito_idp_client, user_id)
            
            self.ui.logsList.addItem("Creating User Pool Client...")
            self.user_data["CognitoUserPoolClientID"] = create_user_pool_client(cognito_idp_client, self.user_data["CognitoUserPoolID"], COGNITO_CALLBACK, user_id)
            
            self.ui.logsList.addItem("Creating User Pool Domain...")
            self.user_data["CognitoUserPoolDomain"] = create_user_pool_domain(cognito_idp_client, self.user_data["CognitoUserPoolID"], user_id)
            
            self.ui.logsList.addItem("Creating Userpool User...")
            create_user_pool_user(cognito_idp_client, self.user_data["CognitoUserPoolID"], self.user_data["CognitoUsername"])
            
            self.ui.logsList.addItem("Setting Userpool User Password...")
            set_user_pool_user_password(cognito_idp_client, self.user_data["CognitoUserPoolID"], self.user_data["CognitoUsername"], self.user_data["CognitoPassword"])
            
            self.ui.logsList.addItem("Creating Identity Pool...")
            self.user_data["IdentityPoolID"] = create_identity_pool(cognito_identity_pool_client, self.user_data["CognitoUserPoolID"], self.user_data["CognitoUserPoolClientID"], user_id)
            
            self.ui.logsList.addItem("Creating IAM Role...")
            self.user_data["RoleArn"], self.user_data["RoleName"] = create_iam_role(iam_client, self.user_data["IdentityPoolID"], user_id)
            
            self.ui.logsList.addItem("Creating IAM Policy...")
            self.user_data["PolicyArn"] = create_policy(iam_client, user_id, self.user_data["enabledResources"])
            
            self.ui.logsList.addItem("Attaching Policy to IAM Role...")
            attach_policy_to_role(iam_client, self.user_data["RoleName"], self.user_data["PolicyArn"])
            
            self.ui.logsList.addItem("Attaching IAM Role to Identity Pool...")
            attach_role_to_identity_pool(cognito_identity_pool_client, self.user_data["IdentityPoolID"], self.user_data["RoleArn"])
            
            self.ui.logsList.addItem("Creating EC2 Key Pair...")
            os.makedirs(USER_EC2_DIR, exist_ok=True)
            ec2_key_file = os.path.join(USER_EC2_DIR, f'depx-keypair-ec2-{user_id}.pem')
            keydata = create_key_pair_ec2(ec2_client, user_id)
            with open(ec2_key_file, 'w') as file:
                file.write(keydata)
            self.user_data["EC2KeyPairLoc"] = ec2_key_file
            
            self.user_data["enabledUser"] = True
            
            file = open(USER_DATA_JSON_PATH, 'w')
            json.dump(self.user_data, file)
            file.close()
        
        except Exception as e:
            self.ui.logsList.addItem(f"Error: {e}")
            self.ui.logsList.addItem("Reverting....")
            
            self.revert(error=True)
            
            file = open(USER_DATA_JSON_PATH, 'w')
            json.dump(self.user_data, file)
            file.close()

        self.ui.setupButton.setEnabled(True)
        self.ui.revertButton.setEnabled(True) 
        
    def revert(self, error=False):
        self.ui.setEnabled(False)
        try:
            if not error:
                if not self.user_data["enabledUser"]:
                    self.ui.logsList.addItem("Warning: No user details stored!")
                    self.ui.setEnabled(True)
                    return
            
            clients = create_clients()
            if clients is None:
                self.ui.logsList.addItem("Error: AWS Credentials not found in environment variables")
                self.ui.setEnabled(True)
                return 
            
            cleanup(clients, self.user_data, self.ui)
            
            file = open(USER_DATA_JSON_PATH, 'w')
            self.user_data["enabledUser"] = False
            json.dump(self.user_data, file)
            self.ui.logsList.addItem("Cleanup Successful!")
        except Exception as e:
            self.ui.logsList.addItem(f"Error: {e}")
        
        self.ui.setEnabled(True)
        
    def show(self):
        self.ui.show()


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     test = LoginDialog()
#     test.open_register_window()
#     sys.exit(app.exec())