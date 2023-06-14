import json
import os

from HomeGuard.utils.resource_paths import ResourcePaths


class TokenManager:

    def __init__(self):
        self.discord_webhook_url = ''
        self.load_tokens()

    def as_dict(self):
        return {
            "discord_webhook_url": self.discord_webhook_url
        }

    def write_tokens(self):

        json_object = json.dumps(self.as_dict(), indent=2, ensure_ascii=False).encode('utf-8')

        filename = ResourcePaths.tokens_path()

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "w") as outfile:
            outfile.write(json_object.decode())

    def load_tokens(self):

        try:
            with open(ResourcePaths.tokens_path(), "r") as infile:
                json_data = json.loads(infile.read())

                self.discord_webhook_url = json_data['discord_webhook_url']

        except BaseException as e:
            print(f'Failed to open tokens data file: {e}')
