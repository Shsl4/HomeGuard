from HomeGuard.log.logger import Logger
from HomeGuard.net.adapter import Adapter
from HomeGuard.net.session import Session
from scapy.all import sniff, conf

if __name__ == "__main__":

    conf.verb = 0

    Logger.log("Starting HomeGuard...")
    Logger.log(f'Using {Adapter.main_adapter()} with ip {Adapter.get_ip()} and hardware address {Adapter.get_mac()}')
    Logger.log(f'The gateway is {Adapter.get_gateway()} with netmask {Adapter.get_netmask()} ({Adapter.get_cidr()})')

    # Adapter.arp_scan(Adapter.get_cidr())

    sniff = sniff(session=Session, store=False)
