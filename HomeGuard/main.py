import threading

from HomeGuard.log.logger import Logger
from HomeGuard.net.adapter import Adapter
from HomeGuard.net.session import Session
from scapy.all import sniff, conf


def console_thread():

    session = Session()

    while True:

        inp = input()
        args = inp.split(' ')
        command = args[0] if len(args) > 0 else 'None'

        if command == 'ids':
            session.id_manager.print()

        elif command == 'dump':
            session.id_manager.write_identities()
            print('Dumped to identities.json')

        elif command == 'arp':
            if len(args) < 2:
                print('This command requires more arguments.')
                continue
            if len(args) == 2:
                print(Adapter.arp_scan(args[1]))
            elif len(args) == 3:
                print(Adapter.arp_scan(args[1], float(args[2])))

        elif command == 'netbios':
            if len(args) < 2:
                print('This command requires more arguments.')
                continue
            if len(args) == 2:
                print(Adapter.netbios_name(args[1]))
            elif len(args) == 3:
                print(Adapter.netbios_name(args[1], int(args[2])))

        else:
            print(f'Unrecognized command: {command}.')


if __name__ == "__main__":

    conf.verb = 0

    Logger.log("Starting HomeGuard...")
    Logger.log(f'Using {Adapter.main_adapter()} with ip {Adapter.get_ip()} and hardware address {Adapter.get_mac()}')
    Logger.log(f'The gateway is {Adapter.get_gateway()} with netmask {Adapter.get_netmask()} ({Adapter.get_cidr()})')

    th = threading.Thread(target=console_thread)
    th.start()

    sniff = sniff(session=Session, store=False)

    th.join()
