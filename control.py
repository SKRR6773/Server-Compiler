import os


def try_parse_integer(var):
    try:
        integer_parsed = int(var)


        return integer_parsed
    
    except:
        return var

def control(key_exit="send"):

    running = True

    data_latest = {}

    while running:
        recv = input(">")


        if recv.startswith("#"):
            if recv.endswith("clear"):
                os.system('clear')

            elif recv.endswith("show"):
                print(data_latest)

            

        elif recv == "+":
            while True:
                key = input("Key: ")

                if key == "!exit" or key == "#" or key == "" or key.strip() == "" or key.startswith("#"):
                    break

                value = input("Value: ")

                if key == "!exit" or key == "#" or key == "" or key.strip() == "" or key.startswith("#"):
                    break

                data_latest[key] = try_parse_integer(value)


        elif recv == "-":
            while True:
                key = input("rm Key: ")

                if key == "!exit" or key == "#" or key == "" or key.strip() == "" or key.startswith("#"):
                    break


                if key in data_latest.keys():
                    del data_latest[key]

                    print(f"removed key: {key}")

                else:
                    print("key not exists!")


        elif recv == key_exit:
            break


        elif recv == "./":
            path_recv = input(os.getcwd() + ": ")

            while not os.path.isfile(path_recv):
                path_recv = input(os.getcwd() + ": ")

            
            return open(path_recv, "rb").read()

    return data_latest



if __name__ == "__main__":
    print(control())