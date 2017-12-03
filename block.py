import hashlib
import json
import os

import config

from utils import int2bytes, timestamp_now


class Block(object):
    PREFIX_FIELD_MAP = (
        ('index', int2bytes),
        ('prev_hash', lambda x: b'' if x is None else bytes.fromhex(x)),
        ('data', lambda x: x.encode('utf8')),
        ('timestamp', lambda x: x.encode('ascii')),
    )

    def __init__(self, attrs):
        for k, v in attrs.items():
            setattr(self, k, v)

    @classmethod
    def from_index(cls, index, prev_hash=None):
        return cls(dict(
            index=index,
            prev_hash=prev_hash,
            data=cls.generate_data(index),
            timestamp=timestamp_now(),
        ))

    @classmethod
    def genesis_block(cls):
        block = cls.from_index(0)
        block.mine()
        return block

    @staticmethod
    def generate_data(index):
        return f'bloco número {index}, feito por #{config.port}'

    @property
    def prefix(self):
        try:
            return self._prefix
        except AttributeError:
            self._prefix = b''.join(
                cast(getattr(self, k)) for k, cast in self.PREFIX_FIELD_MAP
            )
            return self._prefix

    @property
    def dict(self):
        return {k: v for k, v in vars(self).items() if not k.startswith('_')}

    def header(self, nonce):
        return self.prefix + int2bytes(nonce)

    def mine(self):
        nonce = 0
        while True:
            self.update_hash(nonce)
            if self.passes_difficulty():
                break
            nonce += 1

    def mine_rounds(self, starting_nonce):
        for nonce in range(starting_nonce, starting_nonce + config.rounds):
            self.update_hash(nonce)
            if self.passes_difficulty():
                break

    def calc_hash(self, nonce):
        sha = hashlib.sha256(self.header(nonce))
        return sha.hexdigest()

    def update_hash(self, nonce):
        self.hash = self.calc_hash(nonce)
        self.nonce = nonce

    def is_valid(self):
        _hash = self.calc_hash(self.nonce)
        return _hash == self.hash and self.passes_difficulty()

    def passes_difficulty(self):
        return self.hash.startswith('0' * config.difficulty)

    def to_json(self):
        return json.dumps(self.dict)

    def save(self):
        number = str(self.index).zfill(6)
        full_path = os.path.join(config.data_dir, f'block_{number}.json')
        with open(full_path, 'w') as f:
            f.write(self.to_json())

    def __repr__(self):
        def stringify(v):
            return f"'{v}'" if isinstance(v, str) else v
        fields = ', '.join(f'{k}={stringify(v)}' for k, v in self.dict.items())
        return f'Block({fields})'
