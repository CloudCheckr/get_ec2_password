# get_ec2_password

# Gets the windows password from a pem file stored in Secrets Manage, reducing the need for locally stored pem files.
# rslocum 10/29/2020

import argparse
import base64
import json
import os
import rsa
from botocore.exceptions import ClientError
from password_functions import start_client, gimme_creds_connection, sm_error_responses


def parse():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Script to retrieve EC2 passwords")

    parser.add_argument("-i", "--instanceid", help="instance id of ec2 instance")
    parser.add_argument("-p", "--profile", help="aws profile to use")
    parser.add_argument("-g", "--gac-profile", help="Run gimme-aws-creds against given profile")
    parser.add_argument("-r", "--region", help="aws region")

    return parser.parse_args()


def get_secret(client, pem_file):
    secret_name = 'pem/' + pem_file
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        sm_error_responses(e)
    else:
        # Secrets Manager decrypts the secret value using the associated KMS CMK
        # Depending on whether the secret was a string or binary, only one of these fields will be populated
        if 'SecretString' in get_secret_value_response:
            secret_data = get_secret_value_response['SecretString']
        else:
            e = "Invalid Pem Format"
            print(e)
            raise e
        secret_dict = json.loads(secret_data)
        formatted_pem = secret_dict['PrivateKey'] \
            .replace('BEGIN RSA PRIVATE KEY-----', 'BEGIN RSA PRIVATE KEY-----\n') \
            .replace('-----END RSA PRIVATE KEY', '\n-----END RSA PRIVATE KEY')
        key = rsa.PrivateKey.load_pkcs1(formatted_pem)
        return key


# get pem key from ec2
def get_pem_name(client, instance_id):
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
    # digging the value out of the response format
    pem_name = ((((instance['Reservations'])[0])['Instances'])[0])['KeyName']
    return pem_name


# get the password from ec2
def get_ec2_password(client, pem_file, instance_id):
    try:
        encrypted_password = base64.b64decode((client.get_password_data(InstanceId=instance_id))['PasswordData'])
        password = rsa.decrypt(encrypted_password, pem_file)
    except ValueError as e:
        raise e

    return str(password, 'utf-8')


def main(args):
    if args.profile:
        aws_profile = args.profile
    elif args.gac_profile:
        aws_profile = gimme_creds_connection(args.gac_profile)
    else:
        aws_profile = 'default'

    if args.region:
        aws_region = args.region
    else:
        aws_region = os.getenv('AWS_DEFAULT_REGION')

    ec2_session = start_client('ec2', aws_profile, aws_region)
    sm_session = start_client('secretsmanager', aws_profile, aws_region)
    pem_file = get_pem_name(ec2_session, args.instanceid)
    pem_contents = get_secret(sm_session, pem_file)
    ec2_password = get_ec2_password(ec2_session, pem_contents, args.instanceid)

    print(ec2_password)


if __name__ == "__main__":
    try:
        main(parse())
    except KeyboardInterrupt:
        print("KeyboardInterrupt")

