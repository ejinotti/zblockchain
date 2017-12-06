### zblockchain

Zed's blockchain, inspired by
[jackschultz/jbc](https://github.com/jackschultz/jbc).

Wanted to do a few things differently:

1. Python 3 (written on 3.6.3)
2. No dependencies - standard libs only.
3. No linking directories.

#### Running a Node

`python main.py`

Options:

* `-g` create the genesis block.
* `-m` mine, if not given node will just listen.
* `-p PORT` port number to use (between 3000-3007). Uses 3000 if not given.

Blocks are stored under `/chain/<PORT>`.

#### Example Usage

From a fresh clone, in one terminal do:

```
python main.py -g -m
```

This starts the first node on 3000, creates the genesis block, and starts
mining.

In a second terminal do:

```
python main.py -p 3001
```

This starts another node on 3001 that syncs up the longest chain then just
listens for broadcast blocks.

In a third terminal do:

```
python main.py -p 3002 -m
```

This starts another node on 3002 that syncs up the longest chain then competes
for mining blocks.

Etc..
