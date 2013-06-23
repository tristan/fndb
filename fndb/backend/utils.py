import uuid
from fndb.db import Key

def generate_id():
    """Default id generation

    Uses the absolute value of the hash of a generated uuid.
    """
    return abs(hash(uuid.uuid1()))

def validate_key(key, id_func=generate_id):
    """Checkes that the given key has an id, and if not, calls `id_func` to generate one.
    Args:
        key: the key to validate
        id_func: a function that returns an integer id
    Returns: the original key if it was valid, otherwise a new key with an id assigned
    """
    if key.id() is None:
        key = key.flat()[:-1] + (id_func(),)
        return Key(*key)
    return key
