import os
import threading
import time
import uuid

import schedule
from dotenv import load_dotenv
from scapy.config import conf
from scapy.sendrecv import sniff

from HomeGuard.bots.discord_bot import DiscordBot
from HomeGuard.data.event import EventManager
from HomeGuard.data.identity import IdentityManager
from HomeGuard.net.adapter import Adapter
from HomeGuard.net.session import Session
from HomeGuard.webserver.webserver import WebServer


class Engine:

    def __init__(self):

        load_dotenv()

        conf.verb = 0

        self.__identity_manager = IdentityManager()
        self.__event_manager = EventManager()
        self.__discord_webhook: DiscordBot | None = None
        self.__webserver = WebServer(self)
        self.console_thread = None
        self.scheduler_thread = None
        self.webserver_thread = None

    def reset_events(self):
        self.__event_manager.reset_events()
        print('Event manager reset all avents.')

    def run_scheduler(self):

        schedule.every().day.at("00:00").do(self.reset_events)

        while True:
            schedule.run_pending()
            time.sleep(1.0)

    def run(self):

        load_dotenv()

        print("Starting HomeGuard...")
        print(
            f'Using {Adapter.main_adapter()} with ip {Adapter.get_ip()} and hardware address {Adapter.get_mac()}')
        print(
            f'The gateway is {Adapter.get_gateway()} with netmask {Adapter.get_netmask()} ({Adapter.get_cidr()})')

        self.console_thread = threading.Thread(target=self.console_func)
        self.scheduler_thread = threading.Thread(target=self.run_scheduler)
        self.webserver_thread = threading.Thread(target=self.__webserver.run)

        self.console_thread.daemon = True
        self.scheduler_thread.daemon = True
        self.webserver_thread.daemon = True

        self.console_thread.start()
        self.scheduler_thread.start()
        self.webserver_thread.start()

        self.setup_discord_webhook()

        print('Starting sniff session.')

        try:
            sniff(session=Session, store=False, session_kwargs={'engine': self})
        except BaseException as e:
            self.terminate_fatal(e)

    def terminate_fatal(self, e):
        self.__discord_webhook.notify_error('Sniff thread crashed!', e)
        exit(-1)

    def console_func(self):

        manager = self.__identity_manager
        event_manager = self.__event_manager

        try:
            while True:

                inp = input()

                if not inp:
                    continue

                args = inp.split(' ')
                command = args[0] if len(args) > 0 else 'None'

                if command == 'ids':
                    manager.print()

                elif command == 'dump':
                    manager.write_identities()
                    print('Dumped to identities.json')

                elif command == 'ev':
                    if len(args) < 2:
                        print('This command requires more arguments.')
                        continue

                    event_manager.event('Main').add_identity(uuid.UUID(args[1]))
                    event_manager.write_events()

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

                    Adapter.send_netbios_name_request(args[1])
                    print('Sent NetBIOS name request.')

                elif command == 'send':
                    if len(args) < 2:
                        print('This command requires more arguments.')
                        continue

                else:
                    print(f'Unrecognized command: {command}')

        except BaseException as e:

            # Exit input thread on error.
            print(f'Caught exception in input thread. {e}')
            print('Exiting input thread.')

    def setup_discord_webhook(self):

        self.__discord_webhook = DiscordBot(os.getenv('WEBHOOK_URL'))

        try:
            self.__discord_webhook.launch()
            print('Created discord webhook.')
        except Exception as e:
            print(e.args[0])

    def notify(self, name: str | None, ip: str | None, mac: str):

        identity = self.__identity_manager.identity(name, ip, mac)

        if identity is None:
            return

        trigger = self.__event_manager.trigger(identity.uuid)

        if trigger is None:
            return

        self.__discord_webhook.notify_activity(identity, trigger)

    def identity_manager(self) -> IdentityManager:
        return self.__identity_manager

    def event_manager(self) -> EventManager:
        return self.__event_manager
