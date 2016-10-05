#!/usr/bin/env python
# CLI for interacting with interop server.

from __future__ import print_function
import argparse
import datetime
import getpass
import logging
import pprint
import sys
import time

from interop import Client
from interop import Target
from interop import Telemetry
from upload_targets import upload_targets


def missions(args, client):
    missions = client.get_missions()
    for m in missions:
        pprint.pprint(m.serialize())


def targets(args, client):
    upload_targets(client, args.target_filepath, args.imagery_dir)


def probe(args, client):
    while True:
        start_time = datetime.datetime.now()

        telemetry = Telemetry(0, 0, 0, 0)
        telemetry_resp = client.post_telemetry(telemetry)
        obstacle_resp = client.get_obstacles()

        end_time = datetime.datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()
        logging.info('Executed interop. Total latency: %f', elapsed_time)

        delay_time = args.interop_time - elapsed_time
        if delay_time > 0:
            try:
                time.sleep(delay_time)
            except KeyboardInterrupt:
                sys.exit(0)


def main():
    # Setup logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    stream = logging.StreamHandler(sys.stdout)
    stream.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s. %(name)s. %(levelname)s. %(message)s')
    stream.setFormatter(formatter)
    logger.addHandler(stream)

    # Parse command line args.
    parser = argparse.ArgumentParser(description='AUVSI SUAS Interop CLI.')
    parser.add_argument('--url',
                        required=True,
                        help='URL for interoperability.')
    parser.add_argument('--username',
                        required=True,
                        help='Username for interoperability.')
    parser.add_argument('--password', help='Password for interoperability.')
    subparsers = parser.add_subparsers(help='Sub-command help.')

    subparser = subparsers.add_parser('missions', help='Get missions.')
    subparser.set_defaults(func=missions)

    subparser = subparsers.add_parser('targets', help='Upload targets.')
    subparser.set_defaults(func=targets)
    subparser.add_argument('--target_filepath',
                           required=True,
                           help='Filepath to target file.')
    subparser.add_argument('--imagery_dir',
                           required=True,
                           help='Filepath prepended to paths in target file.')

    subparser = subparsers.add_parser('probe', help='Send dummy requests.')
    subparser.set_defaults(func=probe)
    subparser.add_argument('--interop_time',
                           type=float,
                           default=1.0,
                           help='Time between sent requests (sec).')

    # Parse args, get password if not provided.
    args = parser.parse_args()
    if args.password:
        password = args.password
    else:
        password = getpass.getpass('Interoperability Password: ')

    # Create client and dispatch subcommand.
    client = Client(args.url, args.username, password)
    args.func(args, client)


if __name__ == '__main__':
    main()
