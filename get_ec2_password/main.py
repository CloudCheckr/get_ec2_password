import argparse
import os
from get_ec2_password import get, upload
from get_ec2_password.shared import gimme_creds_connection


class Configuration(object):
    pass


def parse():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Script to upload pem files to Secrets Manager, and retrieve passwords for EC2")

    # Upload Flags
    parser.add_argument('-u', '--upload-pem', action='store_true', help='Flag to upload a PEM file')
    parser.add_argument('-f', '--filename', help='File to upload')
    parser.add_argument('-d', '--directory', help='File location')
    parser.add_argument('-k', '--kmskey', help='KMS Key to use, if not default')

    # Retrieve Flags
    parser.add_argument('-g', '--get-password', action='store_true', help='Flag to retrieve a password')
    parser.add_argument('-i', '--instanceid', help='instance id of ec2 instance')

    # Shared Flags
    parser.add_argument('-p', '--profile', help='aws profile to use')
    parser.add_argument('--gac-profile', '--gac', help='Run gimme-aws-creds against given profile')
    parser.add_argument('-r', '--region', help='aws region')

    args = parser.parse_args()

    if not args.get_password and not args.upload_pem:
        raise Exception('Missing Upload or Get Flag')
    elif args.get_password and args.upload_pem:
        raise Exception('Cannot Have Both Upload and Get Flags')
    else:
        return args


def main(args):
    conf = Configuration()
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

    conf.aws_profile = aws_profile
    conf.aws_region = aws_region

    if args.get_password:
        conf.instanceid = args.instanceid
        get.run(conf)

    if args.upload_pem:
        if args.directory:
            path = args.directory
        else:
            path = '..'

        if args.kmskey:
            kms = args.kmskey
        else:
            kms = None
        conf.filename = args.filename
        conf.path = path
        conf.kms = kms
        upload.run(conf)




if __name__ == "__main__":
    try:
        main(parse())
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
