import time
from telnetlib import Telnet
from contextlib import closing

with closing(Telnet("rpi", 1235)) as tn:
    start_time = time.time()
    while time.time() - start_time < 1.0:
        welcome = tn.read_eager()
    print "Welcome", welcome
    str_to_write = b'0100'
    tn.write(str_to_write)
    writen = tn.read_some()
    print "Writen", writen
    assert writen == str_to_write[1]
