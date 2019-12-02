import getopt
import socket
import select
import struct
import sys
import time

import netstruct

from core.settings import Settings
from core.thread.base import Base


def usage():
    print("Usage:")
    print("\tpython interface.py [-v] [-p ping id] [-l lookup username]")
    print("Example:")
    print("\tpython interface.py -p 3")
    print("\tpython interface.py -l 'minyor'")


class ThreadBase(Base):
    def _run(self):
        pass


def send_ping(host, port, id, verbose=True):
    thread_base = ThreadBase(None)

    time_updated = int(round(time.time() * 1000))
    if verbose:
        print("id="+str(id)+" time_updated="+str(time_updated))

    values = (ThreadBase.protocol_version, id, time_updated)
    s = struct.Struct("<B I Q")
    data = s.pack(*values)
    data = thread_base.pack_message(data)

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(data, (host, port))
    client.close()

    # (data, address) = client.recvfrom(512)
    # print("\treceived message: '" + data.decode('ascii') + "'")


def send_lookup(provider_name, host, port, username, gns_separator, verbose=True, wait_seconds_for_response=0):
    thread_base = ThreadBase(None)

    username = username + gns_separator + provider_name
    username_len = len(username)
    if verbose:
        print("username_len="+str(username_len)+" username="+str(username))

    values = (ThreadBase.protocol_version, username_len)
    s = struct.Struct("<B H")
    data = s.pack(*values) + username.encode('ascii')
    data = thread_base.pack_message(data)

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.sendto(data, (host, port))

    if wait_seconds_for_response > 0:
        client.setblocking(0)
        ready = select.select([client], [], [], wait_seconds_for_response)
        if ready[0]:
            (data, address) = client.recvfrom(512)
            data = data[ThreadBase.header_size:-ThreadBase.checksum_size]

            address = data[7 + 3 + username_len : ].decode('ascii')

            #print("data: " + thread_base.bytes_to_str(data))
            client.close()
            return address

    client.close()
    return None

    if 0 != 0:
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


if __name__ == '__main__':
    id = None
    username = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:l:", ["help"])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)
    for o, a in opts:
        if o in ("-h", "--help"):
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
        send_ping(settings.ping_host, settings.ping_port, id)
    if username:
        send_lookup(settings.provider_name, settings.host, settings.port, username, settings.gns_address_separator)
