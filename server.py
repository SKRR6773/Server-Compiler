import shutil
import socket
import os
import threading
import datetime
import json
from lib import generate_uuid_without, encode_package, decode_package, create_chunks_array, is_ico_content, \
    is_plain_text_content, limit_length_of_string


__DIR__ = os.path.dirname(__file__)

''' 
    wait client requests
    ถ่ายโอน Python Script จาก Client
    install pip modules จากข้อมูลที่ถูกถ่ายโอน
    compile ตามเงื่อนไขที่กำหนดของ Client
    zip file แล้วทำการส่งให้ Client โดยใช้อีก socket
    ทำการกำหนด thread สำหรับลบข้อมูลขยะ
    วนซํ้าและทำการรอรับคำสั่งจาก client
'''

'''
    # pyinstaller --noconfirm --onedir --console --icon "/home/skrr6773/Downloads/tiktok_logo_icon_186896.ico"  "/home/skrr6773/Desktop/Python/server_compiler/server.py"
'''

'''
    package request = {
        action: ...,
        Id: ...
        ...
    }
'''

LOAD_DATA = None

# Load settings
with open(os.path.join(__DIR__, "settings.json"))as f:
    LOAD_DATA = json.load(f)


HOSTNAME = LOAD_DATA['hostname']
PORT = LOAD_DATA['port']
LISTEN = LOAD_DATA['listen']
SOCKET_TIMEOUT = LOAD_DATA['socket-timeout']
BUFFER = LOAD_DATA['buffer']
OUTPUT_DIR = LOAD_DATA['output-directory']
LIMIT_ICON_SIZE = LOAD_DATA['limit-icon-size']
LIMIT_REQUIREMENT_SIZE = LOAD_DATA['limit-requirement-size']



class Server:
    def __init__(self):
        self.running = True     # status running
        self.server = None      # keep socket object

        self.clients = []       # keep all client
        self.errors = []        # keep report error on server
        self.uuids_using = []   # keep uuids of clients on server


    # when client connection
    def client_handler(self, client, addr):
        # settimeout
        client.settimeout(SOCKET_TIMEOUT)

        is_first = True                                                 # is first connection

        self.clients.append(client)                                     # append client to server

        self.write_log_and_report(f"{addr} >>เชื่อมต่อมายังเซิร์ฟเวอร์แล้ว!")    # write log and print on console

        current_use_package_id = False                                  # get current uuid of client set default is False
        exec_list = [                                                   # keep execute pyinstaller list
            "pyinstaller",
            "--noconfirm",
        ]

        while self.running:
            try:
                if is_first:                                            # is first to send Welcome .....
                    client.send(b"Welcome to SKRR6773 Server!")
                    is_first = False                                    # set is_first is false 

                succ = []                                               # keep succuss messges for send to client when last loop
                error = []                                              # keep error messages for send to client when last loop
                data = []                                               # keep data for send to client when last loop


                package_recv = client.recv(BUFFER)                      # recv msg from client (no decode)


                if not package_recv:                                    # something client out to the server
                    break

                
                package_decoded = decode_package(package_recv.decode()) # decode user package if false jump to except


                if package_decoded:                                     # can't decode package (json to dict)
                    if "action" in package_decoded:                     
                        # crud
                        if package_decoded['action'] == "create-uuid":  # user want create uuid
                            if current_use_package_id == False or "confirm" in package_decoded:
                                if "confirm" in package_decoded:
                                    self.uuids_using.remove(current_use_package_id)

                                # generate uuid without same in
                                uuid_generated = generate_uuid_without(self.uuids_using)    

                                # append to bag uuid
                                self.uuids_using.append(uuid_generated)

                                # set current uuid
                                current_use_package_id = uuid_generated

                                # when something can't create directory
                                if not self.create_uuid_dir(uuid_generated):
                                    self.uuids_using.remove(current_use_package_id)
                                    current_use_package_id = False

                                    error.append("create uuid dir failed, and so create uuid failed!")

                                else:
                                    succ.append("create uuid successfully!")

                            else:
                                error.append("You confirm for delete uuid and new create Y/N?")

                        elif package_decoded['action'] == "read-uuid":  # read uuid
                            data.append(current_use_package_id)


                        elif package_decoded['action'] == "update-uuid":    # update uuid
                            if current_use_package_id != False:
                                self.delete_uuid_dir(current_use_package_id)

                                self.uuids_using.remove(current_use_package_id)

                            uuid_generated = generate_uuid_without(self.uuids_using)
                            self.uuids_using.append(uuid_generated)
                            current_use_package_id = uuid_generated

                            self.create_uuid_dir(uuid_generated)

                            succ.append("update uuid successfully")


                        elif package_decoded['action'] == "delete-uuid":    # delete uuid
                            if current_use_package_id != False:


                                if self.delete_uuid_dir(current_use_package_id):
                                    succ.append(f"delete uuid successfully!")

                                else:
                                    error.append("delete uuid dir failed")
                                    self.write_log_and_report(f"{addr} - {current_use_package_id} >>Delete uuid dir failed!")



                                self.uuids_using.remove(current_use_package_id)
                                current_use_package_id = False


                            else:
                                error.append(f"uuid not already")


                        elif package_decoded['action'] == "compile":
                            pass

                        elif package_decoded['action'] == "settings_compile":
                            # Options
                            '''
                                # subprocess.run([
                                #     'pyinstaller', 
                                #     '--noconfirm',
                                #     '--onedir',
                                #     '--name', 'my_app2',
                                #     '--distpath', str(os.path.join(__DIR__, 'output')),
                                #     'test_compile.py'
                                # ])
                            '''

                            default_settings = [
                                "pyinstaller",
                                "--noconfirm",
                                "--onedir",
                                "--name", "myapp",
                                "--distpath", os.path.join(__DIR__, "output"),
                                "python_script.py"
                            ]

                            default_commands = {
                                "pyinstaller": "pyinstaller",
                                "--noconfirm": "--noconfirm",
                                "category_output": [
                                    "--onedir", "--onefile"
                                ],
                                "category_console": [
                                    "--console", "--windowed"
                                ],
                                "--icon": None,
                                "--name": None,
                                "--uac-admin": None
                            }

                            exec_list = [
                                "pyinstaller",
                                "--noconfirm",
                            ]


                            if "options" in package_decoded:
                                if isinstance(package_decoded['options'], dict):

                                    # category output condition
                                    if "category_output" in package_decoded['options']:
                                        if isinstance(package_decoded['options']['category_output'], str):
                                            if package_decoded['options']['category_output'] in default_commands['category_output']:
                                                exec_list.append(package_decoded['options']['category_output'])

                                            else:
                                                err_str = f"{addr} >>category_ouput option unknow!"

                                                error.append(err_str)
                                                self.write_log(err_str)

                                        else:
                                            err_str = f"{addr} >>category_output option is string only!"

                                            error.append(err_str)
                                            self.write_log(err_str)

                                    else:
                                        err_str = f"{addr} >>required \"category_output\" option"

                                        error.append(err_str)
                                        self.write_log(err_str)
                                    # end category output condition
                                    

                                    # category console condition
                                    if "category_console" in package_decoded['options']:
                                        if isinstance(package_decoded['options']['category_console'], str):
                                            if package_decoded['options']['category_console'] in default_commands['category_console']:
                                                exec_list.append(package_decoded['options']['category_console'])

                                            else:
                                                err_str = f"{addr} >>category_console option unknow!"

                                                error.append(err_str)
                                                self.write_log(err_str)

                                        else:
                                            err_str = f"{addr} >>category_console option is string only!"

                                            error.append(err_str)
                                            self.write_log(err_str)

                                    else:
                                        err_str = f"{addr} >>required \"category_console\" option"

                                        error.append(err_str)
                                        self.write_log(err_str)
                                    # end category console condition


                                    # app name condition
                                    if "app_name" in package_decoded['options']:
                                        if isinstance(package_decoded['options']['app_name'], str):
                                            exec_list.append("--name")
                                            exec_list.append(package_decoded['options']['app_name'])

                                        else:
                                            err_str = f"{addr} >>app_name option just is string only!"

                                            error.append(err_str)
                                            self.write_log(err_str)

                                    else:
                                        exec_list.append("--name")
                                        exec_list.append("myApp")

                                        err_str = f"{addr} >>Warning: your not set app name, but the server set default is myApp"

                                        error.append(err_str)
                                        self.write_log(err_str)
                                    # end app name condition

                                else:
                                    err_str = f"{addr} >>options is not dict datatype!"

                                    error.append(err_str)
                                    self.write_log(err_str)

                            else:
                                err_str = f"{addr} >>options key not exists!"

                                error.append(err_str)
                                self.write_log(err_str)

                        
                        elif package_decoded['action'] == "attach_icon":
                            
                            if current_use_package_id != False:
                                if self.uuid_dir_is_exists(current_use_package_id):
                                    if "file_size" in package_decoded:
                                        if isinstance(package_decoded['file_size'], int):
                                            if package_decoded['file_size'] <= LIMIT_ICON_SIZE:
                                                error = []
                                                data = []
                                                succ.append({
                                                    "request-ready": True
                                                })

                                                client.send(self.end_status_content(error, succ, data))

                                                content_loading = b""

                                                file_size = package_decoded['file_size']

                                                timeout_count = 0
                                                limit_timeout = 10

                                                chunks_list = create_chunks_array(file_size, BUFFER)

                                                is_done = False

                                                for chunk in range(len(chunks_list)):
                                                    try:
                                                        content_loading += client.recv(chunks_list[chunk])


                                                        if chunk + 1 == len(chunks_list):
                                                            is_done = True

                                                    except socket.timeout:
                                                        if timeout_count > limit_timeout:
                                                            err_str = f"{addr} >>upload icon file timeout!"

                                                            error.append(err_str)
                                                            self.write_log_and_report(err_str)
                                                            break

                                                        timeout_count += 1
                                                        continue

                                                    except Exception as ex:
                                                        err_str = f"{addr} >>Upload icon Error -> {ex}"

                                                        error.append(err_str)
                                                        self.write_log_and_report(err_str)
                                                        break


                                                
                                                if is_done and len(error) == 0:
                                                    if is_ico_content(content_loading):
                                                        with open(os.path.join(__DIR__, OUTPUT_DIR, current_use_package_id, "icon.ico"), 'wb')as f:
                                                            f.write(content_loading)

                                                        
                                                        succ.append("Added icon successfully!")

                                                    else:
                                                        content_loading = b""
                                                        err_str = f"{addr} >>icon upload is .ico only!"

                                                        error.append(err_str)
                                                        self.write_log_and_report(err_str)
                                                
                                                else:
                                                    err_str = f"{addr} >>icon upload somethings error!"

                                                    error.append(err_str)
                                                    self.write_log_and_report(err_str)

                                            else:
                                                err_str = f"{addr} >>icon size must be less than 10MB"

                                                error.append(err_str)
                                                self.write_log(err_str)

                                        else:
                                            err_str = f"{addr} >>file_size is integer only!"

                                            error.append(err_str)
                                            self.write_log(err_str)

                                    else:
                                        err_str = f"{addr} >>required file_size"

                                        error.append(err_str)
                                        self.write_log(err_str)

                                else:
                                    err_str = f"{addr} >>เกิดข้อผิดพลาดบางอย่าง โปรด update-uuid"

                                    error.append(err_str)
                                    self.write_log(err_str)
                            
                            else:
                                err_str = f"{addr} >>You need to create-uuid first!"

                                error.append(err_str)
                                self.write_log(err_str)
                        # end attach icon

                        elif package_decoded['action'] == "attach_requirement_file":

                            if current_use_package_id != False:
                                if self.uuid_dir_is_exists(current_use_package_id):
                                    if "file_size" in package_decoded:
                                        if isinstance(package_decoded['file_size'], int):
                                            if package_decoded['file_size'] <= LIMIT_REQUIREMENT_SIZE:
                                                error = []
                                                succ = [{
                                                    "request-ready": True
                                                }]
                                                data = []

                                                client.send(self.end_status_content(error, succ, data))

                                                content_loading = b''

                                                file_size = package_decoded['file_size']

                                                timeout_count = 0
                                                limit_timeout = 10  

                                                is_done = False

                                                chunks_list = create_chunks_array(file_size, BUFFER)

                                                for chunk in range(len(chunks_list)):
                                                    try:
                                                        content_loading += client.recv(chunks_list[chunk])

                                                        if chunk + 1 == len(chunks_list):
                                                            is_done = True

                                                    except socket.timeout:
                                                        if timeout_count > limit_timeout:
                                                            err_str = f"{addr} >>attach requirement file timeout!"

                                                            error.append(err_str)
                                                            self.write_log_and_report(err_str)


                                                        timeout_count += 1
                                                        continue

                                                    except Exception as ex:
                                                        err_str = f"{addr} >>attach requirement file error -> {ex}"

                                                        error.append(err_str)
                                                        self.write_log_and_report(err_str)

                                                        break


                                                
                                                if is_done and len(error) == 0:
                                                    if is_plain_text_content(content_loading):
                                                        with open(os.path.join(__DIR__, OUTPUT_DIR, current_use_package_id, "requirements.txt"), "wb")as f:
                                                            f.write(content_loading)

                                                        succ.append("Added requirement file!")

                                                    else:
                                                        err_str = f"{addr} >>File Not Support!"

                                                        error.append(err_str)
                                                        self.write_log_and_report(err_str)

                                                else:
                                                    err_str = f"{addr} >>Upload requirement file Failed!"

                                                    error.append(err_str)
                                                    self.write_log_and_report(err_str)

                                            else:
                                                err_str = f"{addr} >>ขนาดของไฟล์ต้องมีขนาดน้อยกว่า 1MB"

                                                error.append(err_str)
                                                self.write_log(err_str)

                                        else:
                                            err_str = f"{addr} >>ขนาดของไฟล์ต้องเป็นตัวเลขเท่านั้น"

                                            error.append(err_str)
                                            self.write_log(err_str)

                                    else:
                                        err_str = f"{addr} >>การอัพโหลดไฟล์ requirement ต้องระบุขนาดด้วย"

                                        error.append(err_str)
                                        self.write_log(err_str)

                                else:
                                    err_str = f"{addr} >>เกิดข้อผิดพลาดบางอย่าง โปรด update-uuid"

                                    error.append(err_str)
                                    self.write_log(err_str)

                            else:
                                err_str = f"{addr} >>You need to create-uuid first!"

                                error.append(err_str)
                                self.write_log(err_str)

                        else:
                            err_str = f"{addr} >>action unknow! -> {limit_length_of_string(str(package_decoded['action']), 10)}"
                            error.append(err_str)

                            self.write_log_and_report(err_str)

                    else:
                        err_str = f"{addr} >>sent package unknow!"
                        error.append(err_str)

                        self.write_log_and_report(err_str)

                else:
                    self.write_log_and_report(f"{addr} >>package decode error! -> {limit_length_of_string(str(package_recv.decode()), 20)}")
                    break



                client.send(self.end_status_content(error, succ, data))


            except socket.timeout:
                continue

            except socket.error as ex:
                break

            except Exception as ex:
                self.write_log_and_report(f"{addr} >>เกิดข้อผิดพลาด -> {ex}")
                break

        
        if current_use_package_id != False:
            self.delete_uuid_dir(current_use_package_id)

        self.write_log_and_report(f"{addr} >>ออกจากเซิร์ฟเวอร์แล้ว")
        self.try_close_socket(client)
        


    def end_status_content(self, error=[], succ=[], data=[]):
        return encode_package({
            "status": True if len(error) == 0 else False,
            "error": error,
            "succ": succ,
            "data": data
        }).encode()

    def start(self, ):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((HOSTNAME, PORT))
            self.server.listen(LISTEN)
            self.server.settimeout(SOCKET_TIMEOUT)

        except:
            return False
        

        while self.running:
            try:
                client, addr = self.server.accept()

                task = threading.Thread(target=self.client_handler, args=(client, addr))
                task.start()

            except socket.timeout:
                continue

            except Exception as ex:
                self.write_log_and_report(f"เกิดข้อผิดพลาดทำให้เซิร์ฟเวอร์หยุด -> {str(ex)}")
                self.running = False


    def write_log_and_report(self, text:str):
        self.write_log(text)
        self.insert_report(text)
        print(f"{self.now()} || {text}\n")


    def write_log(self, text:str):
        with open(os.path.join(__DIR__, "server_log.txt"), 'a')as f:
            f.write(f"[{self.now()}] || {text}\n")

    def now(self, )-> str:
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    

    def close(self, ):
        self.running = False


    def insert_report(self, msg:str):
        self.errors.append(msg)
    

    def get_reports(self, ) -> list:
        return self.errors
    
    def try_close_socket(self, socket_obj):
        try:
            socket_obj.close()

            return True
        
        except:
            return False
        

    def create_uuid_dir(self, uuid:str):
        if not self.uuid_dir_is_exists(uuid):
            os.mkdir(os.path.join(__DIR__, OUTPUT_DIR, uuid))

            return True
        
        else:
            err_str = f"{uuid} >>create uuid dir failed, because is exists!"

            self.write_log_and_report(err_str)
            return False
        
    def uuid_dir_is_exists(self, uuid:str):
        return os.path.exists(os.path.join(__DIR__, OUTPUT_DIR, uuid))
    

    def delete_uuid_dir(self, uuid:str):
        if self.uuid_dir_is_exists(uuid):
            shutil.rmtree(os.path.join(__DIR__, OUTPUT_DIR, uuid))

            return True
        
        else:
            err_str = f"{uuid} >>delete uuid dir failed, because it not exists!"

            self.write_log_and_report(err_str)
            return False



if __name__ == "__main__":
    server = Server()

    print(f"Listen clients on {HOSTNAME}:{PORT}")
    if server.start():
        server.close()

        print("Server Closed!")

    else:
        print("Start Server Failed!")