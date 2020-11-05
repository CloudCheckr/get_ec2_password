# upload_pem_secret

# Stores a pem file in Secrets Manage, to be used by other scripts to retrieve, reducing the need for locally stored pem files.
# rslocum 11/04/2020

import argparse
import os
from botocore.exceptions import ClientError
from password_functions import start_client, gimme_creds_connection, sm_error_responses

def parse():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Script to upload pem files to Secrets Manager")

    parser.add_argument("-f", "--filename", help="File to upload")
    parser.add_argument("-d", "--directory", help="File location")
    parser.add_argument("-k", "--kmskey", help="KMS Key to use, if not default")
    parser.add_argument("-p", "--profile", help="aws profile to use")
    parser.add_argument("-g", "--gac-profile", help="Run gimme-aws-creds against given profile")
    parser.add_argument("-r", "--region", help="aws region")

    return parser.parse_args()

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

    if args.directory:
        path = args.directory
    else:
        path = '.'

    if args.kmskey:
        kms = args.kmskey
    else:
        kms = None

    sm_session = start_client('secretsmanager', aws_profile, aws_region)
    pem_contents = get_pem_data(path, args.filename)
    response = create_secret(sm_session, pem_contents, args.filename, kms)

    print(response)


if __name__ == "__main__":
    try:
        main(parse())
    except KeyboardInterrupt:
        print("KeyboardInterrupt")