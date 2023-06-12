import json
import typing as t
import uuid

from flask import Flask, send_from_directory, jsonify
from flask.json.provider import JSONProvider
from waitress import serve

from HomeGuard.data.event import EventManager, EventEncoder
from HomeGuard.data.identity import IdentityManager


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
        serve(self.__app, host='0.0.0.0', port=8080)

    def register_routes(self):
        @self.__app.route('/')
        def hello():
            return send_from_directory('templates/', 'home.html')

        @self.__app.route('/<path:path>')
        def distribute_public(path):
            return send_from_directory('static/', path)

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

        @self.__app.route('/event_setup')
        def event_setup():
            return send_from_directory('templates/', 'event_setup.html')
