import json
import os
from urllib.parse import urlparse

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler

from jupyterhub.services.auth import HubAuthenticated


class NotebookHandler(HubAuthenticated, RequestHandler):
    def set_default_headers(self):
        self.set_header('content-type', 'application/json')
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, PUT, DELETE, OPTIONS")

    def initialize(self, storage):
        self.storage = storage

    def get(self):
        self.set_header('content-type', 'application/json')
        self.write(json.dumps(self.storage.get('data', []), indent=2, sort_keys=True))

    def post(self):
        self.set_header('content-type', 'application/json')
        try:
            data = json.loads(self.request.body.decode('utf-8'))
            print("Received data:", data)
            
            
            if (len(self.storage.setdefault('data', [])) == 0):
                self.storage.setdefault('data', []).append(data)
            else :
                self.storage.get('data', [])[0] = data
            
            self.write(json.dumps({'status': 'success', 'received': data}, indent=2))
        except json.JSONDecodeError:
            self.set_status(400)
            self.write(json.dumps({'error': 'Invalid JSON'}, indent=2))

    def options(self):
        self.set_status(204)
        self.finish()


def main():
    shared_storage = {}

    app = Application(
        [
            (os.environ['JUPYTERHUB_SERVICE_PREFIX'] + '/?', NotebookHandler, dict(storage=shared_storage)),
            (r'.*', NotebookHandler, dict(storage=shared_storage)),
        ]
    )
    http_server = HTTPServer(app)
    url = urlparse(os.environ['JUPYTERHUB_SERVICE_URL'])

    http_server.listen(url.port, url.hostname)
    IOLoop.current().start()


if __name__ == '__main__':
    main()
