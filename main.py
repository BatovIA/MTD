import socket, sys, threading, os
import struct
import time
from pathlib import Path
import subprocess

ip = 'Main301'
port = 5005
user_pc = 'K301-15'
server = None
client = None
test_path = os.getcwd()


def recv_timeout(the_socket, timeout=2):
    # make socket non blocking
    the_socket.setblocking(0)

    # total data partwise in an array
    total_data = []
    data = b''

    # beginning time
    begin = time.time()
    while 1:
        # if you got some data, then break after timeout
        if total_data and time.time() - begin > timeout:
            break

        # if you got no data at all, wait a little longer, twice the timeout
        elif time.time() - begin > timeout * 2:
            break

        # recv something
        try:
            data = the_socket.recv(8192)
            if data:
                total_data.append(data)
                # change the beginning time for measurement
                begin = time.time()
            else:
                # sleep for sometime to indicate a gap
                time.sleep(0.1)
        except:
            pass
    toReturn = b''
    for i in total_data:
        toReturn += i
    return toReturn


def GetNonExist(name):
    if not Path(test_path + '/' + name).is_file():
        return open(test_path + '/' + name, 'wb')
    i = 2
    while True:
        newname = name[:-4] + ' (' + str(i) + ')' + name[-4:]
        if not Path(test_path + '/' + newname).is_file():
            return open(test_path + '/' + newname, 'wb')
        i += 1


def DownloadTests():
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
            Connect()
            server.send(b'GETTEST\r\n')
            server.send(bytes(user_pc, 'utf-8') + b'\r\n')
            server.send(direct + b'\r\n')
            server.send(bytes(user_pc, 'utf-8') + b'\r\n')
            file = GetNonExist(str(direct[direct.rfind(b'\\') + 1:], 'utf-8'))
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


def Connect():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        global server
        server = sock
    except socket.error as err:
        print(str(err))


def main():
    Connect()
    DownloadTests()


main()
