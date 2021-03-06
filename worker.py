from multiprocessing import Process, Queue

import config

from sync import broadcast_block
from utils import get_messages


class Worker(object):
    def __init__(self, chain, is_mining):
        self.chain = chain
        self.queue = Queue()
        self.process = Process(
            target=self._mining_loop if is_mining else self._listening_loop)

    def start(self):
        self.process.start()

    def terminate(self):
        self.process.terminate()
        self.queue.close()

    def _mining_loop(self):
        print('worker> mining loop..')
        found_valid_block = True

        while True:
            if found_valid_block:
                nonce = 0
                mining_block = self.chain.generate_next_block()
                print(f'worker> mining new block #{mining_block.index}')
            else:
                nonce += config.rounds

            mining_block.mine_rounds(nonce)

            remote_blocks = get_messages(self.queue)

            found_valid_block = False

            if remote_blocks:
                print(f'worker> received {len(remote_blocks)} block(s)')

            for blk in remote_blocks:
                if self.chain.is_valid_next(blk):
                    print(f'worker> saving valid remote block: {blk}')
                    found_valid_block = True
                    self.chain.append(blk)
                else:
                    print(f'worker> ignoring invalid remote block: {blk}')

            if found_valid_block:
                continue

            if mining_block.passes_difficulty():
                print(f'worker> successfully mined block: {mining_block}')
                self.chain.append(mining_block)
                broadcast_block(mining_block)
                found_valid_block = True

    def _listening_loop(self):
        print('worker> listening loop..')
        while True:
            block = self.queue.get()
            print(f'worker> got new block: {block}')
            if self.chain.is_valid_next(block):
                print('worker> saving valid block.')
                self.chain.append(block)
            else:
                print('worker> block not valid, ignoring.')
