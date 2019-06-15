import os


class UnableToVerifyException(Exception):
    """It was impossible to verify the existence of this email"""


class HostSystemNotSupportedException(Exception):
    f"""The host system ('{os.name}') is not supported for this package"""
