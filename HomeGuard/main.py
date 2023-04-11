import os

import netifaces
from netaddr import IPNetwork
from scapy.all import *
from scapy.all import srp, conf
from scapy.layers.dhcp import DHCP
from scapy.layers.dns import DNS
from scapy.layers.inet import IP
from scapy.layers.l2 import Ether, ARP

from log.logger import Logger
from utils.mac_database import MacDatabase

db = MacDatabase()
logger = Logger(os.path.expanduser('~/HomeGuard.log'))


class MySession(DefaultSession):

    def __init__(self, prn=None, store=False, supersession=None, *args, **karg):
        super().__init__(prn, store, supersession, *args, **karg)
        self.__count = 0
        self.addresses = []
        logger.log('Started sniff session.')

    def on_packet_received(self, pkt):
        if not pkt:
            return
        if not isinstance(pkt, Packet):
            raise TypeError("Only provide a Packet.")
        self.__count += 1
        self.handle_packet(pkt)

    @staticmethod
    def dhcp_is_request(pkt: DHCP) -> bool:
        for opt in pkt.options:
            if isinstance(opt, tuple) and opt[0] == "message-type":
                if opt[1] == 3:
                    return True
        return False

    @staticmethod
    def dhcp_get_hostname(pkt: DHCP):
        options: list = pkt.options
        for opt in options:
            if isinstance(opt, tuple) and opt[0] == 'hostname':
                return opt[1].decode("utf-8")
        return ''

    @staticmethod
    def dns_is_local(pkt: DNS):
        if pkt.qdcount > 0:
            qname = pkt.qd.qname.decode('utf-8')
            return qname[-7:] == '.local.'
        return False

    def handle_packet(self, pkt: Packet):

        if DHCP in pkt:
            dhcp_packet: DHCP = pkt[DHCP]
            if MySession.dhcp_is_request(dhcp_packet):
                print(f'{MySession.dhcp_get_hostname(dhcp_packet)} ({str(pkt.src)}) sent a DHCP request.')

        if DNS in pkt:
            dns_packet: DNS = pkt[DNS]
            if MySession.dns_is_local(dns_packet):
                print(dns_packet.qd.qname.decode('utf-8'))

        if IP in pkt:
            source = pkt[IP].src
            source_mac = pkt[Ether].src
            dest = pkt[IP].dst
            dest_mac = pkt[Ether].dst
            gateway: str = conf.route.route("0.0.0.0")[1]
            sub = gateway[:gateway.rindex('.')]
            if self.addresses.count(source) == 0 and str(source).startswith(sub):
                logger.log(f'New address: {source} ({db.get(source_mac)}: {source_mac})')
                self.addresses.append(source)
            if self.addresses.count(dest) == 0 and str(dest).startswith(sub):
                logger.log(f'New address: {dest} ({db.get(dest_mac)}: {dest_mac})')
                self.addresses.append(dest)


def multicast_arp():

    route = conf.route.route("0.0.0.0")
    adapter = route[0]
    my_ip: str = route[1]
    gateway: str = route[2]
    data = netifaces.ifaddresses(adapter)
    mask = data[2][0]['netmask']
    net = IPNetwork(f'{gateway}/{mask}')
    ping_dst = str(net.cidr)

    logger.log(f'Starting multicast arp scan on {ping_dst}.')

    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ping_dst), timeout=5)

    for snd, rcv in ans:
        ip = rcv.sprintf(r"%ARP.psrc%")
        mac = rcv.sprintf(r"%Ether.src%")
        hostname, _ = socket.getnameinfo((ip, 0), 0)
        if hostname == ip:
            logger.log(f'{ip} -> {mac} ({db.get(mac)})')
        else:
            logger.log(f'{ip} -> {hostname} ({mac}, {db.get(mac)})')


if __name__ == "__main__":
    conf.verb = 0

    logger.log("Starting HomeGuard...")

    # multicast_arp()

    sniff = sniff(session=MySession, store=False)
