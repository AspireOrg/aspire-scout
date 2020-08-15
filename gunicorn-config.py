import multiprocessing

bind = '0.0.0.0:8182'
# workers = (multiprocessing.cpu_count() * 2) + 1
worker_class = 'gevent'
worker_connections = 1000
loglevel = 'debug'
