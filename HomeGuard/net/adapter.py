import os
import socket

from netaddr import IPNetwork
from netifaces import AF_INET, AF_LINK, ifaddresses
from scapy.all import conf, srp, sr1
from scapy.layers.l2 import Ether, ARP
from scapy.layers.inet import IP, UDP
from scapy.layers.netbios import NBNSHeader, NBNSNodeStatusRequest
from HomeGuard.log.logger import Logger
from HomeGuard.utils.mac_database import MacDatabase


class Adapter:

    @staticmethod
    def main_adapter():

        adapter = conf.route.route("0.0.0.0")[0]

        if os.name == 'nt':
            return adapter[adapter.index('{'): adapter.index('}') + 1]

        return adapter

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

        ans, _ = srp(Ether(dst='ff:ff:ff:ff:ff:ff') / ARP(pdst=target), timeout=timeout)

        result = []

        for _, pkt in ans:
            result.append((pkt[ARP].psrc, Adapter.netbios_name(pkt[ARP].psrc), pkt[Ether].src))

        return result

    @staticmethod
    def netbios_name(ip, port=137):
        return socket.getnameinfo((ip, port), 0)[0]

    @staticmethod
    def validate_mac(mac):
        return mac != 'ff:ff:ff:ff:ff:ff' and mac != '00:00:00:00:00:00'
