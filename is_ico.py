import requests
from io import BytesIO
from PIL import Image


# load_data = None

# with open('tool.png', 'rb')as f:
#     load_data = f.read()


# print(load_data.startswith(b'\x00\x00\x01\x00'))

load_data = None

with open('tool.png', 'rb')as f:
    load_data = f.read()


with open('tool.png', 'wb')as f:
    f.write(b'\x00\x00\x01\x00' + load_data)