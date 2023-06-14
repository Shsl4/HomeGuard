import json
import typing as t
import uuid

from flask import Flask, send_from_directory, jsonify, request
from flask.json.provider import JSONProvider
from waitress import serve

from HomeGuard.data.event import EventManager, EventEncoder, Event
from HomeGuard.data.identity import IdentityManager, DeviceIdentity


class FlaskJSONProvider(JSONProvider):

    def dumps(self, obj: t.Any, **kwargs: t.Any) -> str:
        return json.dumps(obj, cls=EventEncoder, indent=2)

    def loads(self, s: str | bytes, **kwargs: t.Any) -> t.Any:
        return json.loads(s)


class WebServer:

    def __init__(self, engine):
        self.__app = Flask(__name__)
        self.__engine = engine
        self.__app.json = FlaskJSONProvider(self.__app)
        self.register_routes()

    def run(self):
        try:
            serve(self.__app, host='0.0.0.0', port=8080)
        except BaseException as e:
            print(f'Webserver thread crashed! {e}')

    def register_routes(self):
        @self.__app.route('/')
        def hello():
            return send_from_directory("templates/", 'home.html')

        @self.__app.route('/<path:path>')
        def distribute_public(path):
            return send_from_directory("static/", path)

        @self.__app.route('/event/<path:path>')
        def get_event(path):
            manager: EventManager = self.__engine.event_manager()

            if manager.event_exists(path):
                json_object = {
                    "result": True,
                    "data": manager.event(path)
                }

                return jsonify(json_object)

            return jsonify({"result": False})

        @self.__app.route('/device/<path:path>')
        def get_device(path):

            manager: IdentityManager = self.__engine.identity_manager()

            try:

                device_id = uuid.UUID(path)
                identity = manager.identity_by_id(device_id)

                if identity is not None:

                    json_object = {
                        "result": True,
                        "device": identity
                    }

                    return jsonify(json_object)

            except ValueError:
                pass

            return jsonify({"result": False})

        @self.__app.route('/events')
        def get_events():
            manager: EventManager = self.__engine.event_manager()
            return jsonify(manager.events())

        @self.__app.route('/devices')
        def get_devices():
            manager: IdentityManager = self.__engine.identity_manager()
            return jsonify(manager.identities())

        @self.__app.route('/webhook-status')
        def webhook_status():
            return jsonify({"result": self.__engine.discord_webhook_status()})

        @self.__app.route('/event-view', methods=['FETCH'])
        def event_setup():
            return send_from_directory("templates/", 'event-view.html')

        @self.__app.route('/create_event', methods=['POST'])
        def create_event():

            data = request.json

            try:

                parsed_event = Event.parse(data)
                result = self.__engine.event_manager().add_event(parsed_event)

                if result is not True:
                    raise RuntimeError(f'The event named {parsed_event.name()} already exists.')

                self.__engine.event_manager().write_events()

                return jsonify({
                    "result": True,
                    "status": f"Created and registered event {parsed_event.name()}"
                })

            except BaseException as e:
                return jsonify({"result": False, "status": str(e)})

        @self.__app.route('/edit-event', methods=['POST'])
        def edit_event():

            data = request.json

            try:

                parsed_event = Event.parse(data)
                self.__engine.event_manager().event(data['old_name']).replace_with(parsed_event)
                self.__engine.event_manager().write_events()

                return jsonify({
                    "result": True,
                    "status": f"Edited event {data['old_name']}"
                })

            except BaseException as e:
                return jsonify({"result": False, "status": str(e)})

        @self.__app.route('/edit-device', methods=['POST'])
        def edit_device():

            data = request.json

            try:

                identity: DeviceIdentity = self.__engine.identity_manager().identity_by_id(uuid.UUID(data['uuid']))

                if identity is None:
                    raise RuntimeError(f'Error: {data["uuid"]} is not a valid device id.')

                identity.display_name = data['display_name']
                identity.mac_address = data['mac_address']
                identity.ip_addresses = set(data['ip_addresses'])

                self.__engine.identity_manager().write_identities()

                return jsonify({
                    "result": True,
                    "status": f"Edited device {data['display_name']}"
                })

            except BaseException as e:
                return jsonify({"result": False, "status": str(e)})

        @self.__app.route('/forget-device', methods=['POST'])
        def forget_device():

            data = request.json

            try:
                if self.__engine.forget_device(uuid.UUID(data['uuid'])) is False:
                    raise RuntimeError(f'Error: {data["uuid"]} is not a valid device id.')

                return jsonify({
                    "result": True,
                    "status": f"Forgotten device with id {data['uuid']}"
                })

            except BaseException as e:
                return jsonify({"result": False, "status": str(e)})

        @self.__app.route('/delete-event', methods=['POST'])
        def delete_event():

            data = request.json

            try:
                if self.__engine.delete_event(data['name']) is False:
                    raise RuntimeError(f'Error: {data["name"]} is not a valid event.')

                return jsonify({
                    "result": True,
                    "status": f"Deleted event {data['name']}"
                })

            except BaseException as e:
                return jsonify({"result": False, "status": str(e)})

        @self.__app.route('/update-webhook', methods=['POST'])
        def update_discord_webhook():

            data = request.json

            try:
                if self.__engine.reopen_discord_webhook(data['webhook_url']) is False:
                    raise RuntimeError(f'Error: {data["webhook_url"]} is not a valid webhook url.')

                return jsonify({
                    "result": True,
                    "status": f"Setup new webhook url."
                })

            except BaseException as e:
                return jsonify({"result": False, "status": str(e)})

        @self.__app.route('/device-view', methods=['FETCH'])
        def device_view():
            return send_from_directory("templates/", 'device-view.html')



