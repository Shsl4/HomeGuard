import os
import socket
from log.logger import Logger
from scapy.layers.l2 import Ether, ARP
from scapy.all import srp, conf
from utils.mac_database import MacDatabase

if __name__ == "__main__":

    conf.verb = 0

    logger = Logger(os.path.expanduser('~/HomeGuard.log'))
    logger.log("Starting HomeGuard...")
    db = MacDatabase()

    gateway = conf.route.route("0.0.0.0")[2]
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=gateway+'/24'), timeout=2)

    for snd, rcv in ans:
        ip = rcv.sprintf(r"%ARP.psrc%")
        mac = rcv.sprintf(r"%Ether.src%")
        name, _ = socket.getnameinfo((ip, 0), 0)
        if name == ip:
            logger.log(f'{ip} -> {mac} ({db.get(mac)})')
        else:
            logger.log(f'{ip} -> {name} ({mac}, {db.get(mac)})')

