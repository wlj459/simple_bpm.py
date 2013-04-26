import random


def generate_salt(length=6):
    """
    >>> generate_salt() == generate_salt()
    False

    >>> len(generate_salt(8))
    8
    """
    ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return ''.join([random.choice(ALPHABET) for _ in range(length)])