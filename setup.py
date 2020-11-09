from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='get_ec2_password',
    version='0.1.1',
    package_dir={'': 'get_ec2_password'},
    scripts=['bin/get-ec2-password'],
    install_requires=requirements,
    url='https://github.com/rslocum/get_ec2_password',
    license='',
    author='Rob Slocum',
    author_email='rob.e.slocum@gmail.com',
    description='Scripts to retrieve EC2 passwords from AWS Secrets Manager',
    console=['main.py']
)
