import logging
import socket
from telnetlib import Telnet
import time


class Keyboard:
    def __init__(self):
        self._host = "rpi"
        self._port = 1235
        self._telnet = None

    def __enter__(self):
        """
        :rtype: Keyboard
        """
        assert self._telnet is None
        try:
            self._telnet = Telnet(host=self._host, port=self._port, timeout=5.0)
        except socket.error as se:
            raise socket.error("Cannot connect to %s:%d. %s" % (self._host, self._port, str(se)))

        welcome = self._telnet.read_some()
        logging.debug("Telnet: Welcome: " + welcome)
        assert welcome == 'ser2net port 1235 device /dev/ttyAMA0 [115200 N81]', welcome
        time.sleep(1.0)
        second_line = self._telnet.read_some()
        assert second_line == ' (Debian GNU/Linux)'
        return self

    def _send_packet(self, packet):
        """
        :type packet: bytes
        :rtype: bytes
        """
        assert type(packet) == bytes
        assert len(packet) == 4
        self._telnet.write(packet)
        written = self._telnet.read_some()
        logging.debug("Telnet: Written: " + written)
        return written

    def send_key(self, key):
        """
        :type key: str
        :rtype: bool
        """
        assert len(key) == 1
        str_to_write = b'0' + key.encode() + b'00'
        return self._send_packet(str_to_write) == key

    # noinspection PyUnusedLocal
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._telnet.close()
        self._telnet = None


def test():
    keys = b'1234\n'
    with Keyboard() as keyboard:
        for key in keys:
            assert keyboard.send_key(key), "Key: " + key
            time.sleep(0.05)


if __name__ == '__main__':
    test()
