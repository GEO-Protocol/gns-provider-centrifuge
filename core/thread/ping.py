import multiprocessing
import socket
import netstruct

from core.model.context import Context


class Ping:
    def __init__(self, context: Context):
        self.context = context
        self.host = context.settings.ping_host
        self.port = context.settings.ping_port
        self.process = None

    def run_async(self):
        self.process = multiprocessing.Process(target=self._run)
        self.process.start()

    def _run(self):
        # It is necessary to init socket in the same process, that would use it,
        # to prevent data races.
        self.socket = socket.socket(
            socket.AF_INET,  # Internet
            socket.SOCK_DGRAM)  # UDP
        #self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.socket.bind((self.host, self.port))
        while True:
            # Waiting for new data
            (data, address) = self.socket.recvfrom(128 * 1024)
            data = data[7:]

            # print("data="+self.bytes_to_str(data))

            # Reading client id and timestamp
            s = netstruct.NetStruct(b"<B I Q")
            (protocol_version, id, time_updated) = s.unpack(data)

            self.context.logger.info(
               "Ping received0:" + " protocol_version=" + str(protocol_version) + " id=" + str(id) + " address=" + str(address) + " time_updated=" + str(time_updated))

            # Retrieving client from db and updating its address and timestamp
            client = self.context.client_manager.find_by_id(id)
            if client:
                if not client.time_updated or int(client.time_updated) < int(time_updated):
                    self.context.logger.info(
                        "Ping received:"+" id="+str(id)+" address="+str(address)+" time_updated="+str(time_updated))
                    client.address = address
                    client.time_updated = time_updated
                    self.context.client_manager.save(client)
                    self.socket.sendto("OK".encode('ascii'), address)
                else:
                    self.socket.sendto("TOO FAST".encode('ascii'), address)
            else:
                self.socket.sendto("NOT FOUND".encode('ascii'), address)

    @staticmethod
    def bytes_to_str(arr):
        val = ""
        for byte in arr:
            val += '{:02x}'.format(byte) + ' '
        return val