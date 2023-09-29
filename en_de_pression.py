import os
import zipfile
from io import BytesIO

__DIR__ = os.path.dirname(__file__)

# os.path.realpath()

io_tmp = BytesIO()
io_tmp.seek(0)

is_first = True

with zipfile.ZipFile(io_tmp, "w", zipfile.ZIP_DEFLATED)as zip:
    for root, dirs, files in os.walk(os.path.join(__DIR__, "tmp")):
        for file in files:
            zip.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(__DIR__, "tmp")))



io_tmp.seek(0)
print(len(io_tmp.getvalue()))

with open(os.path.join(__DIR__, "copy.zip"), "wb")as f:
    f.write(io_tmp.getvalue())


io_tmp.close()

