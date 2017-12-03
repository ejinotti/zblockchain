import json

from http.server import BaseHTTPRequestHandler

from block import Block
from chain import Chain
from utils import put_message


def get_handler(queue):
    class NodeHandler(BaseHTTPRequestHandler):
        def parse_path(self):
            return self.path.split('?', 1)[0]

        def send_json(self, data, status=200):
            if not isinstance(data, str):
                data = json.dumps(data)
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(data.encode('utf8'))

        def do_GET(self):
            path = self.parse_path()
            if path == '/chain':
                self.chain()
            elif path == '/chain_length':
                self.chain_length()
            else:
                self.send_response(404)
                self.end_headers()

        def chain(self):
            self.send_json(Chain.local_json())

        def chain_length(self):
            self.send_json({'length': Chain.local_length()})

        def do_POST(self):
            path = self.parse_path()
            if path == '/block':
                self.new_block()
            else:
                self.send_response(404)
                self.end_headers()

        def new_block(self):
            content_length = int(self.headers['Content-Length'])
            block = Block(json.loads(self.rfile.read(content_length)))
            print(f'Received remote block: {block}')
            code = 200 if put_message(queue, block) else 503
            self.send_response(code)
            self.end_headers()

    return NodeHandler
