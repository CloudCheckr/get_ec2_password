# upload_pem_secret

# Stores a pem file in Secrets Manage, to be used by other scripts to retrieve, reducing the need for locally stored pem files.
# rslocum 11/04/2020

import os
from botocore.exceptions import ClientError
from get_ec2_password.shared import start_client, sm_error_responses


def get_pem_data(location, pem_name):
    try:
        file = location + '/' + pem_name
        pem_data = open(file, "r")
    except OSError as e:
        raise e
    else:
        return pem_data.read()


def create_secret(client, pem_data, pem_name, key):
    try:
        secret_name = 'pem/' + pem_name.replace('.pem', '')
        if key:
            response = client.create_secret(
                Name=secret_name,
                Description='Pem File ' + pem_name,
                KmsKeyId=key,
                SecretString=pem_data,
                Tags=[
                    {
                        'Key': 'Type',
                        'Value': 'PEM File'
                    },
                ]
            )
        else:
            response = client.create_secret(
                Name=secret_name,
                Description='Pem File ' + pem_name,
                SecretString=pem_data,
                Tags=[
                    {
                        'Key': 'Type',
                        'Value': 'PEM File'
                    },
                ]
            )
    except ClientError as e:
        sm_error_responses(e)
    else:
        return response


def run(conf):
    sm_session = start_client('secretsmanager', conf.aws_profile, conf.aws_region)
    pem_contents = get_pem_data(conf.path, conf.filename)
    response = create_secret(sm_session, pem_contents, conf.filename, conf.kms)

    print(response)
