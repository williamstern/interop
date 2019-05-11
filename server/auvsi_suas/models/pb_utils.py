"""Utilities for working with protocol buffers."""


def FieldChoicesFromEnum(enum):
    """
    Extracts (value, name) pairs from a protobuf enum for use as choices.

    Args:
        enum: A protocol buffer enum type.
    Returns:
        A list of (value, name) pairs, where name is the name of an enum entry
        and value is the integer value associated with the enum entry.
    """
    return [(v, n) for (n, v) in enum.items()]
