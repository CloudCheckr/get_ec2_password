# get_ec2_password
Get EC2 passwords with Keys stored in Secrets Manager

## Prerequisites

Python 3

### Optional
[gimme-aws-creds](https://github.com/Nike-Inc/gimme-aws-creds) a open source integration between Okta SSO and AWS IAM

## Installation

This is written in Python3

Clone the repository
```bash
git clone https://github.com/rslocum/get_ec2_password
cd get_ec2_password
```

Then Install in command line
```bash
python3 setup.py install
```

_OR_

Build with Docker
```bash
docker build -t get_ec2_password .
```

## Usage

### Uploading a PEM File

```bash
get-ec2-password -u -r <region> -f <file name> -d <directory -p <profile>
```
### Getting a EC2 Password
```bash
get-ec2-password -g -r <region> -f <file name> -d <directory -p <profile>
```

## TODO:
- create Windows cmd file
- get gimme-aws-creds working in docker
- add more functionality
