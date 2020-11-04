# get_ec2_password

# Gets the windows password from a pem file stored in Secrets Manage, reducing the need for locally stored pem files.
# rslocum 10/29/2020

import argparse
import os
import re
import json
import boto3
import base64
import rsa
from botocore.exceptions import ClientError


def parse():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Script to retrieve EC2 passwords")

    parser.add_argument("-i", "--instanceid", help="instance id of ec2 instance")
    parser.add_argument("-p", "--profile", help="aws profile to use")
    parser.add_argument("-g", "--gac-profile", help="Run gimme-aws-creds against given profile")
    parser.add_argument("-r", "--region", help="aws region")

    return parser.parse_args()


def start_client(service, profile, region):
    try:
        # Create a ACM client
        session = boto3.session.Session(profile_name=profile)
        client = session.client(
            service_name=service,
            region_name=region
        )
        return client
    except:
        print("Something bad happened")


def get_secret(client, pem_file):
    secret_name = 'pem/' + pem_file
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            print("InternalServiceErrorException")
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            print("InvalidParameterException")
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            print("InvalidRequestException")
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            print("ResourceNotFoundException")
            raise e
    else:
        # Secrets Manager decrypts the secret value using the associated KMS CMK
        # Depending on whether the secret was a string or binary, only one of these fields will be populated
        if 'SecretString' in get_secret_value_response:
            secret_data = get_secret_value_response['SecretString']
        else:
            secret_data = get_secret_value_response['SecretBinary']
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
        stream = os.popen('gimme-aws-creds -p %s' % args.gac_profile)
        output = stream.read()
        aws_profile = re.search('(.*)Written profile (.*) to (.*)', output).group(2)
        print("profile used: %s" % aws_profile)
        stream.close()

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

