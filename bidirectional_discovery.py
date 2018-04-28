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

    def start_discovery(self, add_callback, remove_callback, delay=DEFAULT_DELAY, port=DEFAULT_PORT):
        self.stopped = False
        self.discovery_service.bind(('', port))
        self.discovered = []
        _thread.start_new(self.discover, (add_callback, port))
        _thread.start_new(self.handle_discoveries, (remove_callback, delay))

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

    def handle_discoveries(self, callback, delay=DEFAULT_DELAY):
        while not self.stopped:
            for discovery in range(len(self.discovered)):
                if self.discovered[discovery].time > int(time.strftime("%S", time.gmtime())) + 2 * delay:
                    del self.discovered[discovery]
                    callback(discovery)
            time.sleep(1)

    def stop_discovery(self):
        self.stopped = True