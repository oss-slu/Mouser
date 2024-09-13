import os
import os.path
try:
    import fcntl
except ImportError:
    fcntl = None


def sync_file(file):
    """sync a file obj"""
    # file flush
    file.flush()
    # fsync the file
    fd = file.fileno()
    os.fsync(fd)
    full_sync(fd)


def sync_dir(path):
    """fsync dir"""
    # https://man7.org/linux/man-pages/man2/fsync.2.html
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
        full_sync(fd)
    except Exception as e:
        pass
    finally:
        os.close(fd)


def full_sync(fd):
    """full sync file description fd"""
    # https://lists.apple.com/archives/darwin-dev/2005/Feb/msg00072.html
    if fcntl and hasattr(fcntl, "F_FULLFSYNC"):
        try:
            fcntl.fcntl(fd, fcntl.F_FULLFSYNC)
        except Exception as e:
            return False
        else:
            return True
    return False
