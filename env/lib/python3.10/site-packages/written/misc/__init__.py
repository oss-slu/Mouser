import os
import os.path
from tempfile import NamedTemporaryFile


def ensure_parent_dir(path):
    """Make sure that parent dir exists (create it if isn't yet created)"""
    parent = os.path.dirname(path)
    try:
        os.makedirs(parent)
    except FileExistsError as e:
        pass


def create_temp_file(parent_dir, mode, encoding):
    t = NamedTemporaryFile(prefix=".pyrustic_written_",
                           suffix=".temp", dir=parent_dir,
                           mode=mode, encoding=encoding,
                           delete=False)
    return t.name


def unlink(path):
    try:
        os.unlink(path)
    except Exception as e:
        pass
