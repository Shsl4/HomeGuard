import datetime
import os
import random
import string
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

import schedule
from dotenv import load_dotenv
from scapy.config import conf
from scapy.sendrecv import sniff

from HomeGuard.bots.bot import Bot
from HomeGuard.bots.discord_bot import DiscordBot
from HomeGuard.data.event import EventManager, Event, Weekdays
from HomeGuard.data.identity import IdentityManager
from HomeGuard.log.logger import Logger
from HomeGuard.net.adapter import Adapter
from HomeGuard.net.session import Session
from HomeGuard.webserver.webserver import WebServer


class Engine:

    def __init__(self):

        conf.verb = 0

        self.__identity_manager = IdentityManager()
        self.__event_manager = EventManager()
        self.__bots: list[Bot] = []
        self.__executor = ThreadPoolExecutor()
        self.__webserver = WebServer(self)

        event: Event = self.__event_manager.event('Main')
        trigger = event.get_trigger()

        trigger.update_date_range(datetime.date(2023, 6, 1), datetime.date(2023, 6, 30))
        trigger.update_time_range(datetime.time(0, 0), datetime.time(23, 59))
        trigger.add_weekday(Weekdays.Tuesday)
        trigger.add_weekday(Weekdays.Friday)
        trigger.add_weekday(Weekdays.Sunday)

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

        self.__executor.submit(self.console_thread)
        self.__executor.submit(self.run_scheduler)
        self.__executor.submit(self.__webserver.run)

        self.setup_discord_webhook()

        sniff(session=Session, store=False, session_kwargs={'engine': self})

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
                Logger.log('Dumped to identities.json')

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
                    Logger.log(Adapter.arp_scan(args[1]))
                elif len(args) == 3:
                    Logger.log(Adapter.arp_scan(args[1], float(args[2])))

            elif command == 'netbios':

                if len(args) < 2:
                    Logger.log('This command requires more arguments.')
                    continue

                Adapter.send_netbios_name_request(args[1])
                Logger.log('Sent NetBIOS name request.')

            elif command == 'send':
                if len(args) < 2:
                    print('This command requires more arguments.')
                    continue

            else:
                Logger.log(f'Unrecognized command: {command}')

    def setup_discord_webhook(self):

        bot = DiscordBot(os.getenv('WEBHOOK_URL'))

        try:
            bot.launch()
            self.__bots.append(bot)
        except Exception as e:
            Logger.log(e.args[0])

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
