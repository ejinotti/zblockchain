import json
import os

import config

from block import Block
from utils import read_file


class Chain(object):
    def __init__(self, blocks):
        self.blocks = blocks

    @classmethod
    def load(cls, chain_json=None):
        if chain_json is None:
            chain_json = cls.local_json()
        blocks = [Block(attrs) for attrs in json.loads(chain_json)]
        return cls(blocks)

    @classmethod
    def local_json(cls):
        json_data = [
            read_file(os.path.join(config.data_dir, fn))
            for fn in cls.block_filenames()
        ]
        return '[' + ', '.join(json_data) + ']'

    @classmethod
    def local_length(cls):
        return len(cls.block_filenames())

    @staticmethod
    def block_filenames():
        return [
            fn for fn in os.listdir(config.data_dir) if fn.endswith('.json')
        ]

    def save(self):
        for block in self.blocks:
            block.save()

    def is_valid(self):
        return all(
            block.is_valid and block.hash == next_block.prev_hash
            for block, next_block
            in zip(self.blocks[:-1], self.blocks[1:]))

    def is_valid_next(self, block):
        last_block = self.blocks[-1]
        return (
            block.prev_hash == last_block.hash
            and
            block.index == last_block.index + 1
            and
            block.is_valid()
        )

    def generate_next_block(self):
        last_block = self.blocks[-1]
        return Block.from_index(last_block.index + 1, last_block.hash)

    def append(self, block):
        self.blocks.append(block)
        block.save()
