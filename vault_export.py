#!/usr/bin/env python3

"""
    EXPORT DATA FROM XLS TO VAULT
    before use please export the VAULT_TOKEN and VAULT_ADDR

"""

from os import environ
from pandas import read_excel

import hvac

# check if env variables are set
try:
    URL = environ['VAULT_ADDR']
    TOKEN = environ['VAULT_TOKEN']
except KeyError:
    print("Please export VAULT_TOKEN and VAULT_ADDR as env variables")

# set connection to VAULT
try:
    client = hvac.Client(
        url=URL,
        token=TOKEN
)
except:
    print("Connection to Vault failed.")
    print("Please check your VAULT_TOKEN and VAULT_ADDR env variables")
    exit(2)

# set general var for vault mount point
VAULT_MOUNT_POINT = 'dba'


def generate_data(xls) -> dict:
    """
    Parse the xls file to sort it and return its content as a dictionary

    :param xls: content of the xls file
    :return: export => a dictionary that sorted and merged the content of the file per project and hostname
    """

    export = {}

    for line in xls.to_dict(orient='record'):
        project = line['project']

        if project not in export:
            export[project] = {}

        hostname = line['hostname']
        if hostname not in export[project]:
            export[project][hostname] = {}

        user = line['user']
        passwd = line['password']

        export[project][hostname].update({user: passwd})

    return export


def get_current_secrets(project: str, hostname: str) -> dict:
    """
    Queries Vault to get the current state of secrets in the requested path


    :return: a "user = passwd" dict for requested path
    """
    try:
        secret_version_response = client.secrets.kv.v2.read_secret_version(
            mount_point=VAULT_MOUNT_POINT,
            path='{}/{}'.format(project, hostname)
        )
        data = secret_version_response['data']['data']
    # if path does not exist in vault
    except hvac.exceptions.InvalidPath:
        data = {}

    return data


def update_data(project: str, hostname: str, secrets: dict):
    """
    Updates or adds passwords and usernames for requested path on Vault.

    :param project: name of the project as a string
    :param hostname: string
    :param secrets: a dict with old and updated passwds
    """
    client.secrets.kv.v2.create_or_update_secret(
        mount_point=VAULT_MOUNT_POINT,
        path='{}/{}'.format(project, hostname),
        secret=secrets
    )


def main():
    filename = 'passwords.xlsx'

    # read xls file and deal with merged cells if
    xls = read_excel(filename, sheet_name='passwords').fillna(method='ffill')

    # parse data of xls file as a dict
    xls_data = generate_data(xls)

    # update secrets one hostname at a time
    for project in xls_data:
        for hostname in xls_data[project]:

            # get the current state of secrets
            current_secrets = get_current_secrets(project.upper(), hostname.lower())

            # get secrets from xls file
            secrets_update = xls_data[project][hostname]

            # merge the dicts
            current_secrets.update(secrets_update)

            update_data(project.upper(), hostname.lower(), current_secrets)


if __name__ == '__main__':
    main()
