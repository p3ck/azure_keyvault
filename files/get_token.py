#!/usr/bin/python
import requests
import argparse
import sys

API_VERSION = '2018-02-01'
OAUTH_URL = 'http://169.254.169.254/metadata/identity/oauth2/token'

def get_token(args):
    token_headers = {
                 'Metadata': 'true'
             }
    token_params = {
                'api-version': API_VERSION,
                'resource': 'https://vault.{0}.net'.format(args.cloud_type)
             }
    if args.object_id:
        token_params['object_id'] = args.object_id

    token_res = requests.get(OAUTH_URL, params=token_params, headers=token_headers, timeout=(3.05, 27))
    token = token_res.json().get("access_token")
    return token

def get_secret(token, args):
    secret_params = {'api-version': '2016-10-01'}
    secret_headers = {'Authorization': 'Bearer ' + token}
    try:
        secret_res = requests.get(args.vault_url + '/secrets/' + args.keyvault_secret,
                params=secret_params, headers=secret_headers)
    except requests.exceptions.ConnectionError as exc:
        print(exc)
        sys.exit(1)

    secret = secret_res.json().get("value")
    return secret

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--vault_url',
            action='store',
            required=True,
            help="The Vault URL to get the secret from")
    parser.add_argument('--object_id',
            action='store',
            help="If using UserAssigned Identity you need to specify the object_id")
    parser.add_argument('--keyvault_secret',
            action='store',
            required=True,
            help="The name of the secret to retrieve from the Keyvault")
    parser.add_argument('--cloud_type',
            action='store',
            default='azure',
            help="The Cloud type, defaults to azure")

    args = parser.parse_args()

    token = get_token(args)
    if token:
        secret = get_secret(token, args)
        if secret:
            print (secret)
        else:
            print ("Unable to retrieve secret for key {}".format(args.keyvault_secret))
            sys.exit(2)
    else:
        print ("Unable to retrieve token\n")
        sys.exit(3)

if __name__ == "__main__":
    main()
