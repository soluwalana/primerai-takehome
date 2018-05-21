"""Command line interface to interact with the project."""

from kafka import KafkaProducer

import os
import sys
import logging

LOG_FMT = '[%(name)+16.16s] %(levelname)-7s %(filename)+20.20s:%(lineno)-5d %(asctime)s %(message)s'
logging.basicConfig(
    datefmt='%Y-%m-%d %H:%M:%S',
    format=LOG_FMT,
    level=logging.DEBUG
)
logging.getLogger('kafka').setLevel(logging.INFO)
logging.getLogger('elasticsearch').setLevel(logging.WARNING)

KAFKA_HOSTS = ['localhost:9092']  # mapped to localhost by docker-compose
MB = 1024 * 1024


def process(kafka, path):
    """Read a file path line by line and put the data into the queue.

    This function will not do any processing beyond splitting
    the file on newlines.
    KafkaProducer is thread safe so we can emit each line to an executor
    passing the producer to the pool.
    """
    if os.path.isdir(path):
        # recursively find files
        for p in os.listdir(path):
            process(kafka, p)
        return

    logging.info('Processing file %s', path)

    futures = []
    with open(path, 'rb') as f:
        for line in f:
            futures.append(kafka.send('places', line))

    for future in futures:
        if future.failed():
            raise Exception('Unable to post kafka {}'.format(future.failed()))


def main():
    """Main entry point of the helper tool."""
    if len(sys.argv) < 2:
        logging.error('''Missing path(s) usage:
            python3 process.py /path/to/file1 /path/to/dirOrFile2
        ''')

    for p in sys.argv[1:]:
        if not os.path.exists(p):
            print('Path provided was not valid')
            return -1

        kafka = KafkaProducer(
            bootstrap_servers=KAFKA_HOSTS,
            buffer_memory=128 * MB,
            retries=2,
            client_id='process_producer',
        )
        process(kafka, p)

    return 0


if __name__ == '__main__':
    sys.exit(main())
