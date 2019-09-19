#!/usr/bin/env python3
"""Checks health of server container."""

import argparse
import logging
import requests
import retrying
import subprocess
import sys

logger = logging.getLogger(__name__)

MAX_DELAY = 1 * 60 * 1000  # 1 minutes.
WAIT = 5 * 1000  # 5 sec.


@retrying.retry(wait_fixed=WAIT, stop_max_delay=MAX_DELAY)
def check_postgres(postgres_host):
    """Check postgres health by attempting to create a TCP connection."""
    logger.info('Checking postgres...')
    subprocess.check_call(["pg_isready", "-q", "-h", postgres_host])


@retrying.retry(wait_fixed=WAIT, stop_max_delay=MAX_DELAY)
def check_homepage(host, port):
    """Check homepage health by requesting via HTTP."""
    logger.info('Checking homepage...')
    r = requests.get('http://%s:%d' % (host, port))
    if r.status_code >= 400:
        logger.error('[%d] %s', r.status_code, r.text)
    assert r.status_code < 400


def main():
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format='%(asctime)s: %(name)s: %(levelname)s: %(message)s')

    parser = argparse.ArgumentParser(
        description='Checks health of server container.')

    parser.add_argument('--check_postgres', default=False, action='store_true')
    parser.add_argument('--postgres_host', type=str, default='localhost')

    parser.add_argument('--check_homepage', default=False, action='store_true')
    parser.add_argument('--server_host', type=str, default='localhost')
    parser.add_argument('--server_port', type=int, default=80)

    args = parser.parse_args()

    logger.info('Health Check')

    if args.check_postgres:
        check_postgres(args.postgres_host)
    if args.check_homepage:
        check_homepage(args.server_host, args.server_port)


if __name__ == '__main__':
    main()
