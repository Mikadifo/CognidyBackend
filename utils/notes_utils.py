import os
import tempfile

def save_tmp_file(file_bytes, ext):
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(file_bytes)
        return tmp.name

def remove_tmp_file(file_name):
    os.remove(file_name)
