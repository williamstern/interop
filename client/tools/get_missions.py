#!/usr/bin/env python
# Program to request and print mission details.

import argparse
import getpass
from __future__ import print_statement

from interop import Client
from interop import Target


def main(url, username, password):
    """Program to get and print the mission details."""
    client = Client(url, username, password)
    missions = client.get_missions()
    print(missions)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AUVSI SUAS Get Missions.')
    parser.add_argument('--url',
                        required=True,
                        help='URL for interoperability.')
    parser.add_argument('--username',
                        required=True,
                        help='Username for interoperability.')
    parser.add_argument('--password', help='Passowrd for interoperability.')
    args = parser.parse_args()

    if args.password:
        password = args.password
    else:
        password = getpass.getpass('Interoperability Password: ')

    main(args.url, args.username, password)
