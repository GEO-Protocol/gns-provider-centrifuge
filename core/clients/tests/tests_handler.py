import unittest

from core.clients.clients import Client
from core.clients.handler import ClientsHandler
from core.settings import Settings


class TestsHandler(unittest.TestCase):
    correctSecret = b'00000000000000000000000000000000'

    def setUp(self):
        self.settings = Settings.load_config('../../../conf.json')
        self.handler = ClientsHandler(self.settings)
        self.handler._redis().flushdb()

    def test_setting_client(self):
        def compare_clients(x, y):
            self.assertEqual(x.id, y.id)
            self.assertEqual(x.name, y.name)
            self.assertEqual(x.secret, y.secret)

        c1 = Client(0, 'name', self.correctSecret)
        self.handler.set_ipv4_address(c1, '178.93.23.200', 3000)

        c2 = self.handler.get_by_id(c1.id)
        compare_clients(c1, c2)

        c3 = self.handler.get_by_name('name')
        compare_clients(c1, c3)

    def test_setting_client_ttl(self):
        c1 = Client(0, 'name', self.correctSecret)
        self.handler.set_ipv4_address(c1, '178.93.23.200', 3000)
        self.assertGreater(self.handler._redis().ttl(c1.id), self.handler.default_address_ttl - 10)
        self.assertGreater(self.handler._redis().ttl(f'{c1.id}:178.93.23.200'), self.handler.default_address_ttl - 10)

    def test_getting_client_valid(self):
        c1 = Client(0, 'name', self.correctSecret)
        self.handler.set_ipv4_address(c1, '127.0.0.1', 3000)

        c2 = self.handler.get_by_id(c1.id)
        self.assertIsNotNone(c2)

    def test_getting_client_invalid(self):
        with self.assertRaises(AssertionError):
            self.handler.get_by_id(-1)

        c1 = self.handler.get_by_id(1)
        self.assertIsNone(c1)

    def test_getting_client_by_name_invalid(self):
        with self.assertRaises(AssertionError):
            self.handler.get_by_name('')

        c1 = self.handler.get_by_name('undefined')
        self.assertIsNone(c1)

    def test_setting_ipv4_address(self):
        valid_addresses = ['178.93.23.200', '178.93.23.201', '178.93.23.202']

        c1 = Client(0, 'name', self.correctSecret)
        for address in valid_addresses:
            self.handler.set_ipv4_address(c1, address, 3000)

        ip_addresses = self.handler.get_ipv4_addresses(c1.id)
        self.assertIs(type(ip_addresses), list)

        for address in ip_addresses:
            self.assertIn(address, valid_addresses)

    def test_setting_ipv4_address_invalid(self):
        c1 = Client(0, 'name', self.correctSecret)

        with self.assertRaises(OSError):
            self.handler.set_ipv4_address(c1, '', 3000)

        with self.assertRaises(OSError):
            self.handler.set_ipv4_address(c1, '178.93.23.2000000', 3000)

        with self.assertRaises(AssertionError):
            self.handler.set_ipv4_address(c1, '178.93.23.200', -1)

        with self.assertRaises(AssertionError):
            self.handler.set_ipv4_address(c1, '178.93.23.200', 300000)

    def test_getting_ipv4_address_and_ports(self):
        valid_addresses = ['178.93.23.200', '178.93.23.201', '178.93.23.202']

        c1 = Client(0, 'name', self.correctSecret)
        for address in valid_addresses:
            self.handler.set_ipv4_address(c1, address, 3000)

        ip_addresses_and_ports = self.handler.get_ipv4_addresses_and_ports(c1.id)
        self.assertIs(type(ip_addresses_and_ports), list)

        for address, port in ip_addresses_and_ports:
            self.assertIn(address, valid_addresses)
            self.assertEqual(port, 3000)