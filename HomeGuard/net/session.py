import threading

from scapy.all import *
from scapy.layers.dhcp import DHCP, DHCPOptionsField
from scapy.layers.dns import DNS
from scapy.layers.inet import IP
from scapy.layers.l2 import Ether, ARP
from scapy.layers.netbios import NBNSQueryResponse, NBNSQueryRequest

from HomeGuard.data.event import TimeWindow, Event
from HomeGuard.data.identity import IdentityManager
from HomeGuard.log.logger import Logger
from HomeGuard.net.adapter import Adapter


class Session(DefaultSession):

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, engine, prn=None, store=False, supersession=None, *args, **kwargs):

        super().__init__(prn, store, supersession, *args, **kwargs)
        self.engine = engine
        self.__count = 0
        self.addresses = []

        Logger.log('Started sniff session.')

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
    def __proc_find_name(count, elem) -> str:
        if count > 0:
            for x in range(0, count):
                idx = elem[x].rrname.find(b'._device-info')
                if idx >= 0:
                    return elem[x].rrname[:idx].decode('utf-8')

    @staticmethod
    def dns_get_device_name(pkt: DNS) -> str:

        procs = [(pkt.arcount, pkt.ar), (pkt.ancount, pkt.an), (pkt.nscount, pkt.ns)]

        for proc in procs:
            result = Session.__proc_find_name(proc[0], proc[1])
            if result is not None:
                return result

        if pkt.qdcount > 0:
            for x in range(0, pkt.qdcount):
                idx = pkt.qd[x].qname.find(b'._device-info')
                if idx >= 0:
                    return pkt.qd[x].qname[:idx].decode('utf-8')

    def handle_packet(self, pkt: Packet):

        source_mac = pkt[Ether].src
        dest_mac = pkt[Ether].dst

        if ARP in pkt:
            arp_pkt: ARP = pkt[ARP]
            source = arp_pkt.psrc
            dest = arp_pkt.pdst
            self.engine.notify(None, source, source_mac)
            self.engine.notify(None, dest, dest_mac)

        if IP in pkt:

            source = pkt[IP].src
            dest = pkt[IP].dst

            if DHCP in pkt:
                dhcp_packet: DHCP = pkt[DHCP]
                if Session.dhcp_is_request(dhcp_packet):
                    device_name = Session.dhcp_get_hostname(dhcp_packet)
                    self.engine.notify(device_name, source, source_mac)

            if DNS in pkt:
                dns_packet: DNS = pkt[DNS]
                dev_name = Session.dns_get_device_name(dns_packet)
                if dev_name is not None:
                    self.engine.notify(dev_name, source, source_mac)

            if NBNSQueryResponse in pkt:
                response: NBNSQueryResponse = pkt[NBNSQueryResponse]
                print(response.name)

            if Adapter.is_same_subnet(source):
                self.engine.notify(None, source, source_mac)

            if Adapter.is_same_subnet(dest):
                self.engine.notify(None, dest, dest_mac)
