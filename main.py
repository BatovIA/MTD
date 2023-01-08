import os
import socket
import subprocess
import time
from pathlib import Path

ip = 'Main301'
port = 5005
user_pc = 'K301-15'
server = None
client = None
test_path = os.getcwd()


def recv_timeout(the_socket, timeout=2):
    the_socket.setblocking(0)
    total_data = []
    data = b''
    begin = time.time()
    while True:
        if total_data and time.time() - begin > timeout:
            break
        elif time.time() - begin > timeout * 2:
            break

        try:
            data = the_socket.recv(8192)
            if data:
                total_data.append(data)
                begin = time.time()
            else:
                time.sleep(0.1)
        except:
            pass
    to_return = b''
    for i in total_data:
        to_return += i
    return to_return


def get_non_exist(name):
    if not Path(test_path + '/' + name).is_file():
        return open(test_path + '/' + name, 'wb')
    i = 2
    while True:
        newname = name[:-4] + ' (' + str(i) + ')' + name[-4:]
        if not Path(test_path + '/' + newname).is_file():
            return open(test_path + '/' + newname, 'wb')
        i += 1


def download_tests():
    global direct
    try:
        server.send(b'GETLIST\r\n')
        server.send(bytes(user_pc, 'utf-8') + b'\r\n')
        data = recv_timeout(server, 1)
        if b'NO\r\n' == data:
            print("Haven't tests")
            return
        data = data.split(b'\r\n')
        directories = list()
        for i in range(2, len(data) - 1, 2):
            directories.append(data[i])
        server.send(b'QUIT\r\n')
        server.close()
        for direct in directories:
            connect()
            server.send(b'GETTEST\r\n')
            server.send(bytes(user_pc, 'utf-8') + b'\r\n')
            server.send(direct + b'\r\n')
            server.send(bytes(user_pc, 'utf-8') + b'\r\n')
            file = get_non_exist(str(direct[direct.rfind(b'\\') + 1:], 'utf-8'))
            data = recv_timeout(server, 5)
            kol = data.find(b'\n', data.find(b'\n', data.find(b'\n', data.find(b'\n') + 1)) + 1) + 1
            file.write(data[kol:])
            file.close()
            server.send(b'QUIT\r\n')
            server.close()
        print('All tests downloaded')
        test_directory = test_path + '/' + str(direct[direct.rfind(b'\\') + 1:], 'utf-8')
        subprocess.run(['MTE.exe', test_directory])
    except socket.error as err:
        print(str(err))


def connect():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        global server
        server = sock
    except socket.error as err:
        print(str(err))


def main():
    connect()
    download_tests()


main()
