from __future__ import division, print_function, unicode_literals
import logging
from telnetlib import Telnet
import time


class Keyboard:
    def __init__(self):
        self._host = "rpi"
        self._port = 1235

    def __enter__(self):
        """
        :rtype: Keyboard
        """
        self._telnet = Telnet(host=self._host, port=self._port)
        welcome = self._telnet.read_some()
        logging.debug("Telnet: Welcome: " + welcome)
        assert welcome == 'ser2net port 1235 device /dev/ttyAMA0 [115200 N81]'
        time.sleep(1.0)
        second_line = self._telnet.read_some()
        assert second_line == ' (Debian GNU/Linux)'
        return self

    def _send_packet(self, packet):
        """
        :type packet: str
        :rtype: str
        """
        assert type(packet) == str
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
        str_to_write = b'0' + str(key) + b'00'
        return self._send_packet(str_to_write) == key

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._telnet.close()


def main():
    keys = b'1234\n'
    with Keyboard() as keyboard:
        for key in keys:
            assert keyboard.send_key(key), "Key: " + key
            time.sleep(0.05)


if __name__ == '__main__':
    main()