# get_ec2_password

# Gets the windows password from a pem file stored in Secrets Manage,
# reducing the need for locally stored pem files.
# rslocum 10/29/2020

import base64

import rsa
from botocore.exceptions import ClientError

from get_ec2_password.shared import sm_error_responses, start_client

# Connect to Secrets Manager and get the PEM File data
# Modified from https://docs.aws.amazon.com/code-samples/latest/catalog/python-secretsmanager-secrets_manager.py.html
def get_secret(client, pem_file):
    secret_name = 'pem/' + pem_file
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        sm_error_responses(e)
    else:
        # Secrets Manager decrypts the secret value using
        # the associated KMS CMK.
        # Depending on whether the secret was a string or binary
        # only one of these fields will be populated
        if 'SecretString' in get_secret_value_response:
            secret_data = get_secret_value_response['SecretString']
        else:
            e = "Invalid Pem Format"
            print(e)
            raise e
        if isinstance(secret_data, str):
            return rsa.PrivateKey.load_pkcs1(secret_data)
        else:
            e = "Unexpected PEM Format, use upload_pem_secret to create0"
            raise Exception(e)


# get pem key from ec2
def get_pem_name(client, instance_id):
    try:
        instance = client.describe_instances(
            Filters=[
                {
                    'Name': 'instance-id',
                    'Values': [
                        instance_id,
                    ]
                },
            ]
        )
    except ClientError as e:
        raise e
    # Making sure instance data was returned
    if len(instance['Reservations']) > 0:
        # digging the value out of the response format
        pem_name = ((((instance['Reservations'])[0])['Instances'])[0])['KeyName']
        return pem_name
    else:
        raise Exception("Instance " + instance_id + " not found")


# get the password from ec2
# From https://quackajack.wordpress.com/2016/12/12/decrypting-aws-windows-passwords/
def get_ec2_password(client, pem_file, instance_id):
    try:
        encrypted_password = base64.b64decode(
            (client.get_password_data(InstanceId=instance_id))['PasswordData'])
        if encrypted_password:
            password = rsa.decrypt(encrypted_password, pem_file)
        else:
            raise Exception("No Password returned, Instance may not be ready yet")
    except ValueError as e:
        raise e

    return str(password, 'utf-8')


def run(conf):

    ec2_session = start_client('ec2', conf.aws_profile, conf.aws_region)
    sm_session = start_client(
        'secretsmanager',
        conf.aws_profile,
        conf.aws_region
    )
    pem_file = get_pem_name(ec2_session, conf.instanceid)
    pem_contents = get_secret(sm_session, pem_file)
    ec2_password = get_ec2_password(ec2_session, pem_contents, conf.instanceid)

    print(ec2_password)
