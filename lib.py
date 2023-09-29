import uuid
import json
import shutil
import os


__DIR__ = os.path.dirname(__file__)

def generate_uuid_without(array_includes=[]):
    while True:
        uuid_generated = uuid.uuid1().hex


        if uuid_generated not in array_includes:
            return uuid_generated
        

def decode_package(text_json:str):
    try:
        temp = json.loads(text_json)
        
        return temp
    
    except json.decoder.JSONDecodeError:
        return False
    
def encode_package(json_obj:list|dict):
    try:
        temp = json.dumps(json_obj)

        return temp
    
    except:
        return False
    
def is_ico_content(content:bytes):
    return content.startswith(b'\x00\x00\x01\x00')

def is_plain_text_content(content:bytes):
    try:
        content.decode()

        return True
    except:
        return False
    

def limit_length_of_string(value:str, limit_length:int):
    return value[:limit_length] if len(value) > limit_length else value


def create_chunks_array(full, sub):
    result = [sub for _ in range(int(full/sub))]


    if full > sub:
        result.append(full % sub)

    else:
        result.append(full)

    return result



if __name__ == "__main__":
    print(generate_uuid_without([]))
    print("a" in decode_package('{"a": 1}'))

    print("##################")

    print(create_chunks_array(288, 4096))

    # shutil.rmtree(os.path.join(__DIR__, "tmp"))