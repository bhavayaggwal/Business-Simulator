"""Errors shared between the layers."""


class StorageError(Exception):
    """Data couldn't be loaded or saved.

    The data layer raises it with a message written for the user (for example
    "Can't reach SQL Server..."), so the screens can show it as it is without
    knowing anything about databases (NFR4).
    """
