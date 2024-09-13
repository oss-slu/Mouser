import os
import os.path
import pathlib
from written import misc
from written.sync import sync_dir, sync_file, full_sync
from written.errors import Error


def write(data, dest):
    """
    Write to a file (TRY to do it atomically for GNU/Linux and MacOS)
    Check https://danluu.com/file-consistency/

    [parameters]
    - data: str or bytes or bytearray, data to write to file
    - dest: a pathlib.Path instance, or a path string to a file that might exist or not
     (the parent directory will be created if it doesn't exist yet)
    """
    if isinstance(dest, pathlib.Path):
        dest = str(dest.resolve())
    if isinstance(dest, str):
        misc.ensure_parent_dir(dest)
    else:
        msg = "Destination should be a path string or a pathlib.Path instance"
        raise errors.Error(msg)
    if os.path.isdir(dest):
        msg = "Destination shouldn't be a directory but a file path (which exists or not)"
        raise Error(msg)
    _write(data, dest)


def _write(data, dest):
    # update encoding and mode
    binary_mode = True if isinstance(data, (bytes, bytearray)) else False
    encoding = None if binary_mode else "utf-8"
    mode = "wb" if binary_mode else "w"
    # get parent dir and open file
    parent_dir = os.path.dirname(dest)
    # create temp file
    temp_path = misc.create_temp_file(parent_dir, mode, encoding)
    # write to temp file
    try:
        with open(temp_path, mode, encoding=encoding) as file:
            file.write(data)
            sync_file(file)
        # swap
        os.replace(temp_path, dest)
        sync.sync_dir(parent_dir)
    except Exception as e:
        pass
    finally:
        misc.unlink(temp_path)
