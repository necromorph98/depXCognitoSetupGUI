import os

def create_key_pair_ec2(client, userid):
    response = client.create_key_pair(
        KeyName=f'depx-ec2-keypair-{userid}',
        TagSpecifications=[
            {
                'ResourceType': 'key-pair',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': f'depx-ec2-keypair-{userid}'
                    },
                ]
            },
        ]
    )

    return response['KeyMaterial']


def delete_key_pair_ec2(client, userid):
    response = client.delete_key_pair(
        KeyName=f'depx-ec2-keypair-{userid}'
    )


def key_exists(client, userid):
    try:
        response = client.describe_key_pairs(
            KeyNames=[
                f'depx-ec2-keypair-{userid}',
            ]
        )
        return True
    except Exception as e:
        return False