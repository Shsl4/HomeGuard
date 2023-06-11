import os
import random
import string
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

import schedule
from dotenv import load_dotenv
from scapy.config import conf
from scapy.layers.inet import IP, UDP
from scapy.layers.netbios import NBNSQueryRequest
from scapy.sendrecv import sniff, sr1, srp, send
from scapy.volatile import RandShort

from HomeGuard.bots.bot import Bot
from HomeGuard.bots.discord_bot import DiscordBot
from HomeGuard.data.event import EventManager, TimeWindow, Event
from HomeGuard.data.identity import IdentityManager
from HomeGuard.log.logger import Logger
from HomeGuard.net.adapter import Adapter
from HomeGuard.net.session import Session


class Engine:

    def __init__(self):

        conf.verb = 0

        self.__identity_manager = IdentityManager()
        self.__event_manager = EventManager()
        self.__bots: list[Bot] = []
        self.executor = ThreadPoolExecutor()

        event: Event = self.__event_manager.event('Main')
        trigger = event.create_trigger()

        trigger.add_day(11)
        trigger.add_month(6)
        trigger.update_time_window(TimeWindow(0, 24))

        self.__event_manager.write_events()

    def run_scheduler(self):

        schedule.every().day.at("00:00").do(self.__event_manager.reset_events)

        while True:
            schedule.run_pending()
            time.sleep(1.0)

    def run(self):

        load_dotenv()

        Logger.log("Starting HomeGuard...")
        Logger.log(
            f'Using {Adapter.main_adapter()} with ip {Adapter.get_ip()} and hardware address {Adapter.get_mac()}')
        Logger.log(
            f'The gateway is {Adapter.get_gateway()} with netmask {Adapter.get_netmask()} ({Adapter.get_cidr()})')

        self.executor.submit(self.console_thread)
        self.executor.submit(self.run_scheduler)

        self.try_start_discord_bot()

        sniff(session=Session, store=False, session_kwargs={'engine': self})

    def generate_name(self):
        string_length = random.randint(1, 15)
        letters_and_digits = string.ascii_letters + string.digits
        return ''.join(random.choice(letters_and_digits) for i in range(string_length))

    def console_thread(self):

        manager = self.__identity_manager
        event_manager = self.__event_manager

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

    def try_start_discord_bot(self):

        bot = DiscordBot(os.getenv('WEBHOOK_URL'))

        try:
            bot.launch()
            self.__bots.append(bot)
        except Exception as e:
            print(e.args[0])

    def notify(self, name: str | None, ip: str | None, mac: str):

        identity = self.__identity_manager.identity(name, ip, mac)

        if identity is None:
            return

        trigger = self.__event_manager.trigger(identity.uuid)

        if trigger is None:
            return

        for bot in self.__bots:
            bot.notify_activity(identity, trigger)

    def identity_manager(self) -> IdentityManager:
        return self.__identity_manager

    def event_manager(self) -> EventManager:
        return self.__event_manager
