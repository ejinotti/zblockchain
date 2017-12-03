base_dir = 'chain'
base_url = 'http://localhost'

starting_port = 3000
node_urls = tuple(map(lambda x: f'{base_url}:{starting_port + x}', range(8)))

difficulty = 5
rounds = 100000
