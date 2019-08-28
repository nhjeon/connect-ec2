import getopt
import os
import boto3
import sys
from botocore.exceptions import ClientError, ProfileNotFound, NoCredentialsError


def get_aws_client(profile='default'):
    try:
        session = boto3.session.Session(profile_name=profile)
        return session.client('ec2')
    except ProfileNotFound as err:
        print(err)
        print("ProfileNotFound: Profile(~/.aws/config) should be created by AWS CLI")
        sys.exit()


def select_ec2(ec2_list):
    for i in range(len(ec2_list)):
        print('{:>0}:  {:<32}  {:<50}'.format(i, ec2_list[i][0], ec2_list[i][2]))
    selection = input("select number you want to connect: ")
    selection = int(selection)
    if selection >= len(ec2_list):
        print("invalid number")
        sys.exit()
    return ('ssh -i "{}.pem" ec2-user@{}'.format(ec2_list[selection][1], ec2_list[selection][2]))


def get_ec2_list(client):
    try:
        ec2_list = client.describe_instances()
        result = []
        for res in ec2_list['Reservations']:
            for ins in res['Instances']:
                if ins['State']['Name'] == 'running':
                    tags = list(filter(lambda x: x['Key'] == 'Name', ins['Tags']))
                    if tags:
                        result.append((tags[0]['Value'], ins['KeyName'], ins['PublicDnsName']))
        return result
    except ClientError as err:
        print(err)
        sys.exit()
    except NoCredentialsError as err:
        print(err)
        print("NoCredentialsError: Credentials(~/.aws/credentials) should be created by AWS CLI")
        sys.exit()


def main(argv):
    print("usage: connect-ec2 -p <profile>")

    profile = None

    opts, args = getopt.getopt(argv, "p:")

    for opt, arg in opts:
        if opt in "-p":
            profile = arg

    if profile is not None:
        print("profile: " + profile)
    else:
        print("default profile: default")

    client = get_aws_client(profile)
    ec2_list = get_ec2_list(client)
    cmd = select_ec2(ec2_list)
    os.system(cmd)

if __name__ == "__main__":
    main(sys.argv[1:])
