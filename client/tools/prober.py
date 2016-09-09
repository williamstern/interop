#!/usr/bin/env python
# Program to probe the interop server for continuous validation.

import argparse
import datetime
import getpass
import logging
import signal
import sys
import time

import datagen
import flightsim
from interop import AsyncClient, InteropError, Telemetry, StationaryObstacle, MovingObstacle


def main(url,
         username,
         password,
         interop_time,
         generator,
         flightsim_kml_path=None):
    """Probes the interop server.

    Args:
        url: The interoperability URL.
        username: The interoperability username.
        password: The interoperability password.
        interop_time: The time between interop requests.
        generator: The data generator name to use.
        flightsim_kml_path: The KML path to use if flightsim generator.
    """
    # Create client and data generator.
    client = AsyncClient(url, username, password)
    if generator == 'zeros':
        data_generator = datagen.ZeroValueGenerator()
    else:
        data_generator = flightsim.KmlGenerator(flightsim_kml_path)

    # Continually execute interop requests until signaled to stop.
    while True:
        start_time = datetime.datetime.now()
        telemetry = data_generator.get_uas_telemetry(start_time)

        telemetry_resp = client.post_telemetry(telemetry)
        obstacle_resp = client.get_obstacles()
        telemetry_resp.result()
        obstacle_resp.result()

        end_time = datetime.datetime.now()
        elapsed_time = (end_time - start_time).total_seconds()
        logging.info('Executed interop. Total latency: %f', elapsed_time)

        delay_time = interop_time - elapsed_time
        if delay_time > 0:
            try:
                time.sleep(delay_time)
            except KeyboardInterrupt:
                sys.exit(0)


if __name__ == '__main__':
    # Setup logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    stream = logging.StreamHandler(sys.stdout)
    stream.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s. %(name)s. %(levelname)s. %(message)s')
    stream.setFormatter(formatter)
    logger.addHandler(stream)

    # Get parameters from command line
    parser = argparse.ArgumentParser(description='Interoperability prober.')
    parser.add_argument('--url',
                        required=True,
                        help='URL for interoperability.')
    parser.add_argument('--username',
                        required=True,
                        help='Username for interoperability.')
    parser.add_argument('--password', help='Password for interoperability.')
    parser.add_argument('--interop_time',
                        type=float,
                        default=1.0,
                        help='Time between sent requests (sec).')
    parser.add_argument('--generator',
                        type=str,
                        choices=['zeros', 'flightsim'],
                        default='zeros',
                        help='Data generation implementation.')
    parser.add_argument('--flightsim_kml_path',
                        nargs='?',
                        type=str,
                        help='Path to the KML file for flightsim generation.')
    args = parser.parse_args()

    if args.password:
        password = args.password
    else:
        password = getpass.getpass('Interoperability Password: ')

    main(args.url, args.username, password, args.interop_time, args.generator,
         args.flightsim_kml_path)
