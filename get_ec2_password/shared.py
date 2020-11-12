import re
import os
import boto3
from botocore.exceptions import ProfileNotFound


def start_client(service, profile, region):
    try:
        # Create a ACM client
        session = boto3.session.Session(profile_name=profile)
        client = session.client(
            service_name=service,
            region_name=region
        )
        return client
    except ProfileNotFound as e:
        raise e


def gimme_creds_connection(profile):
    try:
        stream = os.popen('gimme-aws-creds -p %s' % profile)
        output = stream.read()
        aws_profile = re.search('(.*)Written profile (.*) to (.*)', output).group(2)
        print("profile used: %s" % aws_profile)
        stream.close()
        return aws_profile
    except:
        error = "Error Getting Credentials"
        print(error)
        raise error


# Central Location for Error Handling
# Modified from https://docs.aws.amazon.com/code-samples/latest/catalog/python-secretsmanager-secrets_manager.py.html
def sm_error_responses(error_response):
    if hasattr(error_response, 'response'):
        if error_response.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            raise Exception("InternalServiceErrorException")
        elif error_response.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            raise Exception("InvalidParameterException")
        elif error_response.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            raise Exception("InvalidRequestException")
        elif error_response.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            raise Exception("PEM Secret Not Found")
        elif error_response.response['Error']['Code'] == 'ResourceExistsException':
            # We can't find the resource that you asked for.
            raise Exception("PEM Secret Already Exist")
        else:
            raise Exception(error_response.response)
    else:
        raise Exception(error_response)
