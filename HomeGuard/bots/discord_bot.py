import datetime
import uuid

import discord
from discord.webhook import SyncWebhook
import requests

from HomeGuard.bots.bot import Bot
from HomeGuard.data.event import Event, EventTrigger
from HomeGuard.data.identity import DeviceIdentity


class DiscordBot(Bot):

    def __init__(self, token: str):
        super().__init__(token)
        self.webhook_url = token
        self.webhook: None | SyncWebhook = None

    def launch(self):
        self.webhook = SyncWebhook.from_url(self.webhook_url, session=requests.Session())
        print('Created discord webhook.')

    def notify_activity(self, identity: DeviceIdentity, trigger: EventTrigger):

        if self.webhook is not None:

            embed = discord.Embed(
                title='Activity notification',
                colour=discord.Colour.blue(),
                description=f'A deviced triggered the \'{trigger.event().name()}\' event.',
                timestamp=datetime.datetime.now()
            )

            embed.add_field(name='Device name', value=identity.display_name)
            embed.add_field(name='UUID', value=identity.uuid)
            embed.add_field(name='MAC', value=identity.mac_address)

            embed.add_field(name='IP addresses', value=','.join(identity.ip_addresses), inline=False)

            self.webhook.send(username='HomeGuard', embed=embed)
