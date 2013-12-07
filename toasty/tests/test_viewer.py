from threading import Thread
import SocketServer
import sys
import os
from urllib import urlopen

from ..viewer import SimpleWWTHandler


def cwd():
    return os.path.split(os.path.abspath(__file__))[0]

class TestViewer(object):
    def setup_class(cls):
        sys.argv.append(os.path.join(cwd(), 'test_sky'))
        PORT = 8000
        cls.server = SocketServer.TCPServer(("", PORT), SimpleWWTHandler)
        cls.thread = Thread(target=cls.server.serve_forever)
        cls.thread.start()

    def teardown_class(cls):
        cls.server.shutdown()

    def test_wtml(self):
        data = urlopen('http://0.0.0.0:8000/toasty.wtml').read()
        assert '<ImageSet' in data

    def test_root(self):
        data = urlopen('http://0.0.0.0:8000/').read()
        assert 'WWTCanvas' in data
