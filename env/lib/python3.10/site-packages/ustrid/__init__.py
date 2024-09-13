import uuid
import threading


def ustrid():
    """Generate a unique string identifier (thread-safe)"""
    return Ustrid.run()


class Ustrid:

    """Private class to generate unique string identifiers (thread-safe)"""
    _lock = threading.Lock()
    _count = 0

    @classmethod
    def run(cls):
        """Generate a unique string identifier (thread-safe)"""
        with cls._lock:
            cls._count += 1
            return "{}-{}".format(cls._count, uuid.uuid4())
