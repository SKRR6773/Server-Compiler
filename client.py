import shutil
import socket
import os
import threading
import datetime
import json
from lib import generate_uuid_without, encode_package, decode_package    # มาจาก lib.py ใน folder เดียวกัน
from control import control                                              # มาจาก control.py ใน folder เดียวกัน


def recv_async(server):
    while True:
        try:
            msg = server.recv(BUFFER)

            if not msg: break

            print(f"\n{msg.decode()}")

        except socket.error:
            break

        except Exception as ex:
            print(f"Server Error -> {ex}")
            break
        
    print("Server Closed!")


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

print(server.recv(BUFFER).decode())

task = threading.Thread(target=recv_async, args=(server, ))
task.start()

while True:
    try:
        data = control()

        print()
        print(data)
        print()

        if isinstance(data, dict):                            # ส่ง package ปกติ
            package_encode = encode_package(data).encode()    # แปลง Dict เป็น json string และ encode

        else:                                                  # ส่งไฟล์
            server.sendall(data)


        server.send(package_encode)

    except KeyboardInterrupt:
        break

server.close()
