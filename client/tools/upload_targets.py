#!/usr/bin/env python
# Program to load targets from file and upload via interoperability.

import argparse
import concurrent
import csv
import getpass
import imghdr
import os
import re

from interop import Target

TARGET_TYPE_MAP = {
    'STD': 'standard',
    'QRC': 'qrc',
    'OAX': 'off_axis',
    'EMG': 'emergent',
}

LATITUDE_REGEX = re.compile(
    '(?P<dir>[NS])(?P<deg>\d\d) (?P<min>\d\d) (?P<sec>\d\d\.\d{0,3})')
LATITUDE_DIR = {'S': -1, 'N': 1}
LONGITUDE_REGEX = re.compile(
    '(?P<dir>[EW])(?P<deg>\d\d\d) (?P<min>\d\d) (?P<sec>\d\d\.\d{0,3})')
LONGITUDE_DIR = {'E': -1, 'W': 1}


def load_target_file(target_filepath):
    """Loads targets from the given file.

    Args:
        target_filepath: The path to the target file to load.
    Returns:
        A list of (target, image_filepath) tuples.
    Raises:
        ValueError if the file is not properly formatted.
    """
    targets = []
    with open(target_filepath, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            target_type = row[1]
            latitude_str = row[2]
            longitude_str = row[3]
            orientation = row[4].lower()
            shape = row[5]
            background_color = row[6]
            alphanumeric = row[7]
            alphanumeric_color = row[8]
            image_filepath = row[9]
            description = row[10]

            target = Target()

            if target_type not in TARGET_TYPE_MAP:
                raise ValueError('Type %s not in %s' % (target_type,
                                                        str(TARGET_TYPE_MAP)))
            target.type = TARGET_TYPE_MAP[target_type]

            # Parse latitude. Not required for off axis.
            if target.type != 'off_axis':
                match = LATITUDE_REGEX.match(latitude_str)
                if match:
                    latitude = LATITUDE_DIR[match.group('dir')] * (
                        float(match.group('deg')) + float(match.group('min')) /
                        60 + float(match.group('sec')) / 3600)
                    target.latitude = latitude
                else:
                    raise ValueError('Latitude is not valid: %s' %
                                     latitude_str)

            # Parse longitude. Not required for off axis.
            if target.type != 'off_axis':
                match = LONGITUDE_REGEX.match(longitude_str)
                if match:
                    longitude = LONGITUDE_DIR[match.group('dir')] * (
                        float(match.group('deg')) + float(match.group('min')) /
                        60 + float(match.group('sec')) / 3600)
                    target.longitude = longitude
                else:
                    raise ValueError('Longitude is not valid: %s' %
                                     longitude_str)

            if orientation:
                target.orientation = orientation
            if shape:
                target.shape = shape
            if background_color:
                target.background_color = background_color
            if alphanumeric:
                target.alphanumeric = alphanumeric
            if alphanumeric_color:
                target.alphanumeric_color = alphanumeric_color
            if description:
                target.description = description
            targets.append((target, image_filepath))
    return targets


def upload_targets(client, target_filepath, imagery_dir):
    """Load targets and upload via interoperability.

    Args:
        client: The interop client.
        target_filepath: Filepath to the tab-delimited target file.
        imagery_dir: Base to form paths to imagery files.
    """
    # Load target details.
    targets = load_target_file(target_filepath)

    # Form full imagery filepaths.
    targets = [(t, os.path.join(imagery_dir, i)) for t, i in targets]
    # Validate filepath for each image.
    for _, image_filepath in targets:
        if not os.path.exists(image_filepath):
            raise ValueError('Could not find imagery file: %s' %
                             image_filepath)
    # Validate type of each image.
    for _, image_filepath in targets:
        image_type = imghdr.what(image_filepath)
        if image_type not in ['jpeg', 'png']:
            raise ValueError('Invalid imagery type: %s' % image_type)

    # Upload targets.
    for target, image_filepath in targets:
        image_data = None
        with open(image_filepath, 'rb') as f:
            image_data = f.read()
        target = client.post_target(target)
        client.put_target_image(target.id, image_data)
