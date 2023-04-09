from concurrent.futures.thread import ThreadPoolExecutor
from scapy.layers.inet import IP
from scapy.all import *
from log.logger import Logger
from scapy.layers.l2 import Ether, ARP
from scapy.all import srp, conf
from utils.mac_database import MacDatabase

db = MacDatabase()
logger = Logger(os.path.expanduser('~/HomeGuard.log'))


class MySession(DefaultSession):

    def __init__(self, prn=None, store=False, supersession=None, *args, **karg):
        super().__init__(prn, store, supersession, *args, **karg)
        self.__count = 0
        self.addresses = []

    def on_packet_received(self, pkt):
        if not pkt:
            return
        if not isinstance(pkt, Packet):
            raise TypeError("Only provide a Packet.")
        self.__count += 1
        self.handle_packet(pkt)

    def handle_packet(self, pkt: Packet):
        if IP in pkt:
            source = pkt[IP].src
            source_mac = pkt[Ether].src
            if self.addresses.count(source) == 0 and str(source).startswith("192.168.1"):
                logger.log(f'New address: {source} ({db.get(source_mac)}: {source_mac})')
                self.addresses.append(source)


def multicast_arp():
    gateway = conf.route.route("0.0.0.0")[2]
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=gateway + '/24'), timeout=5)

    for snd, rcv in ans:
        ip = rcv.sprintf(r"%ARP.psrc%")
        mac = rcv.sprintf(r"%Ether.src%")
        name, _ = socket.getnameinfo((ip, 0), 0)
        if name == ip:
            logger.log(f'{ip} -> {mac} ({db.get(mac)})')
        else:
            logger.log(f'{ip} -> {name} ({mac}, {db.get(mac)})')


if __name__ == "__main__":

    conf.verb = 0
    executor = ThreadPoolExecutor(max_workers=10)

    logger.log("Starting HomeGuard...")

    sniff = sniff(session=MySession, store=False)
