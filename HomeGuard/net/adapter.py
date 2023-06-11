import os
import random
import socket

from netaddr import IPNetwork
from netifaces import AF_INET, AF_LINK, ifaddresses
from scapy.all import conf, srp
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether, ARP
from scapy.layers.netbios import NBNSHeader, NBNSQueryRequest
from scapy.sendrecv import send, sr1


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
            result.append((pkt[ARP].psrc, Adapter.host_name(pkt[ARP].psrc), pkt[Ether].src))

        return result

    @staticmethod
    def host_name(ip, port=137):
        return socket.getnameinfo((ip, port), 0)[0]

    @staticmethod
    def send_netbios_name_request(ip: str):

        trn_id = random.randint(1, 0xFFFF)

        header = NBNSHeader(NAME_TRN_ID=trn_id, NM_FLAGS='B')

        query = NBNSQueryRequest(SUFFIX="workstation",
                             QUESTION_NAME=b'*\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
                             QUESTION_TYPE='NBSTAT')

        pkt = IP(dst=ip) / UDP(sport=137, dport='netbios_ns') / header / query

        # Send package and do not wait for response. The response will be caught by the main sniff loop
        sr1(pkt, timeout=0.0001)

    @staticmethod
    def validate_mac(mac):
        return mac != 'ff:ff:ff:ff:ff:ff' and mac != '00:00:00:00:00:00'
