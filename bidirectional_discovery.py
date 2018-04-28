import socket
import _thread
import time

DEFAULT_PORT = 65000
DEFAULT_DELAY = 3

class Discovery:
    def __init__(self, data, address, time):
        self.data = data
        self.address = address
        self.time = time

class Bidirectional_discovery:
    def __init__(self):
        self.announcement_service = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.discovery_service = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.announcement_service.bind(('', 0))
        self.announcement_service.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self.stopped = True

    def start_announcement(self, data, delay=DEFAULT_DELAY, port=DEFAULT_PORT):
        self.stopped = False
        _thread.start_new(self.announce, (data, delay, port))

    def start_discovery(self, callback, delay=DEFAULT_DELAY, port=DEFAULT_PORT):
        self.stopped = False
        self.discovery_service.bind(('', port))
        self.discovered = []
        _thread.start_new(self.discover, (callback, port))
        _thread.start_new(self.handle_discoveries, (delay))

    def announce(self, data, delay=DEFAULT_DELAY, port=DEFAULT_PORT):
        while not self.stopped:
            self.announcement_service.sendto(data.encode(), ('<broadcast>', port))
            time.sleep(delay)

    def discover(self, callback, port=DEFAULT_PORT):
        while not self.stopped:
            data, address = self.discovery_service.recvfrom(1024)
            data = data.decode()
            if address not in [discovery.address for discovery in self.discovered]:
                self.discovered.append(Discovery(data, address, int(time.strftime("%S", time.gmtime()))))
                callback(data)

    def handle_discoveries(self, delay=DEFAULT_DELAY):
        while not self.stopped:
            for discovery in range(len(self.discovered)):
                if self.discovered[discovery].time > int(time.strftime("%S", time.gmtime())) + delay:
                    del self.discovered[discovery]
            time.sleep(delay)

    def stop_announcement(self):
        self.stopped = True

    def stop_discovery(self):
        self.stopped = True