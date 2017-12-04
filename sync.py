import json

from functools import partial
from urllib.request import Request, urlopen

import config

from chain import Chain
from utils import parallel, parallel_nowait


def peer_urls():
    my_port = str(config.port)
    return [url for url in config.node_urls if not url.endswith(my_port)]


def sync_longest_chain():
    def get_chain_length(url):
        url += '/chain_length'
        try:
            res = urlopen(url, timeout=1)
            return json.loads(res.fp.read())['length']
        except Exception as e:
            print(f'Could not read {url} error={e}')
            return 0

    urls_to_check = peer_urls()
    lengths = parallel(urls_to_check, get_chain_length, default=0)

    zipped = list(zip(urls_to_check, lengths))
    local_len = Chain.local_length()

    for url, length in zipped:
        print(f'{url} length={length}')
    print(f'{config.port} (self) length={local_len}')

    try:
        max_url, max_len = max(zipped, key=lambda x: x[1])
    except ValueError:
        print('Loading local chain.')
        return Chain.load()

    if local_len >= max_len:
        print('Loading local chain.')
        return Chain.load()
    else:
        print(f'Fetching chain from: {max_url}')
        res = urlopen(max_url + '/chain')
        chain = Chain.load(res.fp.read())
        chain.save()
        return chain


def broadcast_block(block):
    def post_block(data, headers, url):
        url += '/block'
        req = Request(url, data, headers)
        try:
            urlopen(req, timeout=1)
        except Exception:
            pass
        else:
            print(f'Posted block to: {url}')

    data = block.to_json().encode('utf8')
    headers = {'Content-Type': 'application/json'}

    parallel_nowait(peer_urls(), partial(post_block, data, headers))
