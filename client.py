import getopt
import socket
import struct
import sys
import time

import netstruct

from core.settings import Settings


def usage():
    print("Usage:")
    print("\tpython interface.py [-v] [-p ping id] [-l lookup username]")
    print("Example:")
    print("\tpython interface.py -p 3")
    print("\tpython interface.py -l 'minyor'")


if __name__ == '__main__':
    verbose = False
    id = None
    username = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:l:v", ["help"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-p", "--ping"):
            id = int(a)
        elif o in ("-l", "--lookup"):
            username = a
        else:
            assert False, "unhandled option"

    settings = Settings.load_config()

    if id:
        time_updated = time.time()
        print("id="+str(id)+" time_updated="+str(time_updated))

        values = (id, time_updated)
        s = struct.Struct(">I d")
        data = s.pack(*values)

        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.sendto(data, (settings.ping_host, settings.ping_port))

        (data, address) = client.recvfrom(128 * 1024)
        print("\treceived message: '" + data.decode('ascii') + "'")
    elif username:
        username_len = len(username)
        print("username_len="+str(username_len)+" username="+str(username))

        values = (username_len,)
        s = struct.Struct(">H")
        data = s.pack(*values) + username.encode('ascii')

        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client.sendto(data, (settings.host, settings.port))

        (data, address) = client.recvfrom(128 * 1024)

        if data == "NOT FOUND".encode('ascii') or \
            data == "UNKNOWN PROVIDER".encode('ascii') or \
                        data == "WRONG FORMAT".encode('ascii'):
            print("\treceived message: '" + data.decode('ascii') + "'")
        else:
            s = netstruct.NetStruct(b">B I H")
            (protocol_version, max_unsigned_32, message_type) = s.unpack(data)
            print("\tprotocol_version="+str(protocol_version)+" max_unsigned_32="+str(max_unsigned_32)+
                  " message_type="+str(message_type))

            data_pos = 7
            s = netstruct.NetStruct(b">H")
            (username_len,) = s.unpack(data[data_pos:])
            username = data[data_pos + 2:data_pos + 2 + username_len].decode('ascii')
            print("\tusername_len=" + str(username_len) + " username=" + str(username))

            data_pos += 2 + username_len
            s = netstruct.NetStruct(b">B")
            (address_len,) = s.unpack(data[data_pos:])
            address = data[data_pos + 1:data_pos + 1 + address_len].decode('ascii')
            print("\taddress_len=" + str(address_len) + " address=" + str(address))
