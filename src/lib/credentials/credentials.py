import json
import boto3
import os
import csv

from lib.vars.vars import USER_DATA_DIR, USER_DATA_JSON, USER_DATA_JSON_PATH
from lib.exceptions.exceptions import InvalidCSVFormat, InvalidCredentialsError

def get_aws_creds_path_from_user_data():
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    
    if not os.path.exists(USER_DATA_JSON_PATH):
        with open(USER_DATA_JSON_PATH, 'w') as f:
            f.write(json.dumps({
                "description": "This file is used by depX Cognito Setup utitlity. Donot modify this file or risk breaking the app"
            }))
            f.close()
            return None
        
    with open(USER_DATA_JSON_PATH, 'r') as f:
        data = json.load(f)
        return data.get('AwsCredsPath', None)
            


def validate_user_data_json(dir, path):
    os.makedirs(dir, exist_ok=True)

    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(json.dumps({
                "description": "This file is used by depX Cognito Setup utitlity. Donot modify this file or risk breaking the app"
            }))
            f.close()


def check_csv_validity_in_file(filename):
    try:
        with open(filename, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            
            next(csv_reader)
            
            for row in csv_reader:

                if len(row) != 2:
                    raise InvalidCSVFormat

                access_key = row[0].strip()
                secret_key = row[1].strip()
                
                return access_key, secret_key
            
    except Exception as e:
        return None
    
def check_credentials_validity(access_key, secret_key):
    try:
        # Create a Boto3 client using the credentials
        client = boto3.client(
            'sts',
            region_name='ap-south-1',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )

        # Use the client to make a simple API call to AWS
        response = client.get_caller_identity()

        if not response['Arn']:
            return None

        return response
    
    except Exception as e:
        return None


def store_credentials_to_env(access_key, secret_key):
    os.environ['AWS_ACCESS_KEY_ID'] = access_key
    os.environ['AWS_SECRET_ACCESS_KEY'] = secret_key