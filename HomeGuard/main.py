import netifaces
from netaddr import IPNetwork
from scapy.all import *
from scapy.all import srp, conf
from scapy.layers.dhcp import DHCP
from scapy.layers.dns import DNS, DNSRR, DNSTextField
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
    def __proc_find_name(count, elem) -> str:
        if count > 0:
            for x in range(0, count):
                idx = elem[x].rrname.find(b'._device-info')
                if idx >= 0:
                    return elem[x].rrname[:idx].decode('utf-8')
        return None

    @staticmethod
    def dns_get_device_name(pkt: DNS) -> str:

        procs = [(pkt.arcount, pkt.ar), (pkt.ancount, pkt.an), (pkt.nscount, pkt.ns)]

        for proc in procs:
            result = MySession.__proc_find_name(proc[0], proc[1])
            if result is not None:
                return result

        if pkt.qdcount > 0:
            for x in range(0, pkt.qdcount):
                idx = pkt.qd[x].qname.find(b'._device-info')
                if idx >= 0:
                    return pkt.qd[x].qname[:idx].decode('utf-8')

        return None

    @staticmethod
    def expand(x):
        yield x
        while x.payload:
            x = x.payload
            yield x
    def handle_packet(self, pkt: Packet):

        if DHCP in pkt:
            dhcp_packet: DHCP = pkt[DHCP]
            if MySession.dhcp_is_request(dhcp_packet):
                print(f'{MySession.dhcp_get_hostname(dhcp_packet)} ({str(pkt.src)}) sent a DHCP request.')

        if DNS in pkt:
            dns_packet: DNS = pkt[DNS]
            dev_name = MySession.dns_get_device_name(dns_packet)
            if dev_name is not None:
                print(f'Registered device activity: {dev_name}')


        if IP in pkt:
            source = pkt[IP].src
            source_mac = pkt[Ether].src
            dest = pkt[IP].dst
            dest_mac = pkt[Ether].dst
            gateway: str = conf.route.route("0.0.0.0")[1]
            sub = gateway[:gateway.rindex('.')]
            if self.addresses.count(source) == 0:
                logger.log(f'New activity detected: {source} ({db.get(source_mac)}: {source_mac})')
                self.addresses.append(source)
            if self.addresses.count(dest) == 0:
                logger.log(f'New activity detected: {dest} ({db.get(dest_mac)}: {dest_mac})')
                self.addresses.append(dest)


def multicast_arp():

    route = conf.route.route("0.0.0.0")
    adapter = route[0]
    my_ip: str = route[1]
    gateway: str = route[2]
    data = netifaces.ifaddresses(adapter)
    mask = data[netifaces.AF_INET][0]['netmask']
    net = IPNetwork(f'{gateway}/{mask}')
    ping_dst = net.cidr
    logger.log(f'Starting arp scan on {ping_dst}')

    for addr in net.iter_hosts():
        ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=str(addr)), timeout=0.1)

        if len(ans) == 0:
            print(f'{addr} -> No response\r', end='')
            continue

        for snd, rcv in ans:
            ip = rcv.sprintf(r"%ARP.psrc%")
            mac = rcv.sprintf(r"%Ether.src%")
            hostname, _ = socket.getnameinfo((ip, 0), 0)
            if hostname == ip:
                print(f'{ip} -> {mac} ({db.get(mac)})')
            else:
                print(f'{ip} -> {hostname} ({mac}, {db.get(mac)})')




if __name__ == "__main__":
    conf.verb = 0

    logger.log("Starting HomeGuard...")

    # multicast_arp()

    sniff = sniff(session=MySession, store=False)
