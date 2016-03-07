"""Functions for converting between units."""


def kilometers_to_feet(kilometers):
    """Converts kilometers to feet.

    Args:
        kilometers: A distance in kilometers.
    Returns:
        A distance in feet.
    """
    return kilometers * 3280.8399


def feet_to_meters(feet):
    """Converts feet to meters.

    Args:
        feet: A distance in feet.
    Returns:
        A distance in meters.
    """
    return feet * 0.3048


def knots_to_feet_per_second(knots):
    """Converts knots to feet per second.

    Args:
        knots: A speed in knots.
    Returns:
        A speed in feet per second.
    """
    return knots * 1.6878098571011957
