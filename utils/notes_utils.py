import os
import tempfile

def save_tmp_file(file):
    ext = os.path.splitext(file.filename)[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        file.save(tmp.name)

        return tmp.name

def remove_tmp_file(file_name):
    os.remove(file_name)
