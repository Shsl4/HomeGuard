import socket
from HomeGuard.utils.mac_database import MacDatabase
from HomeGuard.log.logger import Logger
from netifaces import AF_INET, AF_LINK, ifaddresses
from netaddr import IPNetwork
from scapy.all import conf, srp
from scapy.layers.l2 import Ether, ARP

class Adapter:

    @staticmethod
    def main_adapter():
        return conf.route.route("0.0.0.0")[0]

    @staticmethod
    def get_ip():
        return conf.route.route("0.0.0.0")[1]

    @staticmethod
    def get_broadcast():
        return ifaddresses(Adapter.main_adapter())[AF_INET][0]['broadcast']

    @staticmethod
    def get_netmask():
        return ifaddresses(Adapter.main_adapter())[AF_INET][0]['netmask']

    @staticmethod
    def get_mac():
        return ifaddresses(Adapter.main_adapter())[AF_LINK][0]['addr']

    @staticmethod
    def get_gateway():
        return conf.route.route("0.0.0.0")[2]

    @staticmethod
    def get_network():
        my_ip = Adapter.get_ip()
        mask = Adapter.get_netmask()
        return IPNetwork(f'{my_ip}/{mask}')

    @staticmethod
    def get_cidr():
        return str(Adapter.get_network().cidr)

    @staticmethod
    def is_same_subnet(ip):
        return ip in Adapter.get_network()

    @staticmethod
    def arp_scan(target, timeout=1.0):

        if not Adapter.is_same_subnet(target):
            Logger.log('Trying to scan adresses on a different subnet. No response can be obtained.')
            return

        Logger.log(f'Starting arp scan on {target}')

        ans, _ = srp(Ether(dst='ff:ff:ff:ff:ff:ff') / ARP(pdst=target), timeout=timeout)

        if len(ans) == 0:
            Logger.log('No response obtained.')

        for snd, rcv in ans:
            ip = rcv.sprintf(r"%ARP.psrc%")
            mac = rcv.sprintf(r"%Ether.src%")
            hostname, _ = socket.getnameinfo((ip, 0), 0)
            if hostname == ip:
                Logger.log(f'{ip} -> {mac} ({MacDatabase.get(mac)})')
            else:
                Logger.log(f'{ip} -> {hostname} ({mac}, {MacDatabase.get(mac)})')
