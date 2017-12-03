from datetime import datetime

from queue import Empty, Full
from threading import Thread


def int2bytes(x):
    return b'' if x == 0 else int2bytes(x // 256) + bytes([x % 256])


def timestamp_now():
    return datetime.utcnow().strftime('%Y%m%d%H%M%S%f')


def read_file(filename):
    with open(filename, 'r') as f:
        return f.read()


def _thread_wrapper(fn, results, index, *args):
    results[index] = fn(*args)


def parallel(items, fn, default=None):
    results = [default] * len(items)
    threads = []

    for i, item in enumerate(items):
        t = Thread(target=_thread_wrapper, args=(fn, results, i, item))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return results


def parallel_nowait(items, fn):
    for item in items:
        Thread(target=fn, args=(item,)).start()


def get_messages(queue):
    messages = []
    while True:
        try:
            messages.append(queue.get_nowait())
        except Empty:
            return messages


def put_message(queue, message):
    try:
        queue.put_nowait(message)
    except Full:
        return False
    else:
        return True
