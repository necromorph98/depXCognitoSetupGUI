from random import randint
import json

def create_policy(client, user_id, allowed_resources):
    # policy = {
    #     "Version": "2012-10-17",
    #     "Statement": [
    #         {
    #             "Sid": "VisualEditor0",
    #             "Effect": "Allow",
    #             "Action": "cognito-identity:GetCredentialsForIdentity",
    #             "Resource": "*"
    #         },
    #         {
    #             "Sid": "VisualEditor1",
    #             "Effect": "Allow",
    #             "Action": [
    #                 "ec2:DescribeInstanceTypes",
    #                 "ec2:DescribeInstances",
    #                 "ec2:StartInstances",
    #                 "ec2:RunInstances",
    #                 "ec2:StopInstances",
    #                 "ec2:CreateTags",
    #                 "ec2:CreateVpc",
    #                 "ec2:DescribeVpcs",
    #                 "ec2:CreateDefaultVpc",
    #                 "ec2:DescribeSecurityGroups",
    #                 "ec2:CreateSecurityGroup",
    #                 "ec2:AssociateSubnetCidrBlock",
    #                 "ec2:CreateSubnetCidrReservation",
    #                 "ec2:CreateDefaultSubnet",
    #                 "ec2:CreateSubnet",
    #                 "ec2:DescribeSubnets",
    #                 "ec2:DescribeKeyPairs"
    #             ],
    #             "Resource": "*"
    #         },
    #         {
    #             "Sid": "VisualEditor2",
    #             "Effect": "Allow",
    #             "Action": "iam:CreateServiceLinkedRole",
    #             "Resource": "*",
    #             "Condition": {
    #                 "StringEquals": {
    #                     "iam:AWSServiceName": [
    #                         "autoscaling.amazonaws.com",
    #                         "ec2scheduled.amazonaws.com",
    #                         "elasticloadbalancing.amazonaws.com",
    #                         "spot.amazonaws.com",
    #                         "spotfleet.amazonaws.com",
    #                         "transitgateway.amazonaws.com"
    #                     ]
    #                 }
    #             }
    #         },
    #         {
    #             "Sid": "VisualEditor3",
    #             "Effect": "Allow",
    #             "Action": [
    #                 "s3:GetBucketTagging",
    #                 "s3:ListAllMyBuckets",
    #                 "s3:ListBucketVersions",
    #                 "s3:CreateBucket",
    #                 "s3:ListBucket",
    #                 "s3:GetBucketVersioning",
    #                 "s3:GetBucketLocation"
    #             ],
    #             "Resource": "*"
    #         }
    #     ]
    # }
    
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": "cognito-identity:GetCredentialsForIdentity",
                "Resource": "*"
            },
            {
                "Sid": "VisualEditor1",
                "Effect": "Allow",
                "Action": "iam:CreateServiceLinkedRole",
                "Resource": "*",
                "Condition": {
                    "StringEquals": {
                        "iam:AWSServiceName": [
                            "autoscaling.amazonaws.com",
                            "ec2scheduled.amazonaws.com",
                            "elasticloadbalancing.amazonaws.com",
                            "spot.amazonaws.com",
                            "spotfleet.amazonaws.com",
                            "transitgateway.amazonaws.com"
                        ]
                    }
                }
            },
            {
                "Sid": "VisualEditor2",
                "Effect": "Allow",
                "Action": [],
                "Resource": "*"
            }
        ]
    }


    if 'ec2CheckBox' in allowed_resources:
        policy['Statement'][2]['Action'] += [
            "ec2:DescribeInstanceTypes",
            "ec2:DescribeInstances",
            "ec2:StartInstances",
            "ec2:RunInstances",
            "ec2:StopInstances",
            "ec2:CreateTags",
            "ec2:DescribeKeyPairs"
        ]

    if 'vpcCheckBox' in allowed_resources:
        policy['Statement'][2]['Action'] += [
            "ec2:CreateVpc",
            "ec2:DescribeVpcs",
            "ec2:CreateDefaultVpc",
        ]

    if 'sgCheckBox' in allowed_resources:
        policy['Statement'][2]['Action'] += [
            "ec2:DescribeSecurityGroups",
            "ec2:CreateSecurityGroup"
        ]

    if 'subnetCheckBox' in allowed_resources:
        policy['Statement'][2]['Action'] += [
            "ec2:AssociateSubnetCidrBlock",
            "ec2:CreateSubnetCidrReservation",
            "ec2:CreateDefaultSubnet",
            "ec2:CreateSubnet",
            "ec2:DescribeSubnets"
        ]
        
    if 's3CheckBox' in allowed_resources:
        policy['Statement'][2]['Action'] += [
            "s3:GetBucketTagging",
            "s3:ListAllMyBuckets",
            "s3:ListBucketVersions",
            "s3:CreateBucket",
            "s3:ListBucket",
            "s3:GetBucketVersioning",
            "s3:GetBucketLocation"
        ]

    response = client.create_policy(
        PolicyName=f'depx-policy-{user_id}',
        PolicyDocument=json.dumps(policy),
        Description='This policy gives permission to get credentials from web identity token'
    )

    policy_arn = response['Policy']['Arn']
    return policy_arn

def attach_policy_to_role(client, role_name, policy_arn):
    response = client.attach_role_policy(
        RoleName=role_name,
        PolicyArn=policy_arn
    )

def iam_role_exists(client, role_name):
    role_exists = False
    next_token = None

    response = client.list_roles(MaxItems=60)

    while True:
        # Check if the identity pool exists in the current batch
        for roles in response['Roles']:
            if roles['RoleName'] == role_name:
                role_exists = True
                break

        # Check if the identity pool was found or if there's more data to fetch
        if role_exists or 'Marker' not in response:
            break

        # Set the next token for the next iteration
        next_token = response['Marker']
        response = client.list_roles(MaxItems=60, Marker=next_token)

    return role_exists

def policy_exists(client, policy_arn):
    policy_exists = False
    next_token = None

    response = client.list_policies(
        Scope='Local',
        OnlyAttached=False,
        MaxItems=60
    )

    while True:
        # Check if the identity pool exists in the current batch
        for policies in response['Policies']:
            if policies['Arn'] == policy_arn:
                policy_exists = True
                break
        
        # Check if the identity pool was found or if there's more data to fetch
        if policy_exists or 'Marker' not in response:
            break

        # Set the next token for the next iteration
        next_token = response['Marker']
        response = client.list_policies(
            Scope='Local',
            OnlyAttached=False,
            Marker=next_token,
            MaxItems=60
        )

    return policy_exists