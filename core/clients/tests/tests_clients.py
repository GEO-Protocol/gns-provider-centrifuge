import unittest

from core.clients.clients import Client


class ClientsTests(unittest.TestCase):
    correctSecret = b'00000000000000000000000000000000'

    def test_id_valid(self):
        c1 = Client(0, 'name', self.correctSecret)
        self.assertEqual(c1.id, 0)

        c2 = Client(2 ** 32, 'name', self.correctSecret)
        self.assertEqual(c2.id, 2**32)

    def test_id_invalid(self):
        with self.assertRaises(AssertionError):
            Client('00', 'name', self.correctSecret)

        with self.assertRaises(AssertionError):
            Client(-1, 'name', self.correctSecret)

        with self.assertRaises(AssertionError):
            Client((2 ** 32) + 1, 'name', self.correctSecret)

    def test_name_valid(self):
        c1 = Client(0, 'a', self.correctSecret)
        self.assertEqual(c1.name, 'a')

        c2 = Client(0, 'a'*256, self.correctSecret)
        self.assertEqual(c2.name, 'a'*256)

    def test_name_invalid(self):
        with self.assertRaises(AssertionError):
            Client(0, 0, self.correctSecret)

        with self.assertRaises(AssertionError):
            Client(0, '', self.correctSecret)

        with self.assertRaises(AssertionError):
            Client(0, '' * 257, self.correctSecret)

    def test_secret_valid(self):
        c1 = Client(0, 'name', self.correctSecret)
        self.assertEqual(c1.secret, self.correctSecret)

    def test_secret_invalid(self):
        with self.assertRaises(AssertionError):
            Client(0, 'name', '')

        with self.assertRaises(AssertionError):
            Client(0, 'name', b'0000000000000000000000000000000')   # one byte shorter key

        with self.assertRaises(AssertionError):
            Client(0, 'name', b'000000000000000000000000000000000')   # one byte longer key

    def test_serialize(self):
        def compare_clients(x, y):
            self.assertEqual(x.id, y.id)
            self.assertEqual(x.name, y.name)
            self.assertEqual(x.secret, y.secret)
            self.assertEqual(x.remote_ipv4_address, y.remote_ipv4_address)

        c1 = Client(0, 'name', self.correctSecret)
        compare_clients(c1, Client.deserialize(c1.serialize()))

        c2 = Client(2 ** 32, 'name', self.correctSecret)
        compare_clients(c2, Client.deserialize(c2.serialize()))

        c3 = Client(2 ** 32, 'name', self.correctSecret)
        compare_clients(c3, Client.deserialize(c3.serialize()))
