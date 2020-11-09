from setuptools import setup

setup(
    name='get_ec2_password',
    version='0.1.1',
    package_dir={'': 'get_ec2_password'},
    install_requires=[
        'rsa',
        'argparse',
        'boto3',
        'botocore'
    ],
    url='https://github.com/rslocum/get_ec2_password',
    license='',
    author='Rob Slocum',
    author_email='rob.e.slocum@gmail.com',
    description='Scripts to retrieve EC2 passwords from AWS Secrets Manager',
    console=['main.py']
)
