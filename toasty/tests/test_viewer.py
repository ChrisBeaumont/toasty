from threading import Thread
try:
    from SocketServer import TCPServer
    from urllib import urlopen
except ImportError:  # python 3.X
    from socketserver import TCPServer
    from urllib.request import urlopen

import sys
import os

from ..viewer import SimpleWWTHandler


def cwd():
    return os.path.split(os.path.abspath(__file__))[0]


class TestViewer(object):
    def setup_class(cls):
        sys.argv.append(os.path.join(cwd(), 'test_sky'))
        PORT = 8000
        # configure to immediately release the socket on close
        # http://stackoverflow.com/questions/17659334
        cls.server = TCPServer(("", PORT), SimpleWWTHandler, False)
        cls.server.allow_reuse_address = True
        cls.server.server_bind()
        cls.server.server_activate()

        cls.thread = Thread(target=cls.server.serve_forever)
        cls.thread.start()

    def teardown_class(cls):
        cls.server.shutdown()

    def test_wtml(self):
        data = urlopen('http://0.0.0.0:8000/toasty.wtml').read()
        assert '<ImageSet' in str(data)

    def test_root(self):
        data = urlopen('http://0.0.0.0:8000/').read()
        assert 'WWTCanvas' in str(data)
