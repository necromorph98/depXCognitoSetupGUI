import os
from lib.cognito_idp.cognito_idp import user_pool_exists
from lib.cognito_identity.cognito_identity import identity_pool_exists
from lib.iam.iam import iam_role_exists, policy_exists
from lib.ec2.ec2 import delete_key_pair_ec2, key_exists, delete_key_pair_ec2

def cleanup(clients, vals, ui):
    cognito_idp_client, cognito_identity_pool_client, iam_client, ec2_client = clients
    
    if 'CognitoUserPoolID' in vals:
        if user_pool_exists(cognito_idp_client, vals['CognitoUserPoolID']):
            if 'CognitoUserPoolDomain' in vals:
                ui.logsList.addItem("Deleting user pool domain...")
                response = cognito_idp_client.delete_user_pool_domain(
                    Domain=vals['CognitoUserPoolDomain'],
                    UserPoolId=vals['CognitoUserPoolID']
                )

            ui.logsList.addItem("Deleting user pool...")
            cognito_idp_client.delete_user_pool(UserPoolId=vals['CognitoUserPoolID'])
        else:
            ui.logsList.addItem("User pool doesn't exist or has already been deleted")        
        
    if 'IdentityPoolID' in vals:
        if identity_pool_exists(cognito_identity_pool_client, vals['IdentityPoolID']):
            ui.logsList.addItem("Deleting identity pool...")
            cognito_identity_pool_client.delete_identity_pool(IdentityPoolId=vals['IdentityPoolID'])
        else:
            ui.logsList.addItem("Identity pool doesn't exist or has already been deleted")

    if 'PolicyArn' in vals or 'RoleName' in vals:
        if policy_exists(iam_client, vals['PolicyArn']) and iam_role_exists(iam_client, vals['RoleName']):
            ui.logsList.addItem("Detaching IAM policy from IAM role...")
            response = iam_client.detach_role_policy(
                RoleName=vals['RoleName'],
                PolicyArn=vals['PolicyArn']
            )
        else:
            ui.logsList.addItem("IAM policy or IAM role doesn't exist or has already been deleted")

        if policy_exists(iam_client, vals['PolicyArn']):
            ui.logsList.addItem("Deleting IAM policy...")
            response = iam_client.delete_policy(
                PolicyArn=vals['PolicyArn']
            )
        else:
            ui.logsList.addItem("IAM policy doesn't exist or has already been deleted")
        
        if iam_role_exists(iam_client, vals['RoleName']):
            ui.logsList.addItem("Deleting IAM role...")
            iam_client.delete_role(RoleName=vals['RoleName'])
        else:
            ui.logsList.addItem("IAM role doesn't exist or has already been deleted")

    if 'EC2KeyPairLoc' in vals:
        if os.path.exists(vals['EC2KeyPairLoc']):
            os.remove(vals['EC2KeyPairLoc'])
        if key_exists(ec2_client, vals['CognitoUserID']):
            delete_key_pair_ec2(ec2_client, vals['CognitoUserID'])
        else:
            ui.logsList.addItem("Key pair doesn't exist or has already been deleted")
            
    
            
    