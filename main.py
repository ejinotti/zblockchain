import argparse
import os

from http.server import HTTPServer

import config

from block import Block
from chain import Chain
from node import get_handler
from sync import sync_longest_chain
from worker import Worker


parser = argparse.ArgumentParser(description='zbc node')
parser.add_argument(
    '--port', '-p', type=int, default=3000, help='port to use')
parser.add_argument(
    '--mine', '-m', action='store_true', help='mine on this node?')
parser.add_argument(
    '--genesis', '-g', action='store_true', help='do genesis event?')
args = parser.parse_args()

config.port = args.port
config.data_dir = os.path.join(config.base_dir, str(args.port))

if not os.path.exists(config.data_dir):
    os.makedirs(config.data_dir)

if args.genesis:
    print('Beginning genesis..')
    if Chain.local_length():
        raise Exception('Cannot do genesis when blocks already exist.')
    genesis_block = Block.genesis_block()
    chain = Chain([genesis_block])
    chain.save()
    print(f'Created genesis block: {genesis_block}')
else:
    print('Finding longest chain..')
    chain = sync_longest_chain()

worker = Worker(chain, args.mine)
worker.start()

handler = get_handler(worker.queue)
server = HTTPServer(('localhost', args.port), handler)
print(f'Starting server on port {args.port}.')

try:
    server.serve_forever()
except KeyboardInterrupt:
    pass

worker.terminate()
server.server_close()

print('\nServer closed.')
