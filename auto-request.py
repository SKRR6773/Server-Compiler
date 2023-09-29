import socket
import os
import json
from lib import encode_package, decode_package
from time import sleep


def recv_async(server):
    while True:
        print(f"\n{server.recv(BUFFER).decode()}")


__DIR__ = os.path.dirname(__file__)

LOAD_DATA = None

with open(os.path.join(__DIR__, "settings.json"))as f:
    LOAD_DATA = json.load(f)


HOSTNAME = LOAD_DATA['hostname']
PORT = LOAD_DATA['port']
LISTEN = LOAD_DATA['listen']
SOCKET_TIMEOUT = LOAD_DATA['socket-timeout']
BUFFER = LOAD_DATA['buffer']


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((HOSTNAME, PORT))
server.setblocking(True)


server.send(encode_package({
    "action": "create-uuid"
}).encode())

sleep(.01)

file_path = os.path.join(__DIR__, "load.ico")
file_size = os.path.getsize(file_path)

server.send(encode_package({
    "action": "attach_icon",
    "file_size": file_size
}).encode())

sleep(1)

server.sendall(open(file_path, 'rb').read())

sleep(1)

file_path = os.path.join(__DIR__, "requirement.txt")
file_size = os.path.getsize(file_path)

server.send(encode_package({
    "action": "attach_requirement_file",
    "file_size": file_size
}).encode())

print(server.recv(4096).decode())

sleep(.1)

server.sendall(open(file_path, 'rb').read())

input("Wait....")

server.close()