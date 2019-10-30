import multiprocessing
import struct
import binascii

from ..model.context import Context


class Base:
    protocol_version = 0
    header_size = 10
    checksum_size = 4

    def __init__(self, context: Context):
        self.context = context
        self.process = None
        self.socket = None
        self.channel_index = 0

    def run_async(self):
        self.process = multiprocessing.Process(target=self.run)
        self.process.start()

    def _run(self):
        raise NotImplementedError

    def send_message(self, data, address):
        self.socket.sendto(
            self.pack_message(data),
            address
        )

    def pack_message(self, data):
        self.channel_index += 1
        self.channel_index = 0 if self.channel_index > 4294967295 else self.channel_index
        message_size = self.header_size + len(data) + self.checksum_size

        # Packing message length, channel index, number of packets and packet index
        values = (message_size, self.channel_index, 1, 0)
        s = struct.Struct("<H I H H")
        header = s.pack(*values)
        return header + data + struct.pack("<I", self.calc_checksum(data))

    @staticmethod
    def calc_checksum(data):
        checksum = binascii.crc32(data)
        return checksum % (1 << 32)

    @staticmethod
    def bytes_to_str(arr):
        val = ""
        for byte in arr:
            val += '{:02x}'.format(byte) + ' '
        return val
