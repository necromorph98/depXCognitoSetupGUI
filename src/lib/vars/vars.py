import os
import sys

SERVER_NAME      = 'depx.in'
AWS_AUTH_URL     = f'https://api.{SERVER_NAME}/aws'
COGNITO_CALLBACK = f'{AWS_AUTH_URL}/cognito-credentials/callback'


USER_DATA_DIR = "user_data"
USER_DATA_JSON = "user_data.json"
USER_DATA_JSON_PATH = os.path.join(USER_DATA_DIR, USER_DATA_JSON)

USER_EC2_DIR = "ec2_key"

